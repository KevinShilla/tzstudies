"""Server-only payment configuration and the single source of plan metadata."""

import json
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit


def environment_settings():
    return {
        "CLICKPESA_CLIENT_ID": os.getenv("CLICKPESA_CLIENT_ID", ""),
        "CLICKPESA_API_KEY": os.getenv("CLICKPESA_API_KEY", ""),
        "CLICKPESA_CHECKSUM_KEY": os.getenv("CLICKPESA_CHECKSUM_KEY", ""),
        "CLICKPESA_API_BASE_URL": os.getenv("CLICKPESA_API_BASE_URL", "https://api.clickpesa.com/third-parties").rstrip("/"),
        "CLICKPESA_CHECKOUT_DOMAINS": tuple(filter(None, (v.strip() for v in os.getenv("CLICKPESA_CHECKOUT_DOMAINS", "clickpesa.com").split(",")))),
        "PAYMENT_RETURN_URL": os.getenv("PAYMENT_RETURN_URL", ""),
        "CLICKPESA_WEBHOOK_URL": os.getenv("CLICKPESA_WEBHOOK_URL", ""),
        "PAYMENT_CATALOG_FILE": os.getenv("PAYMENT_CATALOG_FILE", str(Path(__file__).resolve().parents[1] / "config/payment-plans.json")),
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


def load_catalog(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
        if len(raw) > 64 * 1024:
            raise ValueError
        catalog = json.loads(raw)
        if type(catalog["schema_version"]) is not int or catalog["schema_version"] != 1 or not isinstance(catalog["paid_features"], list) or not isinstance(catalog["plans"], dict):
            raise ValueError
        for key, plan in catalog["plans"].items():
            if not re.fullmatch(r"[a-z0-9_]{1,60}", key) or not isinstance(plan, dict):
                raise ValueError
            for field in ("name", "description"):
                if not isinstance(plan[field], str) or not 1 <= len(plan[field]) <= (100 if field == "name" else 500):
                    raise ValueError
            if amount(plan["price"]) <= 0 or plan["currency"] not in ("TZS", "USD"):
                raise ValueError
            for field in ("duration_days", "ai_allowance"):
                if type(plan[field]) is not int or not 0 <= plan[field] <= 1000000:
                    raise ValueError
            if not isinstance(plan["limits"], dict) or any(type(v) is not int or v < 0 for v in plan["limits"].values()):
                raise ValueError
            if any(type(plan[field]) is not bool for field in ("enabled", "admin_only")):
                raise ValueError
            if not isinstance(plan["features"], list) or any(not isinstance(v, str) for v in plan["features"]):
                raise ValueError
        if any(not isinstance(v, str) for v in catalog["paid_features"]):
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        raise RuntimeError("Invalid payment catalogue; check config/payment-plans.json.") from exc
    return catalog


def configure_payments(app, production=False):
    base = app.config["PUBLIC_BASE_URL"].rstrip("/")
    for key, path in (("PAYMENT_RETURN_URL", "/payments/return"), ("CLICKPESA_WEBHOOK_URL", "/payments/webhooks/clickpesa")):
        value = app.config.get(key) or base + path
        parsed = urlsplit(value)
        origin = urlsplit(base)
        if (parsed.scheme not in (("https",) if production else ("http", "https"))
                or parsed.netloc != origin.netloc or parsed.scheme != origin.scheme
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or not re.fullmatch(r"/payments/[a-zA-Z0-9/_-]+", parsed.path) or "//" in parsed.path):
            raise RuntimeError(f"{key} must be a payment URL on PUBLIC_BASE_URL.")
        app.config[key] = value
    if app.config["PAYMENT_RETURN_URL"] == app.config["CLICKPESA_WEBHOOK_URL"]:
        raise RuntimeError("Payment return and webhook URLs must be different.")
    api = urlsplit(app.config["CLICKPESA_API_BASE_URL"])
    if api.scheme != "https" or api.hostname != "api.clickpesa.com" or api.username or api.password or api.query or api.fragment or api.port not in (None, 443):
        raise RuntimeError("CLICKPESA_API_BASE_URL must use ClickPesa's HTTPS API.")
    domains = app.config["CLICKPESA_CHECKOUT_DOMAINS"]
    if not isinstance(domains, (list, tuple)) or not domains or any(not isinstance(domain, str) or not re.fullmatch(r"[a-z0-9]+(?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,63}", domain) for domain in domains):
        raise RuntimeError("CLICKPESA_CHECKOUT_DOMAINS requires explicit lowercase hostnames.")
    for key in ("CLICKPESA_CLIENT_ID", "CLICKPESA_API_KEY", "CLICKPESA_CHECKSUM_KEY"):
        value = app.config[key]
        if not isinstance(value, str) or len(value) > 500 or any(ord(char) < 32 for char in value):
            raise RuntimeError(f"Invalid {key} configuration.")
    if app.config["PAYMENTS_ENABLED"] and not all(app.config[key] for key in ("CLICKPESA_CLIENT_ID", "CLICKPESA_API_KEY")):
        raise RuntimeError("Enabled payments require CLICKPESA_CLIENT_ID and CLICKPESA_API_KEY.")
    catalog = load_catalog(app.config["PAYMENT_CATALOG_FILE"])
    test_plan = catalog["plans"].get("payment_test")
    if test_plan and (not test_plan["admin_only"] or test_plan["features"] or test_plan["ai_allowance"] or test_plan["duration_days"]):
        raise RuntimeError("The payment test must remain admin-only without premium grants.")
    if app.config["PAYMENT_TEST_PLAN_ENABLED"]:
        if not test_plan:
            raise RuntimeError("PAYMENT_TEST_PLAN_ENABLED requires a payment_test plan.")
        test_plan["enabled"] = True
    # No study route consults paid_features yet. Changing prices never changes existing orders.
    app.extensions["payment_catalog"] = catalog


def plan_available(plan, user):
    return bool(plan["enabled"] and (not plan["admin_only"] or user.is_admin))
