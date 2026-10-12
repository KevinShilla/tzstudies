"""Server-only payment configuration and the single source of plan metadata."""

import json
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit

PAYPAL_CURRENCIES = frozenset(
    "AUD BRL CAD CNY CZK DKK EUR HKD HUF ILS JPY MYR MXN TWD NZD NOK PHP PLN GBP RUB SGD SEK CHF THB USD".split()
)
ZERO_DECIMAL_CURRENCIES = frozenset(("HUF", "JPY", "TWD"))


def environment_settings():
    return {
        "PAYPAL_CLIENT_ID": os.getenv("PAYPAL_CLIENT_ID", ""),
        "PAYPAL_CLIENT_SECRET": os.getenv("PAYPAL_CLIENT_SECRET", ""),
        "PAYPAL_MODE": os.getenv("PAYPAL_MODE", "sandbox").lower(),
        "PAYPAL_WEBHOOK_ID": os.getenv("PAYPAL_WEBHOOK_ID", ""),
        "PAYMENT_RETURN_URL": os.getenv("PAYMENT_RETURN_URL", ""),
        "PAYPAL_WEBHOOK_URL": os.getenv("PAYPAL_WEBHOOK_URL", ""),
        "PAYMENT_CATALOG_FILE": os.getenv(
            "PAYMENT_CATALOG_FILE", str(Path(__file__).resolve().parents[1] / "config/payment-plans.json")
        ),
        "PAYMENTS_ENABLED": os.getenv("PAYMENTS_ENABLED", "false").lower() == "true",
        "PAYMENT_TEST_PLAN_ENABLED": os.getenv("PAYMENT_TEST_PLAN_ENABLED", "false").lower() == "true",
        "PAYMENT_CONNECT_TIMEOUT": 5,
        "PAYMENT_READ_TIMEOUT": 10,
        "PAYMENT_TOKEN_TTL": 3300,
        "PAYMENT_INTENT_TTL": 3600,
    }


def amount(value):
    """Decimal money only; never accept NaN, exponent notation, bools or fractional cents."""
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("Invalid amount")
    text = str(value)
    if not re.fullmatch(r"\d{1,12}(?:\.\d{1,2})?", text):
        raise ValueError("Invalid amount")
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc


def money_text(value, currency):
    value = amount(value)
    if currency not in PAYPAL_CURRENCIES or currency in ZERO_DECIMAL_CURRENCIES and value != value.to_integral_value():
        raise ValueError("Unsupported currency or precision")
    return format(value, ".0f" if currency in ZERO_DECIMAL_CURRENCIES else ".2f")


def load_catalog(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
        if len(raw) > 64 * 1024:
            raise ValueError
        catalog = json.loads(raw)
        if (
            type(catalog["schema_version"]) is not int
            or catalog["schema_version"] != 1
            or not isinstance(catalog["paid_features"], list)
            or not isinstance(catalog["plans"], dict)
        ):
            raise ValueError
        for key, plan in catalog["plans"].items():
            if not re.fullmatch(r"[a-z0-9_]{1,60}", key) or not isinstance(plan, dict):
                raise ValueError
            for field in ("name", "description"):
                if not isinstance(plan[field], str) or not 1 <= len(plan[field]) <= (100 if field == "name" else 500):
                    raise ValueError
            if amount(plan["price"]) <= 0 or plan["currency"] not in PAYPAL_CURRENCIES | {"TZS"}:
                raise ValueError
            for field in ("duration_days", "ai_allowance"):
                if type(plan[field]) is not int or not 0 <= plan[field] <= 1000000:
                    raise ValueError
            if not isinstance(plan["limits"], dict) or any(
                type(v) is not int or v < 0 for v in plan["limits"].values()
            ):
                raise ValueError
            if any(type(plan[field]) is not bool for field in ("enabled", "admin_only")):
                raise ValueError
            if not isinstance(plan["features"], list) or any(not isinstance(v, str) for v in plan["features"]):
                raise ValueError
            if plan["enabled"]:
                money_text(plan["price"], plan["currency"])
        if any(not isinstance(v, str) for v in catalog["paid_features"]):
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        raise RuntimeError("Invalid payment catalogue; check config/payment-plans.json.") from exc
    return catalog


def configure_payments(app, production=False):
    base = app.config["PUBLIC_BASE_URL"].rstrip("/")
    for key, path in (("PAYMENT_RETURN_URL", "/payments/return"), ("PAYPAL_WEBHOOK_URL", "/payments/webhooks/paypal")):
        value = app.config.get(key) or base + path
        parsed = urlsplit(value)
        origin = urlsplit(base)
        if (
            parsed.scheme not in (("https",) if production else ("http", "https"))
            or parsed.netloc != origin.netloc
            or parsed.scheme != origin.scheme
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or not re.fullmatch(r"/payments/[a-zA-Z0-9/_-]+", parsed.path)
            or "//" in parsed.path
        ):
            raise RuntimeError(f"{key} must be a payment URL on PUBLIC_BASE_URL.")
        app.config[key] = value
    if app.config["PAYMENT_RETURN_URL"] == app.config["PAYPAL_WEBHOOK_URL"]:
        raise RuntimeError("Payment return and webhook URLs must be different.")
    if app.config["PAYPAL_MODE"] not in ("sandbox", "live"):
        raise RuntimeError("PAYPAL_MODE must be sandbox or live.")
    for key in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET", "PAYPAL_WEBHOOK_ID"):
        value = app.config[key]
        if not isinstance(value, str) or len(value) > 500 or any(ord(char) < 32 for char in value):
            raise RuntimeError(f"Invalid {key} configuration.")
    if app.config["PAYMENTS_ENABLED"] and not all(
        app.config[key] for key in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET")
    ):
        raise RuntimeError("Enabled payments require PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET.")
    catalog = load_catalog(app.config["PAYMENT_CATALOG_FILE"])
    test_plan = catalog["plans"].get("payment_test")
    if test_plan and (
        not test_plan["admin_only"] or test_plan["features"] or test_plan["ai_allowance"] or test_plan["duration_days"]
    ):
        raise RuntimeError("The payment test must remain admin-only without premium grants.")
    if app.config["PAYMENT_TEST_PLAN_ENABLED"]:
        if (
            not test_plan
            or app.config["PAYPAL_MODE"] != "sandbox"
            or test_plan["currency"] != "USD"
            or amount(test_plan["price"]) != 1
        ):
            raise RuntimeError("The private USD 1.00 test is restricted to PayPal Sandbox.")
        test_plan["enabled"] = True
    elif test_plan:
        test_plan["enabled"] = False
    if app.config["PAYPAL_MODE"] == "sandbox" and any(
        p["enabled"] and not p["admin_only"] for p in catalog["plans"].values()
    ):
        raise RuntimeError("Sandbox plans must remain admin-only.")
    # No study route consults paid_features yet. Changing prices never changes existing orders.
    app.extensions["payment_catalog"] = catalog


def plan_available(plan, user):
    return bool(plan["enabled"] and plan["currency"] in PAYPAL_CURRENCIES and (not plan["admin_only"] or user.is_admin))
