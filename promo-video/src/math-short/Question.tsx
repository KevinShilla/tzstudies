import {interpolate, useCurrentFrame} from 'remotion';
import {C} from '../design';
import {Cue, Garden, GOLD, Headline, MathFrame} from './layout';

export const MathQuestion = () => {
  const f = useCurrentFrame();
  return <MathFrame step={0} label="REAL EXAM · CSEE 2024 · Q10(b)">
    <Headline>Can you solve<br/>this <span style={{color: GOLD}}>FAST?</span></Headline>
    <div style={{position: 'absolute', left: 88, top: 628, width: 810, fontSize: 49, fontWeight: 700, color: C.mint}}>A rectangular garden. Two clues.</div>
    <Garden top={772} length="? m" width="? m" perimeter start={-20}/>
    <div style={{position: 'absolute', left: 88, top: 1280, width: 810, textAlign: 'center', fontFamily: 'Manrope', fontSize: 59, fontWeight: 800}}>Find its length and width.</div>
    <Cue start={-10}><span style={{color: GOLD}}>56 m</span> of fence. <span style={{color: GOLD}}>171 m²</span> of area.</Cue>
    <div style={{position: 'absolute', left: 88, top: 1720, width: 810, height: 6, background: '#ffffff15'}}><div style={{width: `${interpolate(f, [0, 149], [0, 100], {extrapolateRight: 'clamp'})}%`, height: 6, background: GOLD}}/></div>
  </MathFrame>;
};
