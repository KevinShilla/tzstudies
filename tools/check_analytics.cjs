/* Real browser regression check. Run against tools/serve_analytics_review.py --reset. */
const { chromium } = require((process.env.TZ_NODE_MODULES || 'C:/Users/Kevin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules') + '/playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const base = 'http://127.0.0.1:5051';
const output = path.resolve('output/analytics');
fs.mkdirSync(output, { recursive: true });
const password = 'River stones remember sunrise!';
const ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36';
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  const errors = [], tickets = new Set(), reads = [], collects = [];
  const contexts = [];
  async function visitor() {
    const context = await browser.newContext({ userAgent: ua, viewport: { width: 1440, height: 1000 } });
    contexts.push(context);
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => {
      if (response.url().includes('/analytics/collect')) collects.push(response.status());
      if (response.request().isNavigationRequest() && response.request().frame() === page.mainFrame() && response.status() === 200) {
        reads.push(response.text().then(body => { const match = body.match(/name="analytics-ticket" content="([^"]+)"/); if (match) tickets.add(match[1]); }).catch(() => {}));
      }
    });
    return page;
  }
  async function tracked(page, action) {
    const recorded = page.waitForResponse(response => response.url().endsWith('/analytics/collect') && response.status() === 204);
    await action(); await recorded; await page.waitForTimeout(250);
  }
  async function leave(page) {
    // A beacon can reach the server after the initiating document is gone; verify its exit in the report.
    await page.locator('.footer a[href="/privacy"]').click();
    await page.goto('about:blank'); await new Promise(resolve => setTimeout(resolve, 350));
  }
  const student = await visitor();
  await tracked(student, () => student.goto(base + '/?utm_source=youtube&utm_medium=social'));
  await student.locator('#searchInput').fill('math'); await student.waitForTimeout(1550);
  await tracked(student, () => student.locator('.exam-card:not([hidden]) a.exam-link').first().click());
  await student.waitForTimeout(2300);
  await tracked(student, () => student.locator('.nav-menu a[href="/answer_keys"]').first().click());
  await tracked(student, () => student.locator('.nav-auth a[href="/signup"]').click());
  await student.locator('#name').fill('Browser review student');
  await student.locator('#email').fill('browser-student@example.test');
  await student.locator('#password').fill(password); await student.waitForTimeout(400);
  await tracked(student, () => student.locator('.auth-form button[type="submit"]').click());
  assert.equal(new URL(student.url()).pathname, '/');
  await tracked(student, () => student.locator('.nav-menu a[href="/answer_keys"]').first().click());
  await tracked(student, () => student.locator('a[href^="/view_key/"]').first().click());
  await student.waitForTimeout(1300);
  await tracked(student, () => student.locator('form[action="/logout"] button').click());
  await tracked(student, () => student.locator('.nav-auth a[href="/login"]').click());
  await student.locator('#email').fill('browser-student@example.test');
  await student.locator('#password').fill('A deliberately incorrect test password');
  await tracked(student, () => student.locator('.auth-form button[type="submit"]').click());
  assert.ok((await student.locator('.flash-container').innerText()).includes('Invalid email or password'));
  await student.locator('#email').fill('browser-student@example.test');
  await student.locator('#password').fill(password);
  await tracked(student, () => student.locator('.auth-form button[type="submit"]').click());
  assert.equal((await student.context().request.get(base + '/admin/analytics/data')).status(), 403);
  await leave(student);
  const google = await visitor();
  await tracked(google, () => google.goto(base + '/', { referer: 'https://www.google.com/search?q=study' }));
  await tracked(google, () => google.goto(base + '/tutors')); await leave(google);
  const instagram = await visitor();
  await tracked(instagram, () => instagram.goto(base + '/?utm_source=instagram&utm_medium=social'));
  await tracked(instagram, () => instagram.goto(base + '/tutors'));
  await instagram.locator('#subjectSelect').selectOption({ index: 1 }); await instagram.waitForTimeout(400);
  await tracked(instagram, () => instagram.goto(base + '/signup'));
  await instagram.locator('#name').fill('Abandoned form'); await instagram.waitForTimeout(450);
  await tracked(instagram, () => instagram.goto(base + '/about')); await leave(instagram);
  const referral = await visitor();
  await tracked(referral, () => referral.goto(base + '/', { referer: 'https://school.example.org/resources?private=remove' }));
  await leave(referral);
  const direct = await visitor();
  await tracked(direct, () => direct.goto(base + '/')); await leave(direct);
  await Promise.allSettled(reads);

  const admin = await browser.newContext({ userAgent: ua, viewport: { width: 1440, height: 1000 } });
  const login = await admin.request.get(base + '/login');
  const csrf = (await login.text()).match(/name="csrf-token" content="([^"]+)"/)[1];
  assert.equal((await admin.request.post(base + '/login', { form: { email: 'admin@example.test', password, csrf_token: csrf }, maxRedirects: 0 })).status(), 302);
  const page = await admin.newPage(); page.on('pageerror', error => errors.push(error.message));
  await page.goto(base + '/admin/analytics');
  await page.waitForFunction(() => document.getElementById('analyticsContent').getAttribute('aria-busy') === 'false');
  const result = await (await admin.request.get(base + '/admin/analytics/data?period=30d')).json();
  assert.equal(result.summary.visitors, 5);
  assert.equal(result.summary.visits, 5);
  assert.equal(result.summary.views, tickets.size);
  assert.equal(result.summary.signups, 1);
  assert.equal(result.summary.tracked_signups, 1);
  assert.equal(result.summary.conversion, 20);
  assert.equal(result.summary.signup_abandoned, 1);
  assert.deepEqual(result.sources.map(row => row.source).sort(), ['Direct', 'Google', 'Instagram', 'YouTube', 'school.example.org'].sort());
  assert.equal(result.sources.find(row => row.source === 'school.example.org').referrer, 'school.example.org');
  assert.equal(result.signup_pages[0].path, '/answer_keys');
  assert.equal(result.entries.reduce((sum,row) => sum + row.visits, 0), 5);
  assert.equal(result.exits.reduce((sum,row) => sum + row.visits, 0), 5);
  assert.ok(result.pages.some(row => row.average_time >= 2));
  for (const name of ['signup_start', 'signup_complete', 'login', 'search', 'button_click', 'feature_use', 'signup_leave']) assert.ok(result.event_counts.some(row => row.name === name), name);
  assert.ok(result.journeys.length && result.transitions.length);
  assert.ok(!JSON.stringify(result).includes('browser-student@example.test'));
  assert.equal(await page.locator('#stat-visitors').innerText(), '5');

  for (const period of ['today', '7d', '30d', 'month', 'all']) {
    const changed = page.waitForResponse(response => response.url().includes('/admin/analytics/data?') && new URL(response.url()).searchParams.get('period') === period);
    await page.locator(`[data-period="${period}"]`).click();
    const filtered = await (await changed).json(); assert.equal(filtered.range.period, period); assert.equal(filtered.summary.visitors, 5);
  }
  await page.locator('[data-period="custom"]').click();
  await page.locator('#analyticsStart').fill('2025-01-01'); await page.locator('#analyticsEnd').fill('2025-01-02');
  const empty = page.waitForResponse(response => response.url().includes('period=custom'));
  await page.getByRole('button', { name: 'Apply dates' }).click(); assert.equal((await (await empty).json()).summary.views, 0);
  await page.waitForFunction(() => document.getElementById('stat-visitors').textContent === '0');
  await page.locator('#analyticsStart').fill(result.range.today); await page.locator('#analyticsEnd').fill(result.range.today);
  const today = page.waitForResponse(response => response.url().includes('period=custom'));
  await page.getByRole('button', { name: 'Apply dates' }).click(); assert.equal((await (await today).json()).summary.visitors, 5);
  await page.waitForFunction(() => document.getElementById('stat-visitors').textContent === '5');
  await page.locator('#pageSort').selectOption('least');
  assert.equal(await page.locator('#pageRows tr').first().locator('td').nth(1).innerText(), '0');
  await page.locator('#pageSort').selectOption('popular');
  await page.locator('#sourceChannel').selectOption('social'); assert.ok((await page.locator('#sourceRows').innerText()).includes('YouTube'));
  await page.locator('#sourceChannel').selectOption('all');
  await page.screenshot({ path: path.join(output, 'dashboard-desktop.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 }); await page.waitForTimeout(400);
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'Mobile has horizontal overflow');
  assert.ok(await page.locator('#stat-visitors').isVisible());
  await page.screenshot({ path: path.join(output, 'dashboard-mobile.png'), fullPage: true });
  await page.locator('.analytics-page-panel').screenshot({ path: path.join(output, 'page-table-mobile.png') });
  assert.deepEqual(errors, [], 'Browser JavaScript errors');
  assert.ok(collects.every(status => status === 204), 'All browser collection requests should succeed');
  const checks = { visitors: result.summary.visitors, visits: result.summary.visits, exact_page_views: result.summary.views,
    observed_html_pages: tickets.size, successful_signups: result.summary.signups, conversion_percent: result.summary.conversion,
    abandonment: result.summary.signup_abandoned, sources: result.sources.map(row => row.source),
    entry_exit_visits: [5, 5], date_presets: 5, custom_empty_and_today: true, mobile_overflow: false, browser_errors: errors,
    collect_requests: collects.length, all_collect_requests_204: true, database: 'isolated analytics-review.db' };
  fs.writeFileSync(path.join(output, 'browser-checks.json'), JSON.stringify(checks, null, 2));
  console.log(JSON.stringify(checks, null, 2));
  await browser.close();
})().catch(error => { console.error(error.stack); process.exit(1); });
