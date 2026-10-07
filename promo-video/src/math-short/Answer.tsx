import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {C} from '../design';
import {Cue, Equation, Garden, GOLD, Headline, MathFrame, tween} from './layout';

export const MathAnswer = () => {
  const f = useCurrentFrame();
  return <MathFrame step={6} label={f < 101 ? 'FINAL ANSWER' : 'CHECK BOTH CONDITIONS'}>
    <Headline><span style={{color: C.mint}}>{f < 101 ? 'Solved.' : 'Does it fit?'}</span><br/>{f < 101 ? 'Now check it.' : 'Yes. Both ways.'}</Headline>
    <Garden top={711} length="19 m" width="9 m" answer/>
    <div style={{position: 'absolute', left: 88, top: 1180, width: 810, textAlign: 'center', fontFamily: 'Manrope', fontSize: 110, fontWeight: 800, letterSpacing: -4, color: GOLD, opacity: tween(f, 1, 7), scale: interpolate(f, [0, 9, 17], [.91, 1.035, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(.2, .8, .2, 1)}), display: f < 101 ? 'block' : 'none'}}>19 m × 9 m</div>
    {f >= 101 && <>
      <Equation top={1200} size={72} start={101}><span style={{color: C.mint}}>✓</span> 2(19 + 9) = <span style={{color: GOLD}}>56 m</span></Equation>
      <Equation top={1343} size={74} start={154}><span style={{color: C.mint}}>✓</span> 19 × 9 = <span style={{color: GOLD}}>171 m²</span></Equation>
    </>}
    <Cue>{f < 101 ? <>Both roots describe<br/>the <b>same pair of dimensions.</b></> : f < 154 ? <>The perimeter is exactly <b>56 m.</b></> : <>The area is exactly <b>171 m².</b><br/>Answer confirmed.</>}</Cue>
  </MathFrame>;
};
