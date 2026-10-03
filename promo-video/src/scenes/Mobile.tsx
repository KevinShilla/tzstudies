import {interpolate,useCurrentFrame} from 'remotion';
import {C,Label,Phone,RevealText,Stage,motion} from '../design';
export const Mobile=()=>{
  const f=useCurrentFrame();
  return <Stage>
    <Label style={{position:'absolute',left:128,top:140}}>A little practice, anywhere</Label>
    <RevealText size={112} style={{position:'absolute',left:116,top:278}}>Your pace.<br/>Your place.</RevealText>
    <div style={{position:'absolute',left:129,top:611,fontSize:37,lineHeight:1.55,opacity:motion(f,45),color:C.muted}}>Read online.<br/>Download PDFs. Keep practising.</div>
    <div style={{position:'absolute',left:130,bottom:123,fontSize:26,color:C.green,opacity:motion(f,150)}}>Built for your next study session.</div>
    <Phone image="mobile-papers" width={344} style={{left:1370,top:245,rotate:'8deg',translate:`${130*(1-motion(f,35,60))}px ${-20*Math.sin(f/80)}px`,opacity:motion(f,35,50)}}/>
    <Phone video="mobile" trim={15} width={390} style={{left:1056,top:121,rotate:'-4deg',translate:`${90*(1-motion(f,0,55))}px ${interpolate(f,[0,261],[40,-8])}px`,scale:String(.98+motion(f,0)*.02)}}/>
  </Stage>;
};
