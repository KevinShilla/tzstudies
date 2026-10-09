// Local OCR for scan pages. Public OCR language data is the only download.
const fs = require('fs');
const path = require('path');
const {createWorker} = require(process.env.TZ_NODE_MODULES + '/tesseract.js');
const root = path.resolve(__dirname, '..');
const dest = path.join(root, 'tmp/primary-answers');
const jobs = JSON.parse(fs.readFileSync(path.join(dest, 'ocr-jobs.json'), 'utf8'));
let next = 0;
let done = 0;

async function run() {
  const worker = await createWorker('eng', 1, {cachePath: path.join(root, 'tmp/pdfs')});
  while (next < jobs.length) {
    const job = jobs[next++];
    if (!fs.existsSync(job.output)) {
      const result = await worker.recognize(job.image);
      fs.writeFileSync(job.output, result.data.text);
    }
    done++;
    if (done % 10 === 0) console.log(`Scan pages read: ${done}/${jobs.length}`);
  }
  await worker.terminate();
}

Promise.all([run(), run(), run()]).then(() => {
  for (const item of JSON.parse(fs.readFileSync(path.join(dest, 'inventory.json'), 'utf8'))) {
    const folder = path.join(dest, item.exam.replace(/\.pdf$/i, ''));
    const source = JSON.parse(fs.readFileSync(path.join(folder, 'source.json'), 'utf8'));
    const text = source.pages.map(p => {
      const ocr = p.image.replace(/\.png$/, '.txt');
      return `PAGE ${p.page}\n${p.scanned && fs.existsSync(ocr) ? fs.readFileSync(ocr, 'utf8') : p.text}`;
    }).join('\n\n');
    fs.writeFileSync(path.join(folder, 'source-ocr.txt'), text);
  }
  console.log('Primary scan OCR complete; page images remain the source of truth.');
}).catch(() => {
  console.error('Local OCR failed. Review the original scan images.');
  process.exitCode = 1;
});
