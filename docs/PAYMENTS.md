# TZStudies payments — PayPal Orders v2

This replaces the active ClickPesa integration while preserving internal orders, Supabase, Redis limits, authentication, CSRF and existing study access. No premium restrictions or subscriptions are introduced. The initial product is an admin-only **USD 1.00 Sandbox test**, using fake money.

## Render configuration

Set values only in **Render → tzstudies → Environment**. Never commit actual credentials. `.env` and all `.env.*` files except `.env.example` are ignored.

| Setting | Initial value / purpose |
| --- | --- |
| PAYPAL_CLIENT_ID | Existing Sandbox application's Client ID |
| PAYPAL_CLIENT_SECRET | Same application's secret; server only |
| PAYPAL_MODE | `sandbox` |
| PAYPAL_WEBHOOK_ID | Optional at startup; add after registering the deployed webhook |
| PAYMENTS_ENABLED | `false` during deployment |
| PAYMENT_TEST_PLAN_ENABLED | `false` during deployment |
| PUBLIC_BASE_URL | `https://mytzstudies.com` |
| PAYMENT_RETURN_URL | `https://mytzstudies.com/payments/return` |
| PAYPAL_WEBHOOK_URL | `https://mytzstudies.com/payments/webhooks/paypal` (also the default) |

Keep DATABASE_URL, REDIS_URL, SECRET_KEY, OPENAI_API_KEY, mail settings and TRUSTED_PROXY_HOPS unchanged. PayPal endpoints are pinned by mode: `api-m.sandbox.paypal.com` or `api-m.paypal.com`; arbitrary API hosts are not accepted. Webhooks **fail closed** until PAYPAL_WEBHOOK_ID exists. Capture confirmation does not depend on delivery of a webhook.

## WHAT KEVIN DOES NEXT

