const path=require('path');
const fs=require('fs');
const {bundle}=require('@remotion/bundler');
const {getCompositions,renderMedia,renderStill}=require('@remotion/renderer');
const root=path.resolve(__dirname,'..');
const qa=path.join(root,'qa');
const output=path.resolve(root,'../output/video');
fs.mkdirSync(output,{recursive:true});
fs.mkdirSync(qa,{recursive:true});
(async()=>{
  const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts'),outDir:path.join(qa,'final-bundle')});
  const browserExecutable=process.env.REMOTION_BROWSER_EXECUTABLE||'C:/Program Files/Google/Chrome/Application/chrome.exe';
  const comps=await getCompositions(serveUrl,{browserExecutable});
  const targets=[['TZStudiesLaunch','MyTZStudies-Launch-1080p.mp4'],['TZStudiesSocial','MyTZStudies-Social-Vertical.mp4']];
  const only=process.argv[2];
  for(const [id,name] of targets){
    if(only && only!==id)continue;
    const composition=comps.find(c=>c.id===id);
    let previous=-1;
    console.log('Rendering '+id+' — '+composition.width+'×'+composition.height+', '+composition.durationInFrames/composition.fps+'s');
    const result=await renderMedia({
      serveUrl,composition,browserExecutable,outputLocation:path.join(output,name),
      codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:95,
      audioCodec:'aac',audioBitrate:'320k',sampleRate:48000,colorSpace:'bt709',
      x264Preset:'medium',concurrency:4,overwrite:true,logLevel:'warn',
      metadata:{title:id==='TZStudiesLaunch'?'MyTZStudies — Start ready':'MyTZStudies — Your next chapter',artist:'MyTZStudies',comment:'Original music. Real MyTZStudies website captures.'},
      onProgress:({progress,renderedFrames})=>{const step=Math.floor(progress*20);if(step>previous){previous=step;console.log(id+' '+Math.round(progress*100)+'% ('+renderedFrames+' frames)');}}
    });
    fs.writeFileSync(path.join(qa,id+'-render.json'),JSON.stringify({composition,slowestFrames:result.slowestFrames},null,2));
    console.log('Exported '+name);
  }
  await renderStill({serveUrl,composition:comps.find(c=>c.id==='TZStudiesLaunch'),frame:2110,browserExecutable,output:path.join(output,'MyTZStudies-Poster.png'),imageFormat:'png'});
  console.log('Poster exported.');
})().catch(error=>{console.error(error);process.exitCode=1;});
