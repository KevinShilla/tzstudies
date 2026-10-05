"""ClickPesa's documented token, Hosted Checkout and authoritative query APIs."""

import hashlib
import hmac
import json
import re
import threading
import time
from urllib.parse import urlsplit

import httpx


class GatewayError(Exception):
    """Contains no provider response body, URL, token or secret."""

    def __init__(self, code="unavailable"):
        self.code = code
        super().__init__("Payment provider request could not be completed.")


def checksum(payload, key, ascii_only=False):
    content = {k: v for k, v in payload.items() if k not in ("checksum", "checksumMethod")}
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=ascii_only, allow_nan=False).encode("utf-8")
    return hmac.new(key.encode("utf-8"), encoded, hashlib.sha256).hexdigest()


def verify_checksum(payload, key):
    signature = payload.get("checksum")
    if payload.get("checksumMethod", "canonical") != "canonical" or not isinstance(signature, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", signature):
        return False
    try:
        # The official JavaScript and Python examples differ in Unicode escaping.
        # Both canonical serializers require the same secret and untampered content.
        return any(hmac.compare_digest(signature.lower(), checksum(payload, key, mode)) for mode in (False, True))
    except (ValueError, TypeError, RecursionError):
        return False


def valid_checkout_url(value, domains):
    if not isinstance(value, str) or len(value) > 4096 or any(ord(c) < 33 for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return bool(parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password
                    and parsed.port in (None, 443) and not parsed.fragment
                    and any(parsed.hostname == domain or parsed.hostname.endswith("." + domain) for domain in domains))
    except ValueError:
        return False


class ClickPesa:
    def __init__(self, config):
        self.config = config
        self._token = None
        self._expires = 0
        self._lock = threading.Lock()

    def _request(self, method, path, headers, payload=None):
        timeout = httpx.Timeout(self.config["PAYMENT_READ_TIMEOUT"], connect=self.config["PAYMENT_CONNECT_TIMEOUT"])
        try:
            # Certificate verification is on. No proxy overrides, redirects or POST retries.
            with httpx.stream(method, self.config["CLICKPESA_API_BASE_URL"] + path, headers=headers,
                              json=payload, timeout=timeout, follow_redirects=False, trust_env=False) as response:
                if response.status_code != 200:
                    codes = {400: "configuration", 401: "credentials", 403: "access", 404: "not_found", 409: "reference_exists", 429: "rate_limit"}
                    raise GatewayError(codes.get(response.status_code, "unavailable"))
                if "application/json" not in response.headers.get("content-type", "").lower():
                    raise GatewayError("invalid_response")
                content = bytearray()
                for chunk in response.iter_bytes():
                    content.extend(chunk)
                    if len(content) > 128 * 1024:
                        raise GatewayError("invalid_response")
                return json.loads(content)
        except GatewayError:
            raise
        except (httpx.HTTPError, ValueError, TypeError, RecursionError):
            raise GatewayError() from None

    def _authorization(self):
        if not all(self.config.get(key) for key in ("CLICKPESA_CLIENT_ID", "CLICKPESA_API_KEY")):
            raise GatewayError("configuration")
        with self._lock:
            if self._token and time.monotonic() < self._expires:
                return self._token
            response = self._request("POST", "/generate-token", {
                "client-id": self.config["CLICKPESA_CLIENT_ID"],
                "api-key": self.config["CLICKPESA_API_KEY"],
                "Accept": "application/json",
            })
            token = response.get("token") if isinstance(response, dict) else None
            if not isinstance(response, dict) or response.get("success") is not True or not isinstance(token, str) or not 1 <= len(token) <= 8192 or any(ord(c) < 32 for c in token):
                raise GatewayError("invalid_response")
            self._token = token if token.startswith("Bearer ") else "Bearer " + token
            self._expires = time.monotonic() + self.config["PAYMENT_TOKEN_TTL"]
            return self._token

    def _authorized_request(self, method, path, payload=None):
        for attempt in range(2):
            try:
                return self._request(method, path, {"Authorization": self._authorization(), "Accept": "application/json"}, payload)
            except GatewayError as error:
                if error.code != "credentials" or attempt:
                    raise
                with self._lock:
                    self._token = None
        raise GatewayError()

    def create_checkout(self, order):
        payload = {
            "totalPrice": format(order.amount, ".2f"), "orderReference": order.order_reference,
            "orderCurrency": order.currency, "description": order.plan_name,
        }
        # Application webhooks are configured in the dashboard. callbackUrl is a
        # separate success-only callback and is deliberately not used here.
        if self.config["CLICKPESA_CHECKSUM_KEY"]:
            payload["checksum"] = checksum(payload, self.config["CLICKPESA_CHECKSUM_KEY"])
        response = self._authorized_request("POST", "/checkout-link/generate-checkout-url", payload)
        if (not isinstance(response, dict) or response.get("clientId") != self.config["CLICKPESA_CLIENT_ID"]
                or not valid_checkout_url(response.get("checkoutLink"), self.config["CLICKPESA_CHECKOUT_DOMAINS"])):
            raise GatewayError("invalid_response")
        return response["checkoutLink"]

    def query_payment(self, reference):
        if not re.fullmatch(r"[a-zA-Z0-9]{1,40}", reference):
            raise GatewayError("invalid_reference")
        result = self._authorized_request("GET", "/payments/" + reference)
        if not isinstance(result, list) or len(result) > 100 or any(not isinstance(item, dict) for item in result):
            raise GatewayError("invalid_response")
        return result
