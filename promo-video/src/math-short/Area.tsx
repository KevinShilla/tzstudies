import {useCurrentFrame} from 'remotion';
import {C} from '../design';
import {Cue, Equation, Garden, GOLD, Headline, MathFrame, tween} from './layout';

export const MathArea = () => {
  const f = useCurrentFrame();
  return <MathFrame step={2} label="USE THE AREA">
    <Headline>One variable.<br/><span style={{color: C.mint}}>Two dimensions.</span></Headline>
    <div style={{position: 'absolute', left: 88, top: 620, width: 810, fontSize: 44, fontWeight: 600, color: C.mint}}>Let W = x. Since L + W = 28…</div>
    <Garden top={760} length="(28 − x) m" width="x m"/>
    <Equation top={1253} size={88} start={68} color={GOLD} underline>x(28 − x) = 171</Equation>
    <Cue>{f < 68 ? <>Width is <b>x</b>.<br/>Length is <b>28 − x</b>.</> : <>Area = length × width.<br/>That gives our equation.</>}</Cue>
    <div style={{position: 'absolute', left: 88, top: 1386, width: 810, textAlign: 'center', fontSize: 30, fontWeight: 600, color: C.mint, opacity: tween(f, 83)}}>All lengths are in metres.</div>
  </MathFrame>;
};
