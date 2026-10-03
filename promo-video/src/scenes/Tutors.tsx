import {useCurrentFrame} from 'remotion';
import {Browser,C,Label,RevealText,Stage,motion} from '../design';
export const Tutors=()=>{
  const f=useCurrentFrame();
  const p=motion(f,145,80);
  return <Stage dark>
    <Label dark style={{position:'absolute',left:130,top:84}}>Support for your next step</Label>
    <RevealText size={90} style={{position:'absolute',left:119,top:146}}>Find a little guidance.</RevealText>
    <Browser video={f<135?'tutors':undefined} image={f>=135?'tutors-full':undefined} imageHeight={1500} trim={18} width={1570} height={670} offsetY={-motion(f,75,60)*90-motion(f,135,105)*400} url="mytzstudies.com / tutors" style={{left:175,top:325,scale:String(1+p*.06),translate:`${-p*15}px ${-p*35+(1-motion(f,0))*80}px`}}/>
    <div style={{position:'absolute',right:135,top:102,color:C.mint,fontSize:26,opacity:motion(f,50)}}>Choose a subject. Contact a tutor.</div>
  </Stage>;
};
