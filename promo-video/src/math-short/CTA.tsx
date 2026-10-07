import {interpolate, useCurrentFrame} from 'remotion';
import {C} from '../design';
import {GOLD, MathFrame, tween} from './layout';

export const MathCTA = () => {
  const f = useCurrentFrame();
  return <MathFrame step={7} label="KEEP THE PRACTICE GOING">
    <div style={{position: 'absolute', left: 88, top: 384, width: 810, fontFamily: 'Manrope', fontSize: 91, fontWeight: 800, letterSpacing: -4, lineHeight: 1.13}}>Need more<br/>exam practice?</div>
    <div style={{position: 'absolute', left: 88, top: 660, width: 810, fontSize: 56, lineHeight: 1.28, fontWeight: 600, opacity: tween(f, 12)}}>Study smarter<br/>with <span style={{color: C.mint, fontWeight: 800}}>TZStudies.</span></div>
    <div style={{position: 'absolute', left: 88, top: 958, width: 810, padding: '34px 18px', boxSizing: 'border-box', borderRadius: 22, background: C.mint, textAlign: 'center', fontFamily: 'Manrope', fontSize: 78, letterSpacing: -3.4, fontWeight: 800, color: C.ink, scale: interpolate(f, [0, 15], [.97, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>mytzstudies.com</div>
    <div style={{position: 'absolute', left: 88, top: 1162, width: 810, fontSize: 45, fontWeight: 600, opacity: tween(f, 31)}}>Practice more exam questions. <span style={{color: GOLD}}>↗</span></div>
    <div style={{position: 'absolute', left: 88, top: 1368, width: 810, fontFamily: 'Manrope', fontSize: 64, fontWeight: 800, lineHeight: 1.24, letterSpacing: -2, opacity: tween(f, 69), translate: `0 ${18 * (1 - tween(f, 69))}px`}}>More questions.<br/>More practice.<br/><span style={{color: GOLD}}>Better results.</span></div>
  </MathFrame>;
};