1. Open [PayPal Developer Apps & Credentials](https://developer.paypal.com/dashboard/applications/sandbox). Select **Sandbox**, then the application whose credentials are in Render.
2. In that application's **Sandbox Webhooks** section choose **Add Webhook**. Paste `https://mytzstudies.com/payments/webhooks/paypal` as the URL.
3. Select exactly: `PAYMENT.CAPTURE.COMPLETED`, `PAYMENT.CAPTURE.PENDING`, `PAYMENT.CAPTURE.DECLINED`, `PAYMENT.CAPTURE.REFUNDED`, `PAYMENT.CAPTURE.REVERSED`. Save. `CHECKOUT.ORDER.APPROVED` is unnecessary: the protected return flow captures approved orders server-side.
4. Copy the resulting webhook's **Webhook ID** from that application's webhook list/details. This is not the Client ID.
5. Add it to Render Environment as `PAYPAL_WEBHOOK_ID`, save and redeploy.
6. In PayPal Developer → **Testing Tools → Sandbox Accounts**, use or create a **Personal** buyer account. Open its details to see its Sandbox login credentials. Use this account inside the Sandbox checkout, not your real PayPal account or the merchant Business account. Sandbox accounts and balances use fake money.
7. After `/admin/payments` shows Sandbox credentials and webhook verification configured, set `PAYMENTS_ENABLED=true` and `PAYMENT_TEST_PLAN_ENABLED=true` in Render; keep `PAYPAL_MODE=sandbox`. Save and redeploy.
8. Sign in to TZStudies as your admin. Open `/admin/payments`; click **Pay with PayPal · USD 1.00** once. Check that the URL is on `www.sandbox.paypal.com` and the price is USD 1.00. Approve with the Personal Sandbox buyer. Return to TZStudies; it submits a CSRF-protected server capture request.
9. Success is **Payment confirmed**, a USD 1.00 order with PayPal order/capture IDs and confirmation time. The Sandbox merchant's transaction history should show the matching completed capture, and the application's webhook event delivery should succeed. No study access changes. If pending, check this existing order; do not create another one while the outcome is unclear.
10. After the one test, set both payment flags back to false and redeploy.
11. Remove obsolete Render variables if present: `CLICKPESA_CLIENT_ID`, `CLICKPESA_API_KEY`, `CLICKPESA_CHECKSUM_KEY`, `CLICKPESA_WEBHOOK_URL`, `CLICKPESA_API_BASE_URL`, `CLICKPESA_CHECKOUT_DOMAINS`. Existing legacy rows stay archived and cannot be captured/reconciled through PayPal.
12. **Later, for Live:** first confirm your PayPal merchant account/country can receive payments and meets account requirements. Keep payments paused, create a Live application and Live webhook with the same events, replace Client ID/Secret/Webhook ID with Live values in Render, and set PAYPAL_MODE=live. Keep PAYMENT_TEST_PLAN_ENABLED=false: the fake $1 test is blocked in Live. Explicitly configure and enable real plans/prices in the catalogue only after Live readiness review. Sandbox records cannot be charged in Live.

## Catalogue and currency

`config/payment-plans.json` centralizes plan names, prices, currency, duration, limits, AI allowances, enabled/admin-only flags, features and future paid_features. Each order saves a snapshot: changes affect only new orders. Sandbox cannot enable public plans.

PayPal's current supported-currency list does **not** include TZS. `legacy_payment_test` retains TZS 1000 as disabled information. To use a future TZS-priced plan with PayPal, deliberately choose a supported currency and set its actual price in the catalogue; there is no automatic conversion. The validator rejects enabled unsupported currencies and fractional amounts for JPY/HUF/TWD.

## Financial and security boundaries

An internal order is committed before the server creates a PayPal CAPTURE order. The documented Orders v2 payer-action redirect keeps approval on PayPal without relaxing the site's CSP. The return URL never marks success; it sends a protected POST that retrieves the stored PayPal order, validates ownership and immutable item/amount/currency references, and captures on the server only if approved. Only a COMPLETED capture marks paid.

Order ID is stored as provider_id; capture ID as payment_reference. Provider, mode, expected user/plan snapshot, amount/currency, created/completed/refunded timestamps and capture attempt time are retained. Buyer email, payment instruments and raw provider payloads are not persisted. Database unique constraints and row locks prevent duplicate processing; create and capture have distinct stable PayPal-Request-Id values. Uncertain captures are queried before retry, with a conservative five-hour retry boundary. Missed captures are reconciled by read-only queries, never new charges.

Only the webhook route is CSRF-exempt. It verifies signatures through PayPal's official verify-webhook-signature endpoint using the registered Webhook ID and the original event bytes, then queries order/capture/refund resources to validate financial facts. Duplicate event receipts are unique. Refunds/reversals cannot be resurrected by older completed events. Partial refunds are distinct. PayPal simulator events cannot be verified using this postback method; use the actual fake Sandbox purchase to test deliveries.

The additive migration and serialized startup schema check preserve historical orders; old rows are labelled with their original provider. Supabase anonymous/authenticated browser roles still cannot access payment tables.

## Validation and operations

Run `python -m pytest tests/test_payments.py` and `python tools/check_payments_postgres.py` against the guarded disposable local cluster. `tools/serve_payments_review.py` runs a loopback-only isolated UI with a mock provider; never run it in production. Browser review uses the computer-use tool.

Production read-only readiness: `flask --app 'tzstudies:create_app("production")' payments-check`. It reports booleans/presence only, checks DB and rate-limit storage, and makes no PayPal requests. Read-only recovery: `flask --app 'tzstudies:create_app("production")' payments-reconcile --order TZ...`. Do not print environment variables, provider payloads, connection strings or access tokens in logs.

Official references: [Standard Checkout](https://developer.paypal.com/studio/checkout/standard/integrate), [Orders redirect flow](https://developer.paypal.com/whats-an-order/), [idempotency](https://developer.paypal.com/api/rest/reference/idempotency/), [currencies](https://developer.paypal.com/api/codes/currency), [webhook verification](https://developer.paypal.com/api/rest/webhooks/rest/), [event names](https://developer.paypal.com/api/rest/webhooks/event-names/), [Sandbox accounts](https://developer.paypal.com/sandbox-testing/accounts).
