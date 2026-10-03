const { chromium } = require(process.env.TZ_NODE_MODULES + '/playwright');
const fs = require('fs');
const path = require('path');
const base = 'http://127.0.0.1:5050';
const root = path.resolve(__dirname, '..');
const captures = path.join(root, 'public', 'captures');
const raw = path.join(root, 'raw');
fs.mkdirSync(captures, { recursive: true });
fs.mkdirSync(raw, { recursive: true });
let browser;
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
async function pointer(page) {
  await page.evaluate(() => {
    const cursor = document.createElement('div');
    cursor.id = 'video-pointer';
    cursor.innerHTML = '<svg width="30" height="34" viewBox="0 0 30 34"><path d="M3 2v24l7-6 5 11 5-3-5-10 10-1Z" fill="#133c3b" stroke="white" stroke-width="2.4"/></svg>';
    Object.assign(cursor.style, {position:'fixed',left:'720px',top:'420px',pointerEvents:'none',zIndex:'2147483647',filter:'drop-shadow(0 2px 3px #0004)'});
    document.body.appendChild(cursor);
    document.addEventListener('mousemove', event => {cursor.style.left = event.clientX+'px'; cursor.style.top = event.clientY+'px';});
  });
}
async function click(page, locator) {
  const box = await locator.boundingBox();
  if (!box) throw new Error('Missing control');
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, {steps:30});
  await pause(400);
  await locator.click();
}
async function scroll(page, y) {
  await page.evaluate(y => window.scrollTo({top:y,behavior:'smooth'}), y);
  await pause(1300);
}
async function shot(page, name, fullPage=false) {
  await page.evaluate(() => {const c=document.getElementById('video-pointer'); if(c)c.style.visibility='hidden';});
  await page.screenshot({path:path.join(captures,name+'.png'),fullPage});
  await page.evaluate(() => {const c=document.getElementById('video-pointer'); if(c)c.style.visibility='visible';});
}
async function videoContext(name, storageState, viewport={width:1440,height:900}) {
  const context = await browser.newContext({ viewport, storageState, serviceWorkers:'block', recordVideo:{dir:raw,size:viewport}, deviceScaleFactor:1 });
  const page = await context.newPage();
  const video = page.video();
  return {context,page,finish:async()=>{await context.close();await video.saveAs(path.join(raw,name+'.webm'));console.log('Recorded '+name);}};
}
(async()=>{
  browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  // This account is created only in the isolated promo-preview SQLite database.
  const auth=await browser.newContext({viewport:{width:1440,height:900},serviceWorkers:'block'});
  const login=await auth.newPage();
  await login.goto(base+'/signup',{waitUntil:'networkidle'});
  await login.locator('#name').fill('Student');
  await login.locator('#email').fill('promo-'+Date.now()+'@example.com');
  await login.locator('#password').fill('Study orbit mango lantern 123');
  await login.locator('button[type=submit]').click();
  await login.waitForURL(base+'/');
  const storage=await auth.storageState();
  await auth.close();
  if (!fs.existsSync(path.join(raw,'library.webm'))) {
  const library=await videoContext('library');
  await library.page.goto(base,{waitUntil:'networkidle'});
  await library.page.evaluate(()=>document.fonts.ready);
  await shot(library.page,'home');
  await shot(library.page,'home-full',true);
  await pointer(library.page);
  await pause(1200);
  const libraryY=await library.page.locator('#examSection').evaluate(e=>e.offsetTop-110);
  await scroll(library.page,libraryY);
  await shot(library.page,'library-all');
  await pause(1600);
  await click(library.page,library.page.getByRole('button',{name:'Form 2',exact:true}));
  await pause(1000);
  await click(library.page,library.page.locator('#searchInput'));
  await library.page.locator('#searchInput').pressSequentially('Mathematics',{delay:100});
  await pause(1500);
  await click(library.page,library.page.locator('#yearFilter'));
  await library.page.keyboard.press('Home');
  await library.page.keyboard.press('ArrowDown');
  await library.page.keyboard.press('Enter');
  await pause(1700);
  // Explicitly choose the year to keep the demonstrated result reproducible.
  await library.page.locator('#yearFilter').selectOption('2024');
  await shot(library.page,'library-filtered');
  await pause(2300);
  await click(library.page,library.page.locator('.exam-card:visible .exam-link').first());
  await library.page.waitForLoadState('networkidle');
  await pause(2400);
  await shot(library.page,'paper-preview');
  await library.finish();
  }
  const keys=await videoContext('answers',storage);
  await keys.page.goto(base+'/answer_keys',{waitUntil:'networkidle'});
  await shot(keys.page,'answer-library');
  await pointer(keys.page);
  await pause(1000);
  const keyLink=keys.page.locator('.exam-card[data-grade="F2"][data-subject="Basic Mathematics"][data-year="2024"] .answer-link');
  await keyLink.scrollIntoViewIfNeeded();
  await pause(1000);
  const keyHref=await keyLink.getAttribute('href');
  await click(keys.page,keyLink);
  await keys.page.waitForLoadState('networkidle');
  await pause(3000);
  await shot(keys.page,'answer-preview');
  await pause(1500);
  await keys.finish();
  const tutors=await videoContext('tutors');
  await tutors.page.goto(base+'/tutors',{waitUntil:'networkidle'});
  await tutors.page.evaluate(()=>document.fonts.ready);
  await shot(tutors.page,'tutors-all');
  await pointer(tutors.page);
  await pause(1600);
  await click(tutors.page,tutors.page.locator('#subjectSelect'));
  await tutors.page.keyboard.press('m');
  await tutors.page.keyboard.press('Enter');
  await tutors.page.locator('#subjectSelect').selectOption('Math');
  await pause(1800);
  await shot(tutors.page,'tutors-filtered');
  await scroll(tutors.page,330);
  await pause(6800);
  await tutors.finish();
  const mobile=await videoContext('mobile',undefined,{width:390,height:844});
  await mobile.page.goto(base,{waitUntil:'networkidle'});
  await mobile.page.evaluate(()=>document.fonts.ready);
  await shot(mobile.page,'mobile-home');
  await shot(mobile.page,'mobile-full',true);
  await pause(1600);
  await click(mobile.page,mobile.page.getByRole('link',{name:/Explore past papers/}));
  await pause(1500);
  await shot(mobile.page,'mobile-library');
  await scroll(mobile.page,await mobile.page.locator('#examGrid').evaluate(e=>e.getBoundingClientRect().top+window.scrollY-140));
  await pause(6500);
  await shot(mobile.page,'mobile-papers');
  await mobile.finish();
  fs.writeFileSync(path.join(captures,'manifest.json'),JSON.stringify({capturedAt:new Date().toISOString(),origin:base,keyHref,counts:{papers:60,answerKeys:60,levels:4},account:'Isolated local preview account; no production data'},null,2));
  await browser.close();
})().catch(async error=>{console.error(error);if(browser)await browser.close();process.exitCode=1;});
