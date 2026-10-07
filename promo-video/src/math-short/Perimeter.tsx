import {useCurrentFrame} from 'remotion';
import {C} from '../design';
import {Cue, Equation, Garden, GOLD, Headline, MathFrame} from './layout';

export const MathPerimeter = () => {
  const f = useCurrentFrame();
  return <MathFrame step={1} label="HALVE THE PERIMETER" dark={false}>
    <Headline>Two lengths.<br/>Two widths.</Headline>
    <Garden top={660} dark={false} perimeter/>
    <Equation top={1152} size={84}>2(L + W) = 56</Equation>
    <Equation top={1310} size={94} start={66} color={C.green} underline>L + W = 28</Equation>
    <Cue dark={false}>{f < 66 ? <>Perimeter means <span style={{background: GOLD}}>all four sides.</span></> : <>Divide both sides by 2.<br/>The two dimensions add to <b>28.</b></>}</Cue>
  </MathFrame>;
};
