import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {C} from '../design';

export const GOLD = '#ffd46b';
export const tween = (frame: number, start = 0, duration = 15) =>
  interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(.16, 1, .3, 1),
  });

export const MathFrame: React.FC<{
  children: React.ReactNode; dark?: boolean; step: number; label: string;
}> = ({children, dark = true, step, label}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: dark ? C.ink : C.paper, color: dark ? C.white : C.ink, fontFamily: 'DM Sans', overflow: 'hidden'}}>
    <AbsoluteFill style={{backgroundImage: `radial-gradient(${dark ? '#b9f2d52a' : '#2783651a'} 1.4px, transparent 1.4px)`, backgroundSize: '48px 48px', opacity: .5}}/>
    <div style={{position: 'absolute', width: 980, height: 980, border: `1px solid ${dark ? '#b9f2d51a' : '#2783651a'}`, borderRadius: '50%', left: 190, top: -510, rotate: `${f / 25}deg`}}/>
    <div style={{position: 'absolute', left: 88, top: 140, width: 810, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
      <div style={{fontFamily: 'Manrope', fontSize: 38, fontWeight: 800, letterSpacing: -1.5}}>TZ<span style={{color: dark ? C.mint : C.green}}>Studies</span></div>
      <div style={{fontSize: 25, fontWeight: 700, letterSpacing: 2, color: dark ? C.mint : C.green}}>MATH IN A MINUTE</div>
    </div>
    <div style={{position: 'absolute', left: 88, top: 226, display: 'flex', alignItems: 'center', gap: 18, fontSize: 28, fontWeight: 700, color: dark ? C.mint : C.green}}>
      <span style={{background: dark ? C.mint : C.ink, color: dark ? C.ink : C.white, borderRadius: 10, padding: '8px 12px', fontVariantNumeric: 'tabular-nums'}}>{String(step).padStart(2, '0')}</span>
      <span style={{letterSpacing: 2.2}}>{label}</span>
    </div>
    {children}
    <div style={{position: 'absolute', left: 88, top: 1648, width: 810, height: 5, background: dark ? '#ffffff19' : '#123c3b17', borderRadius: 5}}>
      <div style={{width: `${Math.min(step / 7, 1) * 100}%`, height: 5, background: dark ? C.mint : C.green, borderRadius: 5}}/>
    </div>
  </AbsoluteFill>;
};

export const Headline: React.FC<{children: React.ReactNode; size?: number}> = ({children, size = 94}) =>
  <div style={{position: 'absolute', left: 88, top: 338, width: 810, fontFamily: 'Manrope', fontSize: size, fontWeight: 800, letterSpacing: -4, lineHeight: 1.12}}>{children}</div>;

export const Cue: React.FC<{children: React.ReactNode; dark?: boolean; start?: number}> = ({children, dark = true, start = 0}) => {
  const f = useCurrentFrame();
  return <div style={{position: 'absolute', left: 88, top: 1470, width: 810, fontSize: 47, fontWeight: 600, lineHeight: 1.35, color: dark ? '#e1f1e8' : C.ink, opacity: tween(f, start, 10), translate: `0 ${interpolate(f, [start, start + 14], [14, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}px`}}>{children}</div>;
};

export const Equation: React.FC<{
  children: React.ReactNode; top: number; size?: number; start?: number; color?: string; underline?: boolean;
}> = ({children, top, size = 94, start = 0, color, underline = false}) => {
  const f = useCurrentFrame();
  return <div style={{position: 'absolute', left: 88, top, width: 810, fontFamily: 'Manrope', fontSize: size, lineHeight: 1.25, fontWeight: 800, letterSpacing: -3, textAlign: 'center', color, opacity: tween(f, start, 10), translate: `0 ${interpolate(f, [start, start + 17], [24, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(.16, 1, .3, 1)})}px`}}>
    {children}
    {underline && <svg width="720" height="20" viewBox="0 0 720 20" style={{display: 'block', margin: '12px auto 0'}}><path d="M15 13 Q 350 1 705 10" fill="none" stroke={color || GOLD} strokeWidth="7" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - tween(f, start + 12, 22)}/></svg>}
  </div>;
};

export const DownArrow: React.FC<{top: number; start?: number; dark?: boolean}> = ({top, start = 0, dark = true}) => {
  const f = useCurrentFrame();
  return <svg width="52" height="68" viewBox="0 0 52 68" style={{position: 'absolute', left: 467, top, opacity: tween(f, start, 10), translate: `0 ${8 * (1 - tween(f, start, 15))}px`}} fill="none"><path d="M26 7v48M10 39l16 17 16-17" stroke={dark ? C.mint : C.green} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
};

export const Garden: React.FC<{
  top?: number; length?: string; width?: string; dark?: boolean; start?: number; perimeter?: boolean; answer?: boolean;
}> = ({top = 650, length = 'L', width = 'W', dark = true, start = 0, perimeter = false, answer = false}) => {
  const f = useCurrentFrame();
  const ink = dark ? C.white : C.ink;
  const accent = dark ? C.mint : C.green;
  return <svg width="810" height="480" viewBox="0 0 810 480" style={{position: 'absolute', left: 88, top, opacity: tween(f, start, 10)}}>
    <defs><pattern id="garden-hatch" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M10 19l4-7 4 7M14 12v12" stroke={accent} opacity=".18" fill="none" strokeWidth="2"/></pattern></defs>
    <rect x="90" y="140" width="540" height="280" rx="12" fill={dark ? '#21564f' : '#daeada'}/>
    <rect x="90" y="140" width="540" height="280" rx="12" fill="url(#garden-hatch)"/>
    <rect x="90" y="140" width="540" height="280" rx="12" fill="none" stroke={perimeter ? GOLD : accent} strokeWidth="7" pathLength="1" strokeDasharray={perimeter ? '1' : undefined} strokeDashoffset={perimeter ? 1 - tween(f, start + 8, 40) : undefined}/>
    <path d="M90 108v-17h540v17M656 140h17v280h-17" fill="none" stroke={accent} strokeWidth="3"/>
    <text x="360" y="70" fill={answer ? (dark ? GOLD : C.green) : ink} textAnchor="middle" fontFamily="Manrope" fontWeight="800" fontSize={answer ? 76 : 60}>{length}</text>
    <text x="725" y="296" fill={answer ? (dark ? GOLD : C.green) : ink} textAnchor="middle" fontFamily="Manrope" fontWeight="800" fontSize={answer ? 62 : 53}>{width}</text>
    <text x="360" y="283" fill={ink} textAnchor="middle" fontFamily="Manrope" fontWeight="800" fontSize="78">171 m²</text>
    <text x="360" y="341" fill={accent} textAnchor="middle" fontFamily="DM Sans" fontSize="32" fontWeight="600">GARDEN AREA</text>
    {perimeter && <text x="360" y="461" textAnchor="middle" fill={dark ? GOLD : C.green} fontFamily="DM Sans" fontWeight="700" fontSize="44">All four sides = 56 m</text>}
  </svg>;
};
