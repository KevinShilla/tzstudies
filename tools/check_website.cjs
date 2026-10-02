const { chromium } = require(process.env.TZ_NODE_MODULES + '/playwright');
const fs = require('fs');
const assert = require('assert');
let browser;
(async () => {
  browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', err => errors.push(err.message));
  fs.mkdirSync('tmp/website', { recursive: true });
  await page.goto('http://127.0.0.1:5050', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'tmp/website/home-desktop.png', fullPage: true });
  const total = await page.locator('#examGrid .exam-card').count();
  assert.strictEqual(total, 60);
  const cards = await page.locator('#examGrid .exam-card').evaluateAll(nodes => nodes.map(node => ({
    paper: node.querySelector('.exam-link').getAttribute('href'),
    key: node.querySelector('.answer-link').getAttribute('href')
  })));
  assert(cards.every(card => card.key.startsWith('/view_key/')));
  await page.getByRole('button', { name: 'Form 2', exact: true }).click();
  await page.locator('#searchInput').fill('English');
  await page.locator('#yearFilter').selectOption('2024');
  assert.strictEqual(await page.locator('#examGrid .exam-card:visible').count(), 1);
  assert.strictEqual(await page.locator('#examGrid .exam-card:visible').getAttribute('data-grade'), 'F2');
  await page.locator('#searchInput').fill('no-such-subject');
  assert(await page.locator('#noResults').isVisible());
  await page.getByRole('button', { name: 'Clear filters' }).click();
  assert.strictEqual(await page.locator('#examGrid .exam-card:visible').count(), total);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: 'tmp/website/home-mobile.png', fullPage: true });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  await page.getByRole('button', { name: 'Open navigation' }).click();
  assert(await page.locator('#navMenu').isVisible());
  await page.screenshot({ path: 'tmp/website/menu-mobile.png' });
  await page.keyboard.press('Escape');
  assert(!(await page.locator('#navMenu').isVisible()));
  await page.goto('http://127.0.0.1:5050/view_key/BasicMath-F2-2023%20(Answer%20Key).pdf');
  assert(page.url().includes('/login?next='));
  await page.locator('main').getByRole('link', { name: 'Sign Up', exact: true }).click();
  await page.locator('#name').fill('Website Review');
  const email = 'website-review-' + Date.now() + '@example.com';
  await page.locator('#email').fill(email);
  await page.locator('#password').fill('ReviewPass123');
  await page.locator('button[type=submit]').click();
  await page.waitForURL('**/view_key/**');
  assert(await page.getByRole('link', { name: 'Download answer key' }).isVisible());
  const pdf = await context.request.get('http://127.0.0.1:5050/serve_key/BasicMath-F2-2023%20(Answer%20Key).pdf');
  assert.strictEqual(pdf.status(), 200);
  assert((await pdf.body()).subarray(0, 4).toString() === '%PDF');
  for (const card of cards) {
    for (const [preview, servePrefix] of [[card.paper, '/serve/'], [card.key, '/serve_key/']]) {
      const response = await context.request.get('http://127.0.0.1:5050' + preview);
      assert.strictEqual(response.status(), 200, preview);
      const filename = preview.substring(preview.indexOf('/', 1) + 1);
      const file = await context.request.get('http://127.0.0.1:5050' + servePrefix + filename);
      assert.strictEqual(file.status(), 200, filename);
      assert((await file.body()).subarray(0, 4).toString() === '%PDF', filename);
    }
  }
  for (const route of ['/about', '/tutors', '/become_tutor', '/upload_exams', '/answer_keys', '/history', '/forgot-password', '/missing-review-page']) {
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
      const response = await page.goto('http://127.0.0.1:5050' + route, { waitUntil: 'networkidle' });
      assert.strictEqual(response.status(), route === '/missing-review-page' ? 404 : 200, route);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), route + ' overflows at ' + width);
      await page.screenshot({ path: 'tmp/website/' + route.slice(1) + '-' + width + '.png', fullPage: true });
    }
    if (route === '/tutors') {
      assert.strictEqual(await page.locator('.tutor-card').count(), 7);
      for (const photo of await page.locator('.tutor-card img').evaluateAll(nodes => nodes.map(node => node.src))) {
        assert.strictEqual((await context.request.get(photo)).status(), 200, photo);
      }
      await page.locator('#subjectSelect').selectOption('Math');
      assert.strictEqual(await page.locator('.tutor-card:visible').count(), 2);
      assert.strictEqual(await page.locator('#tutorCount').textContent(), '2 tutors');
    }
    if (route === '/answer_keys') assert.strictEqual(await page.locator('.exam-card').count(), 60);
    if (route === '/history') {
      const discussion = await page.locator('main a[href^="/paper/"]').first().getAttribute('href');
      await page.goto('http://127.0.0.1:5050' + discussion, { waitUntil: 'networkidle' });
      assert(await page.locator('#commentBody').isVisible());
      const commentText = 'Which step should I practise first? Review ' + Date.now();
      const replyText = 'Start by identifying the information in the question. Review ' + Date.now();
      await page.locator('#commentBody').fill(commentText);
      await page.getByRole('button', { name: 'Post Comment', exact: true }).click();
      await page.waitForLoadState('networkidle');
      assert(await page.getByText(commentText, { exact: true }).isVisible());
      await page.getByRole('button', { name: 'Reply', exact: true }).last().click();
      const reply = page.locator('.reply-form.open textarea');
      await reply.fill(replyText);
      await page.locator('.reply-form.open').getByRole('button', { name: 'Submit Reply' }).click();
      await page.waitForLoadState('networkidle');
      assert(await page.getByText(replyText, { exact: true }).isVisible());
      await page.screenshot({ path: 'tmp/website/discussion-mobile.png', fullPage: true });
      const iframe = await page.locator('.pdf-viewer').getAttribute('src');
      assert.strictEqual((await context.request.get('http://127.0.0.1:5050' + iframe.split('#')[0])).status(), 200);
    }
  }
  await page.goto('http://127.0.0.1:5050/logout');
  await page.goto('http://127.0.0.1:5050/login');
  await page.locator('#email').fill(email);
  await page.locator('#password').fill('ReviewPass123');
  await page.locator('button[type=submit]').click();
  await page.waitForURL('http://127.0.0.1:5050/');
  assert(await page.getByText('Hello, Website').isVisible() === false); // mobile menu is closed
  assert.strictEqual(errors.length, 0, errors.join('\n'));
  const result = { papers: total, answerKeys: cards.length, filters: 'passed', mobile: 'passed', signup: 'passed', login: 'passed', pdfDownloads: '120 passed', secondaryPages: 'passed', tutors: 'passed', discussion: 'passed', browserErrors: errors };
  fs.writeFileSync('tmp/website/check-results.json', JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
  await browser.close();
})().catch(async err => { console.error(err); if (browser) await browser.close(); process.exitCode = 1; });
