import {interpolate, useCurrentFrame} from 'remotion';
import {C} from '../design';
import {Cue, Equation, GOLD, Headline, MathFrame, tween} from './layout';

export const MathFactors = () => {
  const f = useCurrentFrame();
  return <MathFrame step={4} label="FIND THE FACTOR PAIR">
    <Headline>Here’s the<br/><span style={{color: GOLD}}>shortcut.</span></Headline>
    <Equation top={648} size={73} color={C.mint}>x² − 28x + 171 = 0</Equation>
    <div style={{position: 'absolute', left: 118, top: 855, width: 750, height: 185, borderRadius: 100, border: '3px solid #b9f2d531', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 56, fontFamily: 'Manrope', fontSize: 110, fontWeight: 800, color: GOLD}}>
      <span style={{opacity: tween(f, 13)}}>9</span><span style={{fontSize: 56, color: C.white, opacity: tween(f, 24)}}>&</span><span style={{opacity: tween(f, 34)}}>19</span>
      <svg width="770" height="205" viewBox="0 0 770 205" style={{position: 'absolute', left: -11, top: -11}}><ellipse cx="385" cy="102" rx="376" ry="94" fill="none" stroke={GOLD} strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - interpolate(f, [43, 78], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}/></svg>
    </div>
    <Equation top={1122} size={88} start={67}><span style={{color: GOLD}}>9 × 19</span> = 171</Equation>
    <Equation top={1281} size={f < 156 ? 88 : 73} start={112}>{f < 156 ? <><span style={{color: GOLD}}>9 + 19</span> = 28</> : <><span style={{color: GOLD}}>(−9) + (−19)</span> = −28</>}</Equation>
    <Cue>{f < 112 ? <>Find two numbers that <b>multiply<br/>to 171</b>…</> : f < 156 ? <>…and <b>add to 28.</b></> : <>Their negatives add to <b>−28.</b><br/>Use two minus signs.</>}</Cue>
  </MathFrame>;
};
