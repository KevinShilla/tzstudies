import {CanvasImage,interpolate,staticFile,useCurrentFrame} from 'remotion';
import {Browser,C,Label,RevealText,Stage,motion} from '../design';
export const Answers=()=>{
  const f=useCurrentFrame();
  const focus=motion(f,95,34);
  return <Stage dark>
    <Label dark style={{position:'absolute',left:128,top:91}}>Worked answer keys</Label>
    <div style={{position:'absolute',left:119,top:221,width:625,opacity:1-focus}}><RevealText size={97}>Go beyond<br/>the answer.</RevealText></div>
    <div style={{position:'absolute',left:119,top:223,width:575,opacity:focus}}><RevealText size={91} start={98}>See how.<br/><span style={{color:C.mint}}>Step by step.</span></RevealText></div>
    <div style={{position:'absolute',left:128,top:573,width:480,fontSize:31,lineHeight:1.55,color:'#d2e8dd',opacity:motion(f,35)}}>Try the question.<br/>Follow the working.<br/>Check your answer.</div>
    <div style={{position:'absolute',left:128,bottom:102,fontSize:25,color:C.mint,opacity:motion(f,120)}}>Free with your MyTZStudies account.</div>
    <Browser image="answer-preview" width={1050} height={752} url="mytzstudies.com / answer keys" style={{left:760,top:210,opacity:1-focus,rotate:'-1.5deg',scale:String(.97+motion(f,0)*.03)}}/>
    <div style={{position:'absolute',left:730,top:270,width:1070,height:480,background:'#ffffff',borderRadius:22,overflow:'hidden',boxShadow:'0 35px 75px #001e2c66',opacity:focus,translate:`${60*(1-focus)}px ${20*(1-focus)}px`,scale:String(1+interpolate(f,[150,350],[0,.03],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}}>
      <CanvasImage src={staticFile('captures/answer-question.png')} style={{position:'absolute',width:1070,height:378,top:50,left:0}}/>
      <div style={{position:'absolute',left:17,right:17,top:222,height:41,borderRadius:5,border:`3px solid ${C.green}`,opacity:interpolate(f,[160,177,226,240],[0,.7,.7,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
      <div style={{position:'absolute',left:17,right:17,top:270,height:61,borderRadius:5,border:`3px solid ${C.green}`,opacity:interpolate(f,[234,248,286,301],[0,.7,.7,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
      <div style={{position:'absolute',left:17,right:17,top:341,height:76,borderRadius:5,border:`3px solid ${C.green}`,opacity:motion(f,302)}}/>
    </div>
    <div style={{position:'absolute',left:750,top:813,fontSize:34,color:C.mint,opacity:motion(f,320)}}>Working → Understanding → Final answer</div>
  </Stage>;
};
