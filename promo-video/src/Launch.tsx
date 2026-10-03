import {Sequence,staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import {Hook} from './scenes/Hook';
import {Problem} from './scenes/Problem';
import {Reveal} from './scenes/Reveal';
import {Browse} from './scenes/Browse';
import {Answers} from './scenes/Answers';
import {Mobile} from './scenes/Mobile';
import {Tutors} from './scenes/Tutors';
import {Proof} from './scenes/Proof';
import {CTA} from './scenes/CTA';
export const Launch=()=> <>
  <Audio src={staticFile('audio/main.wav')} volume={1}/>
  <Sequence durationInFrames={196} name="01 — Start ready"><Hook/></Sequence>
  <Sequence from={196} durationInFrames={131} name="02 — Less searching"><Problem/></Sequence>
  <Sequence from={327} durationInFrames={197} name="03 — Meet MyTZStudies"><Reveal/></Sequence>
  <Sequence from={524} durationInFrames={393} name="04 — Find your paper"><Browse/></Sequence>
  <Sequence from={917} durationInFrames={393} name="05 — Understand the working"><Answers/></Sequence>
  <Sequence from={1310} durationInFrames={262} name="06 — Your pace, your place"><Mobile/></Sequence>
  <Sequence from={1572} durationInFrames={262} name="07 — Find support"><Tutors/></Sequence>
  <Sequence from={1834} durationInFrames={131} name="08 — The real library"><Proof/></Sequence>
  <Sequence from={1965} durationInFrames={195} name="09 — Your next chapter"><CTA/></Sequence>
</>;
