const path = require('path');
const fs = require('fs');
const {bundle} = require('@remotion/bundler');
const {getCompositions, openBrowser, renderStill, renderMedia} = require('@remotion/renderer');
const root = path.resolve(__dirname, '..');
const qa = path.join(root, 'qa', 'math-short');
const output = path.resolve(root, '../output/shorts');
fs.mkdirSync(qa, {recursive: true});
fs.mkdirSync(output, {recursive: true});

(async () => {
  const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts'), outDir: path.join(qa, 'bundle')});
  const browser = await openBrowser('chrome', {browserExecutable: process.env.REMOTION_BROWSER_EXECUTABLE || 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  try {
    const compositions = await getCompositions(serveUrl, {puppeteerInstance: browser});
    const composition = compositions.find(c => c.id === 'TZStudiesMathShort');
    if (!composition) throw new Error('Math Short composition missing');
    fs.writeFileSync(path.join(qa, 'composition.json'), JSON.stringify(composition, null, 2));
    if (process.argv[2] === 'preview') {
      for (const frame of [0, 75, 166, 252, 346, 460, 580, 690, 750, 867, 958, 1050, 1125, 1194, 1250, 1340, 1460, 1559]) {
        await renderStill({serveUrl, composition, frame, puppeteerInstance: browser, output: path.join(qa, `frame-${frame}.png`), imageFormat: 'png', scale: .5});
        console.log(`Preview ${frame} (${(frame / 30).toFixed(2)}s)`);
      }
      return;
    }
    let previous = -1;
    const result = await renderMedia({
      serveUrl, composition, puppeteerInstance: browser,
      outputLocation: path.join(output, 'TZStudies-Math-Short.mp4'),
      codec: 'h264', crf: 17, pixelFormat: 'yuv420p', colorSpace: 'bt709',
      imageFormat: 'jpeg', jpegQuality: 96, audioCodec: 'aac', audioBitrate: '320k', sampleRate: 48000,
      x264Preset: 'medium', concurrency: 4, overwrite: true,
      metadata: {title: 'Can you solve this Tanzanian exam question? | TZStudies', artist: 'TZStudies', comment: 'CSEE 2024 Basic Mathematics Q10(b). Original music and sound effects.'},
      onProgress: ({progress, renderedFrames}) => {
        const step = Math.floor(progress * 20);
        if (step > previous) {previous = step; console.log(`${Math.round(progress * 100)}% — ${renderedFrames} frames`);}
      },
    });
    fs.writeFileSync(path.join(qa, 'render.json'), JSON.stringify({composition, slowestFrames: result.slowestFrames}, null, 2));
    await renderStill({serveUrl, composition, frame: 75, puppeteerInstance: browser, output: path.join(output, 'TZStudies-Math-Short-Poster.png'), imageFormat: 'png'});
    console.log('52-second Short and portrait poster exported.');
  } finally {await browser.close({silent: true});}
})().catch(error => {console.error(error); process.exitCode = 1;});
