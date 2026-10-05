/* Run after serve_payments_review.py; all payments and credentials here are mocks. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/Kevin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'tmp', 'payments-review');
const base = 'http://127.0.0.1:5052';
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  return value;
}
(async () => {
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe', headless:true});
  try {
    const context = await browser.newContext({viewport:{width:1440,height:1000}, serviceWorkers:'block'});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {
      if (message.type() === 'error' && /Content Security Policy|Refused to|blocked/i.test(message.text())) errors.push(message.text());
    });
    await page.goto(base + '/login');
    await page.locator('[name="email"]').fill('admin@example.test');
    await page.locator('[name="password"]').fill('River stones remember sunrise!');
    await Promise.all([page.waitForURL(url => !url.pathname.endsWith('/login')), page.locator('form button[type="submit"]').click()]);
    await page.goto(base + '/admin/payments');
    assert.equal(await page.locator('.payment-heading h1').innerText(), 'Payments');
    await page.screenshot({path:path.join(output,'admin-desktop.png'), fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({path:path.join(output,'admin-mobile.png'), fullPage:true});
    let reference;
    await context.route('https://checkout.clickpesa.com/mock/**', async route => {
      reference = new URL(route.request().url()).pathname.split('/').pop();
      await route.fulfill({status:200, contentType:'text/html', body:`<!doctype html><meta name="viewport" content="width=device-width"><h1>Mock hosted checkout</h1><p>TZS 1,000 · no real funds</p><a href="${base}/payments/return?success=true&status=SUCCESS&orderReference=${reference}">Return to TZStudies</a>`});
    });
    await Promise.all([page.waitForURL('https://checkout.clickpesa.com/mock/**'), page.getByRole('button',{name:/Continue to ClickPesa/}).click()]);
    assert(reference && /^[A-Z0-9]{34}$/.test(reference));
    await page.getByRole('link',{name:'Return to TZStudies'}).click();
    await page.waitForURL(base + '/payments/return**');
    assert.equal(await page.locator('#paymentTitle').innerText(),'Awaiting payment confirmation');
    await page.screenshot({path:path.join(output,'return-pending-mobile.png'), fullPage:true});
    const record = {id:'browser-payment-1', clientId:'mock-client', orderReference:reference, status:'SUCCESS', collectedAmount:1000, collectedCurrency:'TZS', paymentReference:'browser-receipt-1'};
    fs.writeFileSync(path.join(output,'provider-state.json'), JSON.stringify(record));
    const payload = {event:'PAYMENT RECEIVED',data:record};
    payload.checksum = crypto.createHmac('sha256','mock-checksum').update(JSON.stringify(canonical(payload))).digest('hex');
    let response = await fetch(base + '/payments/webhooks/clickpesa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    assert.equal(response.status,204);
    response = await fetch(base + '/payments/webhooks/clickpesa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    assert.equal(response.status,204);
    await page.waitForFunction(() => document.querySelector('#paymentTitle')?.textContent === 'Payment confirmed',{},{timeout:15000});
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({path:path.join(output,'return-paid-mobile.png'), fullPage:true});
    await page.reload();
    assert((await page.locator('.payment-receipt').innerText()).includes('browser-receipt-1'));
    await page.setViewportSize({width:1440,height:1000});
    await page.screenshot({path:path.join(output,'return-paid-desktop.png'), fullPage:true});
    await page.goto(base + '/admin/payments');
    assert.equal(await page.locator('.payment-table tbody tr').count(),1);
    assert((await page.locator('.payment-table').innerText()).includes('Paid'));
    const html = await page.content();
    for (const secret of ['mock-api-key','mock-checksum']) assert(!html.includes(secret));
    assert.deepEqual(errors,[]);
    const results = {desktop:[1440,1000],mobile:[390,844],hosted_navigation:true,return_only_stays_pending:true,
      signed_webhook_confirmed:true,duplicate_kept_one_order:true,status_poll_updated:true,receipt_visible:true,
      mobile_overflow:false,browser_errors:errors,secrets_in_html:false};
    fs.writeFileSync(path.join(output,'browser-checks.json'),JSON.stringify(results,null,2));
    console.log(JSON.stringify(results,null,2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
