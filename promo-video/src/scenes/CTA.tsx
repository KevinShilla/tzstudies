import {interpolate,useCurrentFrame} from 'remotion';
import {Arrow,C,RevealText,Stage,Wordmark,motion} from '../design';
export const CTA=()=>{
  const f=useCurrentFrame();
  return <Stage dark>
    <Wordmark dark size={60} style={{position:'absolute',left:0,right:0,top:129,textAlign:'center',opacity:motion(f,0)}}/>
    <RevealText size={119} start={8} style={{position:'absolute',left:0,right:0,top:302,textAlign:'center'}}>A little practice.<br/>A brighter <span style={{color:C.mint}}>future.</span></RevealText>
    <div style={{position:'absolute',left:0,right:0,top:707,display:'flex',alignItems:'center',justifyContent:'center',gap:35,fontSize:76,fontWeight:700,letterSpacing:-3,opacity:motion(f,35),translate:`0 ${(1-motion(f,35))*25}px`,color:C.mint}}>MyTZStudies.com <Arrow size={76} color={C.mint}/></div>
    <div style={{position:'absolute',left:490,right:490,top:811,height:2,background:C.mint,scale:`${interpolate(f,[49,79],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})} 1`}}/>
    <div style={{position:'absolute',left:0,right:0,top:868,textAlign:'center',fontSize:31,color:'#deeee4',opacity:motion(f,55)}}>Explore the free library.</div>
  </Stage>;
};
