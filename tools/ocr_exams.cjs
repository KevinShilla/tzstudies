// OCR is local. Only the public language model files are downloaded.
const fs = require('fs');
const path = require('path');
const { createWorker } = require(process.env.TZ_NODE_MODULES + '/tesseract.js');
const root = path.resolve(__dirname, '..');
const jobs = JSON.parse(fs.readFileSync(path.join(root, 'tmp/pdfs/ocr-jobs.json'), 'utf8'));
let next = 0;
let completed = 0;
async function run() {
  const worker = await createWorker('eng', 1, { cachePath: path.join(root, 'tmp/pdfs') });
  while (next < jobs.length) {
    const job = jobs[next++];
    if (!fs.existsSync(job.output)) {
      const result = await worker.recognize(job.image);
      fs.writeFileSync(job.output, result.data.text);
    }
    completed++;
    if (completed % 10 === 0) console.log(`OCR ${completed}/${jobs.length}`);
  }
  await worker.terminate();
}
Promise.all([run(), run(), run()]).then(() => {
  const inventory = JSON.parse(fs.readFileSync(path.join(root, 'tmp/pdfs/review-inventory.json'), 'utf8'));
  for (const exam of inventory) {
    const text = exam.pages.map(p => `PAGE ${p.page}\n${p.scanned ? fs.readFileSync(p.image.replace(/\.png$/, '.txt'), 'utf8') : p.text}`).join('\n\n');
    fs.writeFileSync(path.join(root, 'tmp/pdfs', exam.file.replace(/\.pdf$/i, '') + '-readable.txt'), text);
  }
  console.log('OCR complete.');
}).catch(err => { console.error(err); process.exitCode = 1; });
