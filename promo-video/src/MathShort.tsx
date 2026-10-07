import {Sequence, staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import {MathQuestion} from './math-short/Question';
import {MathPerimeter} from './math-short/Perimeter';
import {MathArea} from './math-short/Area';
import {MathRearrange} from './math-short/Rearrange';
import {MathFactors} from './math-short/Factors';
import {MathRoots} from './math-short/Roots';
import {MathAnswer} from './math-short/Answer';
import {MathCTA} from './math-short/CTA';

export const MathShort = () => <>
  <Audio src={staticFile('audio/math-short.wav')} volume={1}/>
  <Sequence name="01 — The real garden question" durationInFrames={150}><MathQuestion/></Sequence>
  <Sequence name="02 — Halve the perimeter" from={150} durationInFrames={180}><MathPerimeter/></Sequence>
  <Sequence name="03 — Translate the area" from={330} durationInFrames={210}><MathArea/></Sequence>
  <Sequence name="04 — Expand and rearrange" from={540} durationInFrames={180}><MathRearrange/></Sequence>
  <Sequence name="05 — Find the factor pair" from={720} durationInFrames={210}><MathFactors/></Sequence>
  <Sequence name="06 — Solve both factors" from={930} durationInFrames={150}><MathRoots/></Sequence>
  <Sequence name="07 — Final answer and checks" from={1080} durationInFrames={255}><MathAnswer/></Sequence>
  <Sequence name="08 — Keep practising with TZStudies" from={1335} durationInFrames={225}><MathCTA/></Sequence>
</>;
