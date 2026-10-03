# TZStudies security controls

This review covers the Flask website, templates, uploads and deployment files. The 19 categories come from page 29 of *SSA - 5 - Input Validation* (Howard, LeBlanc and Viega, 2005). The slides are reference material; obsolete examples such as PHP magic quotes are not implemented.

The controls follow current [Flask guidance](https://flask.palletsprojects.com/en/stable/web-security/), [OWASP authentication guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [password storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [recovery guidance](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html), and [upload guidance](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html).

## Coverage of all 19 categories

| Category | Protection in this application | Remaining scope / hosting responsibility |
| --- | --- | --- |
| Buffer overruns | Python-managed strings; 64 KB ordinary bodies, 12 MB multipart bodies, 32 KB fields, 24 form parts, 10 MB files; bounded document inspection. | Native libraries, Python and the OS need updates and resource limits. Python does not eliminate native memory bugs. |
| Format string problems | No user-controlled format programs or compiled templates. User content is data. | Preserve this boundary in new integrations. |
| Integer overflows | IDs restricted to positive signed 32-bit values; bounded reply IDs and input lengths. | Python integers do not wrap; native/database ranges still matter. |
| SQL injection | SQLAlchemy bound queries. Raw SQL is constant schema/health SQL plus a bound advisory-lock key. | Least-privilege database accounts; move schema changes entirely into a migration deployment step when retiring compatibility bootstrap. |
| Command injection | Request handlers do not launch shells, evaluate Python, or construct executable commands from user input. | Future document conversion/scanning belongs in isolated workers. |
| Failing to handle errors | Generic HTML/JSON failures, rollback, failed-upload cleanup, SMTP/AI timeouts, safe health errors, 503 on unavailable rate storage. | Restrict logs and monitor failures. |
| XSS | Jinja escaping, textContent for AI output, per-response script nonces, blocked inline event handlers, nosniff and same-origin frames. | Inline CSS remains allowed for existing layouts. Published library PDFs are reviewed content; uploads are never automatically published. |
| Unprotected network traffic | Production HTTPS redirect, rejection of HTTP form submissions, Secure/HttpOnly/SameSite cookies, HSTS, verified SMTP TLS and HTTPS AI requests. | Valid edge certificates and encrypted database/external Redis connections. |
| Magic URLs / hidden fields | Server-side admin/key authorization; submitted role fields ignored; CSRF on forms and JSON; random, hashed, expiring, one-use account tokens. | Keep tokens out of access logs and analytics. Knowing a URL grants no admin authority. |
| Improper TLS/SSL | Validating SMTP SSL context before authentication; fixed HTTPS API origin; forwarded host headers ignored. | Configure TLS 1.2/1.3 at the edge, exact proxy hops and an origin inaccessible to untrusted clients. |
| Weak passwords | New/reset passwords: 15-128 characters, small common/repeated-password blocklist, salted scrypt N=32768/r=8/p=3, login hash upgrades and IP/hashed-account rate limits. | The blocklist is not a comprehensive breach database. Existing short passwords work until reset. MFA is outside this change. |
| Insecure data storage | Password/token hashes; revocable login-token hashes; private randomly named CVs; owner-only Unix permissions; admin attachment downloads; sensitive no-store responses; private files excluded from Git/Docker. | Encrypted database/file volumes and backups, restricted service accounts and a CV retention policy. Signed session cookies are not encrypted; they contain an opaque token, no password/email. |
| Information leakage | Raw errors removed; canonical email links; consistent recovery messages; dummy password checks for unknown accounts. | Restrict logs and filter account-token URLs. Signup success still differs from unsuccessful registration. |
| Improper file access | Direct .pdf names inside resolved catalogue roots; traversal and escaping symlinks rejected; admin-only CV retrieval; exclusive file creation. | Keep application code and published papers read-only to the service user. Docker gives write access only to private runtime folders. |
| Trusting name resolution | No user-supplied outbound URL or DNS lookup; fixed API/SMTP hosts; HTTP host allowlist; TLS validates service identity. | Protect DNS/provider accounts. Verify database and Redis certificate hostnames; DNS alone is not identity proof. |
| Race conditions | Uniqueness/conflict handling; account-row serialization; conditional token consumption/password updates; O_EXCL uploads; PostgreSQL advisory lock or SQLite file lock for bootstrap. | Full PostgreSQL concurrency and multi-host testing require staging. SQLite locks coordinate only workers sharing a filesystem. |
| Unauthenticated key exchange | Certificate-verified TLS libraries, strong production signing secrets, no custom key-exchange protocol. | Valid edge certificates and a protected secret store. |
| Weak random numbers | Python secrets for 256-bit account/session tokens, upload names and CSP nonces; only token hashes persisted. | Generate SECRET_KEY with secrets.token_hex(32). |
| Poor usability | Passphrases/spaces/password managers, clear errors, existing-password compatibility, safe return URLs and responsive CSRF-protected logout. | Check mobile browsers and accessibility after future interface changes. |

## Before production deployment

1. Generate `SECRET_KEY` with `python -c "import secrets; print(secrets.token_hex(32))"` and store it in the host's secret manager. Production refuses missing/weak/obvious placeholder keys.
2. Set `PUBLIC_BASE_URL=https://mytzstudies.com` and `TRUSTED_HOSTS` to actual domains. Render's `RENDER_EXTERNAL_HOSTNAME` is added automatically. Do not allow arbitrary hosts.
3. Set `TRUSTED_PROXY_HOPS` to the exact count of trusted proxies (usually 1 for one managed edge), prevent direct origin access and confirm HTTPS redirects without loops. Default 0 ignores forged forwarded headers.
4. Configure required `REDIS_URL` on a private network or certificate-verified `rediss://`. Limits are shared across workers. Memory fallback and swallowed storage errors are disabled; unavailable rate storage returns 503.
5. Configure a valid edge certificate, TLS 1.2/1.3, and encrypted PostgreSQL/externally reachable Redis connections. PostgreSQL outside a trusted private network must verify its certificate, e.g. `sslmode=verify-full` with the correct CA certificate. Never disable verification.
6. Configure encrypted database/file volumes and backups, minimum privileges and CV retention. The app does not encrypt database or CV file bodies. Docker Compose is local development with demo database credentials and loopback ports.
7. Install `requirements.txt` and apply `flask db upgrade` through the established migration flow. The new migration adds `auth_token` and `login_session`. Compatibility startup creates missing new tables and serializes schema checks. Existing sessions and old signed verification/reset links need reauthentication or fresh links; accounts/passwords are retained.
8. Keep uploaded documents in review. Content checks are not an antivirus guarantee. Scan/disarm documents in a separate sandbox before staff open them or before publication. New uploads reject legacy .doc, encryption, macros, active PDF actions and embedded files. PDF and DOCX are accepted for CVs.
9. Do not log request bodies, cookies or account tokens. Filter `/verify/` and `/reset-password/` from access logs and keep logs private. Review admin/provider/database access periodically.

## Verification

```bash
python -m pytest tests/ -v --cov=tzstudies --cov-report=term-missing
ruff check tzstudies/ tests/ --ignore=E501
python -m pip_audit -r requirements.txt
python -m bandit -r tzstudies -ll
```

CI runs tests/lint plus dependency and static-security checks on pushes and pull requests. A clean audit reflects known advisories at that time; it does not prove absence of undiscovered vulnerabilities. `tools/check_website.cjs` covers signup/login/logout, filters, discussions, mobile layouts and all 60 exam/key pairs. Use an isolated preview database and suppress email.

Local verification uses Windows/Python 3.11; GitHub CI uses Linux/Python 3.13. Certificates, encryption at rest, actual Redis operation and PostgreSQL behavior still require staging checks. No production settings or external accounts were changed by this local update.
