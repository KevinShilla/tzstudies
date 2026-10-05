# TZStudies payments: Render + Supabase

Implemented against the official ClickPesa documentation on 3 October 2026. This is a payment foundation: current study features remain available as before, and no subscription or premium entitlement is granted. The only initial product is an admin-only TZS 1,000 checkout test. Charging is disabled until you enable it.

## 1. Put credentials in Render, never in GitHub

The keys pasted in chat should be replaced before production use. Revoke/regenerate the ClickPesa API key under its application's **Manage API Keys**, and replace the OpenAI API key in your OpenAI project. Keep the Client ID belonging to that same ClickPesa application. Do not paste replacement values into chat or source files.

Open **Render Dashboard → your existing TZStudies web service → Environment → Edit**. Add the following keys, with their replacement/private values in Render's **Value** fields:

| Key | Value |
| --- | --- |
| `CLICKPESA_CLIENT_ID` | Your Hosted application's Client ID |
| `CLICKPESA_API_KEY` | Your new ClickPesa API key |
| `OPENAI_API_KEY` | Your new OpenAI project API key |
| `FLASK_ENV` | `production` |
| `PUBLIC_BASE_URL` | `https://mytzstudies.com` |
| `PAYMENT_RETURN_URL` | `https://mytzstudies.com/payments/return` |
| `CLICKPESA_WEBHOOK_URL` | `https://mytzstudies.com/payments/webhooks/clickpesa` |
| `PAYMENTS_ENABLED` | `false` during setup; `true` for your payment test |
| `PAYMENT_TEST_PLAN_ENABLED` | `false` during setup; `true` for your payment test |

Choose **Save, rebuild, and deploy** after the code has been deployed to your existing service. These changes have been implemented locally; they are not automatically uploaded to GitHub or deployed to Render.

Keep the existing `DATABASE_URL`, `SECRET_KEY`, and mail variables. `DATABASE_URL` must remain the server-side Supabase PostgreSQL connection string, using a database role permitted to create/manage tables and bypass their RLS (normally the existing `postgres` owner). Do not switch to a Supabase browser/anon API key. Keep SSL required in the Supabase connection string; a session-pooler connection is suitable when Render cannot reach the direct IPv6 database address.

The existing production security code also requires `REDIS_URL` for shared rate limits. It was not visible in your screenshot. If it is not supplied by an environment group, add your Render Key Value/private Redis connection. Set `TRUSTED_PROXY_HOPS=1` for Render's single trusted edge proxy, provided the origin is reachable only through that proxy. This allows HTTPS webhook requests forwarded by Render to be recognized correctly. Preserve a strong random `SECRET_KEY`; changing it signs users out.

For local development only, copy `.env.example` to the project-root `.env`, enter private values locally, and use `PUBLIC_BASE_URL=http://127.0.0.1:5000`, matching local payment URLs. Real dotenv files and their variants are excluded from Git and Docker. CI scans tracked text for recognizable credentials without printing them. These checks do not revoke a key already disclosed or remove it from old Git history.

## 2. Configure your ClickPesa Hosted application

