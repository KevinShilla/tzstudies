# TZStudies analytics

Open `/admin/analytics` after logging in with the existing `is_admin` account. No new administrator is created or promoted. Both the dashboard and `/admin/analytics/data` use the existing server-side admin guard and private, non-cacheable responses.

## Tracking and privacy

The small deferred first-party script records public HTML pages after loading. PDF iframes, static assets, health checks, errors, account-reset links, administrator browsing, known bots, DNT, GPC and opted-out browsers are excluded. `/privacy` offers an opt-out without affecting accounts. There is no external analytics provider, API key or new runtime dependency.

Random signed HttpOnly cookies identify anonymous browsers; only hashes are stored. The visitor cookie lasts 90 days after the latest navigation. A visit uses a rolling 30-minute activity window. Signed page tickets bind collection to the browser and server-approved path. Collection requires CSRF, checks origins, limits request/batch size and rejects arbitrary event names and labels. Back/forward-cache restorations produce distinct, idempotent views.

Timing is cumulative, sent on a 30-second heartbeat, visibility changes, pagehide and before normal link navigation using asynchronous fetch or small FormData beacons. Hidden tabs do not accumulate time. Updates take the maximum value; sequence numbers prevent delayed heartbeats reopening ended pages. No unload handler or blocking navigation is used. Moving from signup to another tracked page also records abandonment on the server when no signup was completed, covering missed exit events. Analytics writes have their own SQLAlchemy session, so a failure cannot roll back signup or break browsing. Only successful server authentication records signup/login completion.

Analytics never stores account IDs, names, emails, IPs, passwords, search words, messages, form contents, referrer paths or URL queries. Referrers keep a public hostname only; campaign labels use a fixed allowlist. Account information remains separate.

## Report definitions

- **Visitors:** distinct anonymous browsers with a view during the period. Clearing cookies or changing devices can create another visitor. **Visits:** distinct browsing sessions. **Views:** rendered public pages, including reloads and restored pages.
- **New / returning:** first seen inside / before the selected period, mutually exclusive for each browser in that report.
- **Signups:** non-admin account creation dates, including existing accounts. **Tracked signups:** server-confirmed conversions with an anonymous visit. Historical, opted-out or unrecorded signups are marked unattributed; earlier visitor history is never fabricated.
- **Conversion:** distinct recorded visitors completing signup in the period ÷ recorded visitors in that period. Historical account totals are not used as the numerator.
- **Attribution:** initial external source in the visit and latest public/study page before signup. Source counts can overlap when a visitor uses different sources across visits. Direct includes unavailable referrers.
- **Entries:** sessions starting in the period. **Exits:** a session's latest page, when ended or inactive for 30 minutes. Continued browsing can change provisional exits; missing mobile beacons settle after inactivity.
- **Page time:** visible active seconds ÷ measured views, capped at four hours per page and elapsed wall time. Zero measured time is valid; unmeasured time shows a dash.
- **Engagement:** two views in a visit or at least 10 measured active seconds. **Abandonment:** a started signup visit with a leave event or inactivity and no subsequent completion in that visit.
- **Funnel:** ordered visitor → study page → start → completion in one visit and the chosen period. Direct signups also count in signup/conversion totals.
- **Journeys:** first 12 pages from up to 500 recent visits. Transition aggregates cover the whole period. Individual browser/session IDs are not exposed.

Dates use Tanzania time (UTC+3). Weeks start Monday; presets include the current partial day. Comparison uses the preceding equal number of calendar days. Conversion/engagement changes use percentage points. All time has no comparison. Longer ranges use monthly unique visitors rather than summed daily uniques.

Application PostgreSQL connections explicitly use UTC, preserving other connection options, so account creation timestamps and date filters stay consistent even if the database host's default timezone differs.

## Database and operation

Compatibility bootstrap creates four indexed tables. Alembic revision `a43809df725c` also creates them and tolerates prior bootstrap creation. Both enable PostgreSQL row-level security and revoke client grants on analytics and the existing private `user`, `auth_token`, and `login_session` tables. This protects the admin flag and authentication data from direct Supabase public API access. Server-owner/service-role privileges are preserved; use the existing privileged server database connection. No keys are sent to browsers and no account's admin flag is changed. These private account protections survive a migration downgrade. This follows [Supabase's RLS and grant guidance](https://supabase.com/docs/guides/database/postgres/row-level-security).

`ANALYTICS_ENABLED=false` disables collection while leaving private reports available. No local preview writes automatically reach production.

For retention, run `python -m flask --app app analytics-prune --days 365` during server maintenance (minimum 30 days). This removes old anonymous sessions/events and orphan visitors, leaving accounts untouched. This is an explicit command, not an automatic scheduler. All-time traffic reports refer to retained records.

Aggregates run in SQL; detail queries are bounded. The dashboard refreshes every 60 seconds while visible and supports manual refresh. Collection is separate from reporting.

## Verification

`python -m pytest tests` checks accuracy, source sanitisation, signup attribution and failure, abandonment, login, idempotency, timing order, entries/exits/journeys, privacy, CSRF, forged tickets, admin access, date boundaries, comparisons, migrations, RLS and account-safe failure/retention. `tools/check_analytics.cjs` exercises real navigation, signup, login, all dashboard filters and desktop/mobile layouts using `tools/serve_analytics_review.py` and an isolated local database.

Validation passed with 177 tests on both SQLite and PostgreSQL 17. The browser journey recorded exactly 19 public HTML views across five visitors, one signup, one abandonment, five sources, and five entries/exits. Mobile/tablet widths 320, 390 and 768 pixels had no horizontal overflow or JavaScript errors. `tools/check_analytics_postgres.py` additionally verified 56 denied public-role operations across seven protected tables, preserved server/service-role reads and a single existing fixture admin, and exercised real PostgreSQL tracking, attribution, date reporting and the ordered funnel. All review accounts/data were isolated; the production database was not accessed.
