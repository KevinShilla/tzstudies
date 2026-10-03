import {CanvasImage,staticFile,useCurrentFrame} from 'remotion';
import {C,Label,RevealText,Stage,motion} from '../design';
export const Problem=()=>{
  const f=useCurrentFrame();
  return <Stage>
    <Label style={{position:'absolute',left:125,top:184}}>Make your study time count</Label>
    <div style={{position:'absolute',left:115,top:333,zIndex:3}}>
      <RevealText size={118}>Less searching.</RevealText>
      <RevealText size={118} start={39} style={{color:C.green}}>More practising.</RevealText>
    </div>
    <div style={{position:'absolute',right:135,top:170,width:475,height:670,rotate:`${7-motion(f,20)*5}deg`,translate:`${90*(1-motion(f,0))}px ${30*Math.sin(f/95)}px`,opacity:.15}}><CanvasImage src={staticFile('captures/answer-title.png')} style={{width:475,height:670}}/></div>
    <div style={{position:'absolute',bottom:180,left:130,fontSize:31,opacity:motion(f,63),color:C.muted}}>The right paper. In one place.</div>
  </Stage>;
};
