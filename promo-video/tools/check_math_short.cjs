const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');
const {chromium} = require(path.join(process.env.TZ_NODE_MODULES, 'playwright'));
const root = path.resolve(__dirname, '..');
const qa = path.join(root, 'qa/math-short');
const output = path.resolve(root, '../output/shorts');
const html = path.join(qa, 'playback.html');
fs.writeFileSync(html, `<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>TZStudies Math Short</title><style>body{margin:0;background:#123c3b;display:flex;justify-content:center}video{display:block;max-width:100vw;max-height:100vh;width:auto;height:auto}</style><video controls muted playsinline preload="auto" src="${pathToFileURL(path.join(output, 'TZStudies-Math-Short.mp4'))}"></video>`);

(async () => {
  const browser = await chromium.launch({executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true});
  try {
    const checks = [];
    for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
      const page = await browser.newPage({viewport});
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(pathToFileURL(html).href);
      await page.waitForFunction(() => document.querySelector('video').readyState >= 2);
      const metadata = await page.locator('video').evaluate(v => ({duration: v.duration, width: v.videoWidth, height: v.videoHeight, error: v.error && v.error.message}));
      if (metadata.duration >= 60 || metadata.width !== 1080 || metadata.height !== 1920 || metadata.error) throw new Error('Browser video metadata failed');
      await page.locator('video').evaluate(async v => {await v.play();});
      await page.waitForFunction(() => document.querySelector('video').currentTime > .2);
      await page.locator('video').evaluate(v => v.pause());
      for (const time of [5.1, 18.1, 29.7, 36.4, 44.7, 51.8]) {
        await page.locator('video').evaluate((v, t) => new Promise((resolve, reject) => {
          v.addEventListener('seeked', resolve, {once: true});
          v.addEventListener('error', () => reject(new Error('Video decode error')), {once: true});
          v.currentTime = t;
        }), time);
      }
      const layout = await page.locator('video').evaluate(v => {const r = v.getBoundingClientRect(); return {left: r.left, right: r.right, bottom: r.bottom, fits: r.left >= 0 && r.right <= innerWidth && r.bottom <= innerHeight};});
      if (!layout.fits || errors.length) throw new Error('Playback or responsive framing failed');
      await page.screenshot({path: path.join(qa, `playback-${viewport.width}.png`)});
      checks.push({viewport, metadata, layout, plays: true, sought_through_all_scenes: true, page_errors: errors});
      await page.close();
    }
    fs.writeFileSync(path.join(output, 'playback-checks.json'), JSON.stringify(checks, null, 2));
    console.log('Desktop and phone browser playback, scene seeking, and framing passed.');
  } finally {await browser.close();}
})().catch(error => {console.error(error); process.exitCode = 1;});
