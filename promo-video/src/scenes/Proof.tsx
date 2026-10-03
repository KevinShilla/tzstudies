import {useCurrentFrame,interpolate} from 'remotion';
import {C,Label,RevealText,Stage,motion} from '../design';
export const Proof=()=>{
  const f=useCurrentFrame();
  return <Stage>
    <Label style={{position:'absolute',left:0,right:0,top:122,textAlign:'center'}}>A clearer place to begin</Label>
    <RevealText size={81} style={{position:'absolute',left:0,right:0,top:195,textAlign:'center'}}>Your free Tanzania exam library.</RevealText>
    <div style={{position:'absolute',left:170,top:397,width:455,opacity:motion(f,13),translate:`0 ${(1-motion(f,13))*35}px`,textAlign:'center'}}><div style={{fontFamily:'Manrope',fontSize:207,fontWeight:800,letterSpacing:-11,lineHeight:1.05}}>{Math.round(interpolate(f,[15,54],[0,60],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}</div><div style={{fontSize:35,color:C.muted,marginTop:19}}>past papers</div></div>
    <div style={{position:'absolute',left:734,top:397,width:455,opacity:motion(f,26),translate:`0 ${(1-motion(f,26))*35}px`,textAlign:'center'}}><div style={{fontFamily:'Manrope',fontSize:207,fontWeight:800,letterSpacing:-11,lineHeight:1.05,color:C.green}}>{Math.round(interpolate(f,[28,67],[0,60],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}</div><div style={{fontSize:35,color:C.muted,marginTop:19}}>worked answer keys</div></div>
    <div style={{position:'absolute',left:1296,top:397,width:455,opacity:motion(f,39),translate:`0 ${(1-motion(f,39))*35}px`,textAlign:'center'}}><div style={{fontFamily:'Manrope',fontSize:207,fontWeight:800,letterSpacing:-11,lineHeight:1.05}}>{Math.round(interpolate(f,[41,80],[0,4],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}</div><div style={{fontSize:35,color:C.muted,marginTop:19}}>school levels</div></div>
    <div style={{position:'absolute',left:200,right:200,top:821,height:1,background:'#bed1bf',scale:`${motion(f,50)} 1`}}/>
    <div style={{position:'absolute',left:0,right:0,top:878,textAlign:'center',fontSize:30,color:C.green,opacity:motion(f,70)}}>Standard 4 &nbsp; · &nbsp; Standard 7 &nbsp; · &nbsp; Form 2 &nbsp; · &nbsp; Form 4</div>
  </Stage>;
};
