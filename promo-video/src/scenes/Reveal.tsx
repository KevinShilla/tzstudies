import {useCurrentFrame,interpolate} from 'remotion';
import {Browser,C,Label,Stage,Wordmark,motion} from '../design';
export const Reveal=()=>{
  const f=useCurrentFrame();
  const move=motion(f,56,58);
  return <Stage dark>
    <div style={{position:'absolute',left:0,right:0,top:interpolate(move,[0,1],[350,94]),textAlign:'center',opacity:motion(f,0,25),scale:String(interpolate(motion(f,0,35),[0,1],[.92,1]))}}>
      <Wordmark dark size={126}/>
      <Label dark style={{marginTop:30,fontSize:27,letterSpacing:4}}>Your free Tanzania exam library</Label>
    </div>
    <Browser image="home" width={1420} height={785} style={{left:250,top:410,translate:`0 ${(1-motion(f,64,54))*700}px`,scale:String(interpolate(f,[64,196],[.92,1.04],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}}/>
    <div style={{position:'absolute',left:122,bottom:57,fontSize:23,color:C.mint,opacity:motion(f,120)}}>Made for your next step.</div>
  </Stage>;
};