Open [merchant.clickpesa.com](https://merchant.clickpesa.com) → **Settings → Developers → select the TZStudies application**.

1. Ensure **Integration Type: Hosted**, with **Hosted Checkout** enabled. Use credentials from this application.
2. Set its **Return URL** to `https://mytzstudies.com/payments/return`.
3. Open **Application Webhooks** (the application's webhook settings under Developers).
4. Enable **PAYMENT RECEIVED** and paste `https://mytzstudies.com/payments/webhooks/clickpesa` into that event's URL field.
5. Enable **PAYMENT FAILED** and paste the **same URL** into that event's URL field. Save both.

Use application webhooks for these checkout orders. No payout events are needed. The code does not set a separate `callbackUrl`, avoiding a duplicate success-only notification channel. ClickPesa's return URL is configured on the application; it is not a checkout request parameter. [Hosted setup](https://docs.clickpesa.com/application/hosted-application-setup), [webhook documentation](https://docs.clickpesa.com/home/webhooks).

### Optional checksum validation

Check **Settings → Developers → Encryption**. If checksum validation is enabled, add `CLICKPESA_CHECKSUM_KEY` to Render with that **separate encryption/checksum secret**, then redeploy. It is not your API key. Incoming notifications will require a valid canonical HMAC-SHA256 checksum, and checkout requests include a checksum. Restart/redeploy after changing checksum settings to discard cached tokens, as ClickPesa invalidates old tokens on a settings change.

With your three original credential types and no checksum key, leave ClickPesa checksum validation disabled. Unsigned notifications still cannot declare a payment successful: the server always calls the authenticated Query Payment API and validates the matching application, order, transaction, amount, currency and payment reference. Adding checksum validation provides notification authentication in addition to this confirmation. [Checksum documentation](https://docs.clickpesa.com/home/checksum).

## 3. What may still prevent real payments

No real API requests or charges were made during implementation, and your private ClickPesa dashboard was not inspected. Local tests cannot establish your account's actual activation or KYC status. Check:

- The implemented code is deployed, the three Render variables are present, and both payment flags are enabled for testing.
- API credentials are valid, unexpired, and belong to the Hosted application with checkout enabled.
- A collection method is enabled under **Settings → Collection** and your merchant account is permitted to collect payments.
- KYC and account limits permit the payment. ClickPesa currently has **no sandbox**: all API/Explorer transactions use real funds. Before approved KYC, the documented limits are TZS 100,000 combined transaction volume and 100 API calls/day; cards, TanQR and CRDB Direct Debit require approved KYC. [Testing limits](https://docs.clickpesa.com/home/sandbox-and-testing-environment).
- The configured Return URL and application webhook URLs are reachable over public HTTPS and match Render's deployed hostname.
- If Encryption is enabled, the matching checksum key is configured in Render.
- If IP whitelisting is enabled, Render's actual outbound addresses are permitted. Find them under **Render service → Connect → Outbound**. Render provides shared CIDR ranges; confirm ClickPesa accepts the relevant addresses/ranges rather than entering your website's DNS address. A fixed outbound IP may be needed if the account cannot accept Render's ranges. [Render outbound IPs](https://render.com/docs/outbound-ip-addresses).
- Production startup has the required Redis, database permissions and proxy configuration. `flask --app 'tzstudies:create_app("production")' payments-check` in a Render shell reports configuration presence without showing secrets or making API calls.

## 4. First small real payment

1. Deploy this code with payments paused. Set the replacement credentials and the URLs in Render; configure the ClickPesa application as above.
2. Set `PAYMENTS_ENABLED=true` and `PAYMENT_TEST_PLAN_ENABLED=true`, then save/redeploy. Sign in with your **existing single admin account**.
3. Open `https://mytzstudies.com/admin/payments` (also linked from Admin Dashboard). Confirm the readiness panel and the test amount, initially **TZS 1,000**.
4. Click **Continue to ClickPesa** once. Verify that ClickPesa displays the expected amount; provider/customer fees may apply. Complete one payment with an enabled method. Enter any PIN or card details only in the provider/telco's secure flow.
5. Return to TZStudies. It may say **Awaiting payment confirmation** first. Wait for **Payment confirmed**. A success-looking return URL alone is deliberately insufficient.
6. Compare the order reference, amount and ClickPesa payment reference in TZStudies with the successful transaction in ClickPesa. Confirm the webhook delivered successfully and that the same order still appears only once after a refresh.
7. If it remains pending, use **Check payment status** once. This queries ClickPesa; it cannot initiate another charge. Check webhook settings and Render logs for the generic verification warning. Do not repay while uncertain.
8. When finished, set `PAYMENT_TEST_PLAN_ENABLED=false` (and `PAYMENTS_ENABLED=false` if you want all new checkout paused), then save/redeploy. Existing orders and webhook confirmations remain available.

An administrator can recover a missed callback in a Render shell with `flask --app 'tzstudies:create_app("production")' payments-reconcile --order TZ…`, replacing `TZ…` with that order's alphanumeric reference. This queries the provider and never creates a checkout or charge. ClickPesa's docs do not promise a webhook retry schedule; use reconciliation if needed.

## 5. Change plans later in one place

Edit `config/payment-plans.json`, then redeploy. It contains each plan's `name`, `description`, `price` (decimal string), `currency`, `duration_days`, `limits`, `ai_allowance`, `enabled`, `admin_only` and `features`. The top-level `paid_features` list is a reserved configuration point. No existing feature reads that list or becomes paid in this implementation. Future entitlement enforcement should be attached to the same catalogue rather than duplicating prices/limits in routes.

`PAYMENT_TEST_PLAN_ENABLED=true` enables only the protected test plan. Regular plans must be explicitly added/enabled in the catalogue. Each order saves a price and plan snapshot; catalogue edits affect new orders only. `PAYMENT_CATALOG_FILE` optionally selects another catalogue file. `CLICKPESA_API_BASE_URL` and `CLICKPESA_CHECKOUT_DOMAINS` centralize the provider URLs, with HTTPS and hostname validation.

## 6. Storage, trust boundaries and verification

Two tables are added to the existing SQLAlchemy database: `payment_order` and `payment_webhook_event`. An Alembic revision is included; the existing compatibility startup creates missing tables too. Both tables enable RLS and revoke access for PUBLIC, `anon` and `authenticated` on PostgreSQL/Supabase. Your current admin flag and authentication are reused; no account or auth system is added.

Orders retain internal and provider transaction IDs, order/payment references, existing user ID, amount/currency, status, immutable plan snapshot and created/completed/check times. A checkout URL is retained only while needed and cleared on confirmed payment/refund/reversal. Webhook receipts retain only event/transaction/order IDs and timestamps. Raw provider payloads, payer profiles, phone numbers, PINs, CVVs and card credentials are not retained or logged.

The return handler and background status polling only read the database. Webhooks and the explicit check/reconcile actions use the authenticated provider query. Successful amounts/currency/application/references must match the stored order. A transaction row lock and unique transaction/reference/event constraints protect concurrent callbacks and replays. Completion occurs once; failed or successful replays cannot undo a refund/reversal. Unknown checkout outcomes are preserved without automatic checkout retries.

Existing AI requests still use `OPENAI_API_KEY` only in the server-side OpenAI client; the AI model and study experience are unchanged. No payment/OpenAI secret is inserted into HTML, JavaScript or a public API. Checkout POSTs and manual checks require authentication and CSRF; only the dedicated provider webhook is CSRF-exempt and it cannot trust its payload alone.

Run `python -m pytest tests/`, `ruff check tzstudies/ tests/ --ignore E501`, `python tools/check_secrets.py`, and the optional disposable PostgreSQL check in `tools/check_payments_postgres.py`. Browser review outputs are kept locally under ignored `tmp/payments-review/`. Automated mocks never move real funds and do not verify live account eligibility.

Additional sources: [Checkout API](https://docs.clickpesa.com/api-reference/collection/generate-checkout-link/generate-checkout-link), [Render environment variables](https://render.com/docs/configure-environment-variables), [Supabase PostgreSQL connections](https://supabase.com/docs/guides/database/connecting-to-postgres), [OpenAI API authentication](https://developers.openai.com/api/reference/overview).
