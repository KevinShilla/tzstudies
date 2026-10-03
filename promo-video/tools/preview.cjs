const path=require('path');
const fs=require('fs');
const {bundle}=require('@remotion/bundler');
const {getCompositions,openBrowser,renderStill}=require('@remotion/renderer');
const root=path.resolve(__dirname,'..');
const qa=path.join(root,'qa');
fs.mkdirSync(qa,{recursive:true});
(async()=>{
  const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts'),outDir:path.join(qa,'bundle')});
  const browser=await openBrowser('chrome',{browserExecutable:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  try {
    const comps=await getCompositions(serveUrl,{puppeteerInstance:browser});
    fs.writeFileSync(path.join(qa,'compositions.json'),JSON.stringify(comps,null,2));
    for(const [id,frames] of [['TZStudiesLaunch',[120,265,460,600,810,974,1120,1270,1485,1750,1940,2110]],['TZStudiesSocial',[65,232,398,567,755]]]){
      const composition=comps.find(c=>c.id===id);
      for (const frame of frames){
        await renderStill({composition,serveUrl,frame,output:path.join(qa,id+'-'+frame+'.png'),puppeteerInstance:browser,imageFormat:'png',scale:.75});
        console.log(id+' frame '+frame+' ready');
      }
    }
  }finally{await browser.close({silent:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
