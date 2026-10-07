import {Composition,Folder} from 'remotion';
import {Launch} from './Launch';
import {Social} from './Social';
import {MathShort} from './MathShort';
import {MathQuestion} from './math-short/Question';
import {MathPerimeter} from './math-short/Perimeter';
import {MathArea} from './math-short/Area';
import {MathRearrange} from './math-short/Rearrange';
import {MathFactors} from './math-short/Factors';
import {MathRoots} from './math-short/Roots';
import {MathAnswer} from './math-short/Answer';
import {MathCTA} from './math-short/CTA';
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
      <Composition id="TZStudiesMathShort" component={MathShort} durationInFrames={1560} fps={30} width={1080} height={1920}/>
      <Folder name="Math-short-scenes">
        <Composition id="MathQuestion" component={MathQuestion} durationInFrames={150} fps={30} width={1080} height={1920}/>
        <Composition id="MathPerimeter" component={MathPerimeter} durationInFrames={180} fps={30} width={1080} height={1920}/>
        <Composition id="MathArea" component={MathArea} durationInFrames={210} fps={30} width={1080} height={1920}/>
        <Composition id="MathRearrange" component={MathRearrange} durationInFrames={180} fps={30} width={1080} height={1920}/>
        <Composition id="MathFactors" component={MathFactors} durationInFrames={210} fps={30} width={1080} height={1920}/>
        <Composition id="MathRoots" component={MathRoots} durationInFrames={150} fps={30} width={1080} height={1920}/>
        <Composition id="MathAnswer" component={MathAnswer} durationInFrames={255} fps={30} width={1080} height={1920}/>
        <Composition id="MathShortCTA" component={MathCTA} durationInFrames={225} fps={30} width={1080} height={1920}/>
      </Folder>
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
