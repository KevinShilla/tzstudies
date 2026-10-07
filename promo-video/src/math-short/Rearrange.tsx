import {useCurrentFrame} from 'remotion';
import {C} from '../design';
import {Cue, DownArrow, Equation, GOLD, Headline, MathFrame} from './layout';

export const MathRearrange = () => {
  const f = useCurrentFrame();
  return <MathFrame step={3} label="EXPAND & REARRANGE" dark={false}>
    <Headline>Make it<br/>a quadratic.</Headline>
    <Equation top={746} size={80}>x(28 − x) = 171</Equation>
    <DownArrow top={874} dark={false} start={18}/>
    <Equation top={985} size={88} start={28}>28x − x² = 171</Equation>
    <DownArrow top={1135} dark={false} start={76}/>
    <Equation top={1265} size={77} start={91} color={C.green} underline>x² − 28x + 171 = 0</Equation>
    <Cue dark={false}>{f < 76 ? <>Multiply <span style={{background: GOLD}}>x into both terms.</span></> : <>Move terms, then multiply by −1.<br/>Now we can factorise.</>}</Cue>
  </MathFrame>;
};
