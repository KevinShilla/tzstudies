import {CanvasImage,interpolate,staticFile,useCurrentFrame} from 'remotion';
import {C,Label,RevealText,Stage,motion,Wordmark} from '../design';

export const Hook=()=>{
  const f=useCurrentFrame();
  const second=motion(f,78,28);
  return <Stage dark>
    <Wordmark dark size={40} style={{position:'absolute',left:115,top:82,opacity:motion(f,5,20)}}/>
    <Label dark style={{position:'absolute',left:118,top:256,opacity:motion(f,8)}}>Your next chapter</Label>
    <div style={{position:'absolute',left:105,top:340,zIndex:3,opacity:1-second,translate:`0 ${-second*65}px`}}><RevealText size={174} start={2}>Next exam?</RevealText></div>
    <div style={{position:'absolute',left:105,top:340,zIndex:3,opacity:second}}><RevealText size={170} start={78}>Start <span style={{color:C.mint}}>ready.</span></RevealText></div>
    <div style={{position:'absolute',left:121,top:599,fontSize:36,opacity:motion(f,114,24),translate:`0 ${(1-motion(f,114))*20}px`,color:'#d9eadf'}}>A little practice goes a long way.</div>
    <div style={{position:'absolute',width:660,height:730,right:-32,top:335,rotate:`${interpolate(f,[0,195],[15,4])}deg`,translate:`${interpolate(f,[0,90,195],[120,45,0])}px ${interpolate(f,[0,195],[180,5])}px`,opacity:.13}}><CanvasImage src={staticFile('captures/answer-title.png')} style={{width:660,height:932}}/></div>
    <div style={{position:'absolute',width:530,height:748,right:168,top:515,rotate:`${interpolate(f,[0,195],[-15,-7])}deg`,translate:`0 ${interpolate(f,[0,195],[170,-35])}px`,opacity:.11}}><CanvasImage src={staticFile('captures/answer-page.png')} style={{width:530,height:748}}/></div>
    <div style={{position:'absolute',left:120,bottom:130,height:3,width:interpolate(f,[90,158],[0,210],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}),background:C.mint}}/>
    <div style={{position:'absolute',right:118,bottom:115,color:C.mint,fontSize:24,letterSpacing:2}}>PRACTICE / UNDERSTAND / GROW</div>
  </Stage>;
};
