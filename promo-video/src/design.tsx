import React from 'react';
import {AbsoluteFill, CanvasImage, Easing, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Video} from '@remotion/media';
import {loadFont} from '@remotion/fonts';

loadFont({family:'DM Sans',url:staticFile('fonts/DM-Sans.ttf'),weight:'100 1000'});
loadFont({family:'Manrope',url:staticFile('fonts/Manrope.ttf'),weight:'200 800'});

export const C = {ink:'#123c3b', mint:'#b9f2d5', paper:'#f1f4e9', green:'#278365', muted:'#6f8278', white:'#fcfff9'};
export const ease = Easing.bezier(.19,1,.22,1);
export const motion = (frame:number, start:number, duration=28) => interpolate(frame,[start,start+duration],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:ease});

export const Stage:React.FC<{dark?:boolean;children:React.ReactNode}> = ({dark=false,children}) => {
  const f=useCurrentFrame();
  return <AbsoluteFill style={{background:dark?C.ink:C.paper,color:dark?C.white:C.ink,fontFamily:'DM Sans',overflow:'hidden'}}>
    <AbsoluteFill style={{opacity:dark?.09:.07,backgroundImage:`radial-gradient(${dark?C.mint:C.green} 1.1px,transparent 1.1px)`,backgroundSize:'34px 34px',translate:`${Math.sin(f/110)*9}px ${Math.cos(f/140)*8}px`}}/>
    <div style={{position:'absolute',width:1100,height:1100,borderRadius:'50%',border:`1px solid ${dark?'#b9f2d52a':'#27836522'}`,right:-460,top:-360,scale:String(1+Math.sin(f/140)*.05)}}/>
    <div style={{position:'absolute',width:1400,height:1400,borderRadius:'50%',border:`1px solid ${dark?'#b9f2d516':'#27836512'}`,right:-610,top:-510}}/>
    {children}
  </AbsoluteFill>;
};

export const Wordmark:React.FC<{size?:number;dark?:boolean;style?:React.CSSProperties}> = ({size=54,dark=false,style}) =>
  <div style={{fontFamily:'Manrope',fontSize:size,fontWeight:800,letterSpacing:-size*.045,whiteSpace:'nowrap',lineHeight:1.2,color:dark?C.white:C.ink,...style}}>my<span style={{color:dark?C.mint:C.green}}>TZ</span>Studies<span style={{color:dark?C.mint:C.green}}>.</span></div>;

export const Label:React.FC<{children:React.ReactNode;dark?:boolean;style?:React.CSSProperties}> = ({children,dark=false,style}) =>
  <div style={{fontSize:23,fontWeight:600,letterSpacing:4,textTransform:'uppercase',color:dark?C.mint:C.green,...style}}>{children}</div>;

export const RevealText:React.FC<{children:React.ReactNode;start?:number;size?:number;style?:React.CSSProperties}> = ({children,start=0,size=96,style}) => {
  const f=useCurrentFrame();
  const p=motion(f,start,32);
  return <div style={{overflow:'hidden',paddingBottom:12,...style}}><div style={{fontFamily:'Manrope',fontSize:size,fontWeight:800,lineHeight:1.12,letterSpacing:-size*.055,translate:`0 ${interpolate(p,[0,1],[125,0])}%`,opacity:interpolate(f,[start,start+6],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>{children}</div></div>;
};

export const Browser:React.FC<{image?:string;video?:string;trim?:number;rate?:number;width?:number;height?:number;imageHeight?:number;offsetY?:number;url?:string;style?:React.CSSProperties}> = ({image,video,trim=0,rate=1,width=1440,height=900,imageHeight=900,offsetY=0,url='mytzstudies.com',style}) =>
  <div style={{position:'absolute',width,height,borderRadius:22,overflow:'hidden',background:'#fcfff9',boxShadow:'0 28px 70px #06262226',border:'1px solid #ffffffad',...style}}>
    <div style={{height:55,display:'flex',alignItems:'center',gap:8,padding:'0 23px',background:'#e6ebe3',borderBottom:'1px solid #d5dfd4'}}>
      <span style={{width:11,height:11,borderRadius:'50%',background:'#b9c8bb'}}/><span style={{width:11,height:11,borderRadius:'50%',background:'#b9c8bb'}}/><span style={{width:11,height:11,borderRadius:'50%',background:'#b9c8bb'}}/>
      <div style={{margin:'0 auto',height:31,width:'48%',background:'#f5f8f1',borderRadius:8,textAlign:'center',fontSize:16,lineHeight:'31px',color:C.ink,fontWeight:500}}>⌁ &nbsp; {url}</div>
      <span style={{fontSize:23,color:'#829985'}}>↗</span>
    </div>
    <div style={{position:'relative',width,height:height-55,overflow:'hidden'}}>
      {image?<CanvasImage src={staticFile('captures/'+image+'.png')} style={{position:'absolute',width,height:width*imageHeight/1440,top:offsetY,left:0}}/>:null}
      {video?<Video src={staticFile('clips/'+video+'.mp4')} trimBefore={trim} playbackRate={rate} muted style={{position:'absolute',width,height:width*900/1440,top:offsetY,left:0}}/>:null}
    </div>
  </div>;

export const Phone:React.FC<{image?:string;video?:string;trim?:number;width?:number;style?:React.CSSProperties}> = ({image,video,trim=0,width=390,style}) =>
  <div style={{position:'absolute',width:width+26,height:width*844/390+26,borderRadius:62,border:'8px solid #183e3b',padding:5,background:'#12312f',overflow:'hidden',boxShadow:'0 30px 70px #082a3433',...style}}>
    <div style={{width,height:width*844/390,borderRadius:44,overflow:'hidden',position:'relative',background:C.paper}}>
      {image?<CanvasImage src={staticFile('captures/'+image+'.png')} style={{width,height:width*844/390}}/>:null}
      {video?<Video src={staticFile('clips/'+video+'.mp4')} trimBefore={trim} muted style={{width,height:width*844/390}}/>:null}
      <div style={{position:'absolute',width:82,height:19,background:'#12312f',borderRadius:20,left:'50%',translate:'-50% 0',top:9}}/>
    </div>
  </div>;

export const Arrow:React.FC<{size?:number;color?:string}> = ({size=50,color=C.ink}) =>
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none"><path d="M8 24h30M26 12l12 12-12 12" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/></svg>;
