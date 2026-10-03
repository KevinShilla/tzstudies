import {useCurrentFrame} from 'remotion';
import {Browser,C,Label,RevealText,Stage,motion} from '../design';
export const Browse=()=>{
  const f=useCurrentFrame();
  const focus=motion(f,173,70);
  return <Stage>
    <Label style={{position:'absolute',left:126,top:80}}>Past national papers</Label>
    <RevealText size={89} style={{position:'absolute',left:116,top:145}}>Find your next paper.</RevealText>
    <div style={{position:'absolute',right:138,top:137,fontSize:31,color:C.green,opacity:motion(f,53),textAlign:'right',lineHeight:1.7}}>Your level.<br/>Your subject.<br/>Your year.</div>
    <Browser video={f<354?'library':undefined} image={f>=354?'paper-preview':undefined} trim={110} width={1580} height={668} offsetY={-motion(f,65,165)*248} style={{left:170,top:332,translate:`${-focus*15}px ${(1-motion(f,0))*100}px`,scale:String(1+focus*.10)}}/>
  </Stage>;
};
