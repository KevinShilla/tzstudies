import {CanvasImage,Sequence,interpolate,staticFile,useCurrentFrame} from 'remotion';
import {Audio} from '@remotion/media';
import {Arrow,C,Label,Phone,RevealText,Stage,Wordmark,motion} from './design';

const SocialHook=()=>{
  const f=useCurrentFrame();
  return <Stage dark>
    <Wordmark dark size={56} style={{position:'absolute',left:95,top:175,opacity:motion(f,0)}}/>
    <Label dark style={{position:'absolute',left:101,top:404,fontSize:25}}>Your next chapter</Label>
    <RevealText size={140} start={1} style={{position:'absolute',left:89,top:532}}>Next exam?</RevealText>
    <RevealText size={142} start={26} style={{position:'absolute',left:89,top:744,color:C.mint}}>Start ready.</RevealText>
    <div style={{position:'absolute',left:100,top:1057,fontSize:36,color:'#d9eadf',opacity:motion(f,44)}}>A little practice goes a long way.</div>
    <Phone image="mobile-home" width={410} style={{left:546,top:1260,rotate:'-12deg',translate:`0 ${240*(1-motion(f,28,40))}px`,opacity:.4}}/>
  </Stage>;
};
const SocialBrowse=()=>{
  const f=useCurrentFrame();
  return <Stage>
    <Label style={{position:'absolute',left:98,top:166,fontSize:24}}>Past papers, one place</Label>
    <RevealText size={118} style={{position:'absolute',left:89,top:245}}>Find your<br/>next paper.</RevealText>
    <Phone video="mobile" trim={55} width={470} style={{left:310,top:649,rotate:'-3deg',translate:`0 ${70*(1-motion(f,0))}px`,scale:String(1+f*.00012)}}/>
    <div style={{position:'absolute',left:100,top:1586,fontSize:37,lineHeight:1.5,background:C.paper,padding:'18px 20px',color:C.green,opacity:motion(f,70)}}>Your level. Your subject.<br/>Your year.</div>
  </Stage>;
};
const SocialAnswers=()=>{
  const f=useCurrentFrame();
  return <Stage dark>
    <Label dark style={{position:'absolute',left:100,top:164,fontSize:25}}>Worked answer keys</Label>
    <RevealText size={113} style={{position:'absolute',left:90,top:267}}>Understand.<br/><span style={{color:C.mint}}>Step by step.</span></RevealText>
    <div style={{position:'absolute',left:90,top:716,width:900,height:404,borderRadius:21,overflow:'hidden',background:'#fff',opacity:motion(f,25),translate:`0 ${40*(1-motion(f,25))}px`,scale:String(1+f*.0001)}}><CanvasImage src={staticFile('captures/answer-question.png')} style={{position:'absolute',width:900,height:318,top:43,left:0}}/></div>
    <RevealText size={91} start={85} style={{position:'absolute',left:92,top:1260,color:C.mint}}>A clear final answer.</RevealText>
    <div style={{position:'absolute',left:100,top:1550,fontSize:32,lineHeight:1.55,color:'#d6eade',opacity:motion(f,105)}}>Free with your<br/>MyTZStudies account.</div>
  </Stage>;
};
const SocialProof=()=>{
  const f=useCurrentFrame();
  return <Stage>
    <Wordmark size={50} style={{position:'absolute',left:99,top:170}}/>
    <RevealText size={102} style={{position:'absolute',left:89,top:329}}>Your free<br/>Tanzania<br/>exam library.</RevealText>
    <div style={{position:'absolute',left:95,top:872,display:'flex',alignItems:'baseline',gap:36,opacity:motion(f,30)}}><div style={{fontSize:170,fontFamily:'Manrope',fontWeight:800,letterSpacing:-7}}>{Math.round(interpolate(f,[30,63],[0,60],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}</div><div style={{fontSize:47,color:C.muted}}>past papers</div></div>
    <div style={{position:'absolute',left:95,top:1152,display:'flex',alignItems:'baseline',gap:36,opacity:motion(f,52)}}><div style={{fontSize:170,fontFamily:'Manrope',fontWeight:800,letterSpacing:-7,color:C.green}}>{Math.round(interpolate(f,[52,85],[0,60],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}</div><div style={{fontSize:47,color:C.muted}}>answer keys</div></div>
    <div style={{position:'absolute',left:101,top:1510,fontSize:38,color:C.green,opacity:motion(f,79)}}>Four school levels. One place.</div>
  </Stage>;
};
const SocialCTA=()=>{
  const f=useCurrentFrame();
  return <Stage dark>
    <Wordmark dark size={67} style={{position:'absolute',left:0,right:0,top:270,textAlign:'center',opacity:motion(f,0)}}/>
    <RevealText size={130} start={8} style={{position:'absolute',left:0,right:0,top:608,textAlign:'center'}}>Start your<br/>next chapter.</RevealText>
    <div style={{position:'absolute',left:0,right:0,top:1116,textAlign:'center',fontSize:65,fontWeight:700,letterSpacing:-2,color:C.mint,opacity:motion(f,30)}}>MyTZStudies.com</div>
    <div style={{position:'absolute',left:139,right:139,top:1250,borderRadius:80,background:C.mint,padding:'26px 30px',display:'flex',alignItems:'center',justifyContent:'center',gap:20,fontSize:32,fontWeight:700,color:C.ink,opacity:motion(f,48),translate:`0 ${(1-motion(f,48))*22}px`}}>Explore the free library <Arrow size={45}/></div>
  </Stage>;
};
export const Social=()=> <>
  <Audio src={staticFile('audio/social.wav')} volume={1}/>
  <Sequence durationInFrames={90} name="01 — Start ready"><SocialHook/></Sequence>
  <Sequence from={90} durationInFrames={180} name="02 — Find your paper"><SocialBrowse/></Sequence>
  <Sequence from={270} durationInFrames={180} name="03 — Understand the answer"><SocialAnswers/></Sequence>
  <Sequence from={450} durationInFrames={150} name="04 — The real library"><SocialProof/></Sequence>
  <Sequence from={600} durationInFrames={180} name="05 — Visit MyTZStudies"><SocialCTA/></Sequence>
</>;
