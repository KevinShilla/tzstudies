import {Composition,Folder} from 'remotion';
import {Launch} from './Launch';
import {Social} from './Social';
import {Hook} from './scenes/Hook';
import {Problem} from './scenes/Problem';
import {Reveal} from './scenes/Reveal';
import {Browse} from './scenes/Browse';
import {Answers} from './scenes/Answers';
import {Mobile} from './scenes/Mobile';
import {Tutors} from './scenes/Tutors';
import {Proof} from './scenes/Proof';
import {CTA} from './scenes/CTA';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="TZStudiesLaunch" component={Launch} durationInFrames={2160} fps={30} width={1920} height={1080}/>
      <Composition id="TZStudiesSocial" component={Social} durationInFrames={780} fps={30} width={1080} height={1920}/>
      <Folder name="Editable-scenes">
        <Composition id="Hook" component={Hook} durationInFrames={196} fps={30} width={1920} height={1080}/>
        <Composition id="Problem" component={Problem} durationInFrames={131} fps={30} width={1920} height={1080}/>
        <Composition id="BrandReveal" component={Reveal} durationInFrames={197} fps={30} width={1920} height={1080}/>
        <Composition id="BrowsePapers" component={Browse} durationInFrames={393} fps={30} width={1920} height={1080}/>
        <Composition id="WorkedAnswers" component={Answers} durationInFrames={393} fps={30} width={1920} height={1080}/>
        <Composition id="StudyAnywhere" component={Mobile} durationInFrames={262} fps={30} width={1920} height={1080}/>
        <Composition id="FindTutors" component={Tutors} durationInFrames={262} fps={30} width={1920} height={1080}/>
        <Composition id="LibraryProof" component={Proof} durationInFrames={131} fps={30} width={1920} height={1080}/>
        <Composition id="CallToAction" component={CTA} durationInFrames={195} fps={30} width={1920} height={1080}/>
      </Folder>
    </>
  );
};
