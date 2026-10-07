import {useCurrentFrame} from 'remotion';
import {C} from '../design';
import {Cue, DownArrow, Equation, GOLD, Headline, MathFrame, tween} from './layout';

export const MathRoots = () => {
  const f = useCurrentFrame();
  return <MathFrame step={5} label="SET EACH FACTOR TO ZERO" dark={false}>
    <Headline>Factorise.<br/>Then solve.</Headline>
    <Equation top={725} size={78} color={C.green} underline>(x − 9)(x − 19) = 0</Equation>
    <DownArrow top={919} dark={false} start={25}/>
    <div style={{position: 'absolute', left: 88, top: 1065, width: 810, display: 'flex', gap: 28}}>
      <div style={{width: 391, borderTop: '4px solid #278365', paddingTop: 38, textAlign: 'center', opacity: tween(f, 41)}}><div style={{fontSize: 51, fontWeight: 600}}>x − 9 = 0</div><div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 101, marginTop: 26, color: C.green}}>x = 9</div></div>
      <div style={{width: 391, borderTop: '4px solid #278365', paddingTop: 38, textAlign: 'center', opacity: tween(f, 66)}}><div style={{fontSize: 51, fontWeight: 600}}>x − 19 = 0</div><div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 99, marginTop: 26, color: C.green}}>x = 19</div></div>
    </div>
    <Cue dark={false}>{f < 90 ? <>A product is zero when<br/><span style={{background: GOLD}}>at least one factor is zero.</span></> : <>The sides are <b>9 m</b> and <b>19 m.</b><br/>Swapping them gives the same garden.</>}</Cue>
  </MathFrame>;
};
