"""PayPal Orders v2, OAuth and webhook postback verification. No buyer data retained."""

import hashlib
import json
import re
import threading
import time
import uuid
from urllib.parse import urlencode, urlsplit

import httpx


class GatewayError(Exception):
    """Safe error: never includes provider bodies, credentials or request URLs."""

    def __init__(self, code="unavailable"):
        self.code = code
        super().__init__("Payment provider request could not be completed.")


def provider_identifier(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Z0-9]{1,20}", value))


def binding(order):
    return hashlib.sha256(f"{order.id}|{order.user_id}|{order.plan_id}".encode()).hexdigest()


def request_id(order, operation):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"tzstudies:{operation}:{order.id}"))


def valid_checkout_url(value, mode):
    if not isinstance(value, str) or len(value) > 4096 or any(ord(c) < 33 for c in value):
        return False
    try:
        url = urlsplit(value)
        host = "www.sandbox.paypal.com" if mode == "sandbox" else "www.paypal.com"
        return (
            url.scheme == "https"
            and url.hostname == host
            and not url.username
            and not url.password
            and url.port in (None, 443)
            and not url.fragment
            and url.path in ("/checkoutnow", "/webapps/hermes")
        )
    except ValueError:
        return False


class PayPal:
    def __init__(self, config):
        self.config = config
        self.mode = config["PAYPAL_MODE"]
        if self.mode not in ("sandbox", "live"):
            raise RuntimeError("PAYPAL_MODE must be sandbox or live.")
        self.base = "https://api-m.sandbox.paypal.com" if self.mode == "sandbox" else "https://api-m.paypal.com"
        self._token, self._expires = None, 0
        self._lock = threading.Lock()

    def _request(self, method, path, headers, payload=None, auth=None, data=None, content=None):
        try:
            with httpx.stream(
                method,
                self.base + path,
                headers=headers,
                json=payload,
                auth=auth,
                data=data,
                content=content,
                timeout=httpx.Timeout(
                    self.config["PAYMENT_READ_TIMEOUT"], connect=self.config["PAYMENT_CONNECT_TIMEOUT"]
                ),
                follow_redirects=False,
                trust_env=False,
            ) as response:
                if response.status_code not in (200, 201):
                    raise GatewayError(
                        {401: "credentials", 403: "access", 404: "not_found", 422: "validation", 429: "rate_limit"}.get(
                            response.status_code, "unavailable"
                        )
                    )
                if "application/json" not in response.headers.get("content-type", "").lower():
                    raise GatewayError("invalid_response")
                content = bytearray()
                for chunk in response.iter_bytes():
                    content.extend(chunk)
                    if len(content) > 256 * 1024:
                        raise GatewayError("invalid_response")
                result = json.loads(content)
                if not isinstance(result, dict):
                    raise GatewayError("invalid_response")
                return result
        except GatewayError:
            raise
        except (httpx.HTTPError, ValueError, TypeError, RecursionError):
            raise GatewayError() from None

    def _authorization(self):
        if not all(self.config.get(k) for k in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET")):
            raise GatewayError("configuration")
        with self._lock:
            if self._token and time.monotonic() < self._expires:
                return self._token
            result = self._request(
                "POST",
                "/v1/oauth2/token",
                {"Accept": "application/json"},
                auth=httpx.BasicAuth(self.config["PAYPAL_CLIENT_ID"], self.config["PAYPAL_CLIENT_SECRET"]),
                data={"grant_type": "client_credentials"},
            )
            token, expires = result.get("access_token"), result.get("expires_in")
            if (
                result.get("token_type", "").lower() != "bearer"
                or not isinstance(token, str)
                or not 1 <= len(token) <= 8192
                or any(ord(c) < 33 for c in token)
                or type(expires) is not int
                or expires <= 0
            ):
                raise GatewayError("invalid_response")
            self._token = "Bearer " + token
            self._expires = time.monotonic() + max(1, min(expires - 30, self.config["PAYMENT_TOKEN_TTL"]))
            return self._token

    def _authorized_request(self, method, path, payload=None, idempotency=None, content=None):
        for attempt in range(2):
            headers = {
                "Authorization": self._authorization(),
                "Accept": "application/json",
                "Prefer": "return=representation",
            }
            if idempotency:
                headers["PayPal-Request-Id"] = idempotency
            if content is not None:
                headers["Content-Type"] = "application/json"
            try:
                return self._request(method, path, headers, payload, content=content)
            except GatewayError as error:
                if error.code != "credentials" or attempt:
                    raise
                with self._lock:
                    self._token = None
        raise GatewayError()

    def create_checkout(self, order):
        from tzstudies.payment_config import money_text

        price = {"currency_code": order.currency, "value": money_text(order.amount, order.currency)}
        unit = {
            "reference_id": order.id,
            "custom_id": binding(order),
            "invoice_id": order.order_reference,
            "amount": {**price, "breakdown": {"item_total": price}},
            "items": [
                {
                    "name": order.plan_name,
                    "sku": order.plan_id,
                    "quantity": "1",
                    "category": "DIGITAL_GOODS",
                    "unit_amount": price,
                }
            ],
        }
        context = {
            "brand_name": "TZStudies",
            "shipping_preference": "NO_SHIPPING",
            "user_action": "PAY_NOW",
            "return_url": self.config["PAYMENT_RETURN_URL"] + "?" + urlencode({"order": order.id}),
            "cancel_url": self.config["PAYMENT_RETURN_URL"] + "?" + urlencode({"order": order.id, "cancelled": "1"}),
        }
        return self._authorized_request(
            "POST",
            "/v2/checkout/orders",
            {
                "intent": "CAPTURE",
                "purchase_units": [unit],
                "payment_source": {"paypal": {"experience_context": context}},
            },
            request_id(order, "create"),
        )

    def get_order(self, identifier):
        if not provider_identifier(identifier):
            raise GatewayError("invalid_reference")
        return self._authorized_request("GET", "/v2/checkout/orders/" + identifier)

    def capture_order(self, order):
        if not provider_identifier(order.provider_id):
            raise GatewayError("invalid_reference")
        return self._authorized_request(
            "POST", "/v2/checkout/orders/" + order.provider_id + "/capture", {}, request_id(order, "capture")
        )

    def get_capture(self, identifier):
        if not provider_identifier(identifier):
            raise GatewayError("invalid_reference")
        return self._authorized_request("GET", "/v2/payments/captures/" + identifier)

    def get_refund(self, identifier):
        if not provider_identifier(identifier):
            raise GatewayError("invalid_reference")
        return self._authorized_request("GET", "/v2/payments/refunds/" + identifier)

    def verify_webhook(self, payload, headers, raw_body=None):
        if not self.config.get("PAYPAL_WEBHOOK_ID"):
            raise GatewayError("webhook_not_configured")
        fields = {
            "auth_algo": "PAYPAL-AUTH-ALGO",
            "cert_url": "PAYPAL-CERT-URL",
            "transmission_id": "PAYPAL-TRANSMISSION-ID",
            "transmission_sig": "PAYPAL-TRANSMISSION-SIG",
            "transmission_time": "PAYPAL-TRANSMISSION-TIME",
        }
        values = {key: headers.get(header, "") for key, header in fields.items()}
        if any(
            not isinstance(v, str) or not 1 <= len(v) <= 4096 or any(ord(c) < 32 for c in v) for v in values.values()
        ):
            return False
        try:
            cert = urlsplit(values["cert_url"])
            host = "api.sandbox.paypal.com" if self.mode == "sandbox" else "api.paypal.com"
            modern = "api-m.sandbox.paypal.com" if self.mode == "sandbox" else "api-m.paypal.com"
            if (
                cert.scheme != "https"
                or cert.hostname not in (host, modern)
                or cert.port not in (None, 443)
                or cert.username
                or cert.password
                or cert.query
                or cert.fragment
                or not cert.path.startswith("/v1/notifications/certs/")
            ):
                return False
        except ValueError:
            return False
        values["webhook_id"] = self.config["PAYPAL_WEBHOOK_ID"]
        if raw_body is None:
            raw_body = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode()
        # Preserve the signed event's original bytes, including whitespace/Unicode.
        content = json.dumps(values, separators=(",", ":")).encode()[:-1] + b',"webhook_event":' + raw_body + b"}"
        result = self._authorized_request("POST", "/v1/notifications/verify-webhook-signature", content=content)
        return result.get("verification_status") == "SUCCESS"
