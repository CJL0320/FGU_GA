import React from 'react';
import {Composition} from 'remotion';
import {Funnel} from './Funnel';
import {DocCard} from './DocCard';
import {Cube3D} from './Cube3D';
import {Phone3D} from './Phone3D';
import {BrandBadge} from './BrandBadge';
import {EndCard} from './EndCard';
import {TipReel} from './TipReel';
import {Dress3D} from './Dress3D';
import {PhoneSplit, GlassCard, SearchBar, CtaPills} from './RefStyle';

// B-roll clips: 540x960 (upscaled to 1080x1920 by edit_reel.py), 30 fps. End card: full 1080x1920. Brand palette C.
export const Root: React.FC = () => (
  <>
    <Composition id="Funnel" component={Funnel} durationInFrames={66} fps={30} width={540} height={960}
      defaultProps={{title: 'طريق البيع'}} />
    <Composition id="DocCard" component={DocCard} durationInFrames={60} fps={30} width={540} height={960}
      defaultProps={{text: 'اعرف وين تشري', kicker: 'E-COMMERCE • DZ'}} />
    <Composition id="Cube3D" component={Cube3D} durationInFrames={60} fps={30} width={540} height={960}
      defaultProps={{title: 'PRODUIT', sub: 'المنتوج في يدك'}} />
    <Composition id="Dress3D" component={Dress3D} durationInFrames={60} fps={30} width={540} height={960}
      defaultProps={{title: 'الموديل', sub: ''}} />
    <Composition id="Phone3D" component={Phone3D} durationInFrames={60} fps={30} width={540} height={960} />
    <Composition id="BrandBadge" component={BrandBadge} durationInFrames={120} fps={30} width={540} height={170}
      defaultProps={{handle: '@kabli_ms', tag: 'E-COMMERCE • SPONSOR'}} />
    <Composition id="EndCard" component={EndCard} durationInFrames={90} fps={30} width={1080} height={1920}
      defaultProps={{handle: '@kabli_ms', whatsapp: '0550 20 54 64', cta: 'راسلني على واتساب', tag: 'E-COMMERCE • SPONSOR • META ADS'}} />
    <Composition id="TipReel" component={TipReel} durationInFrames={765} fps={30} width={1080} height={1920}
      calculateMetadata={({props}) => ({durationInFrames: props.scenes.reduce((a: number, s: {d: number}) => a + s.d, 0)})}
      defaultProps={{scenes: [{d: 90, title: 'TEST', sub: 'test'}]}} />
    {/* "Reference reel" look: duration passed with --frames / calculateMetadata props.d (frames) */}
    <Composition id="PhoneSplit" component={PhoneSplit} durationInFrames={75} fps={30} width={1080} height={1920}
      calculateMetadata={({props}) => ({durationInFrames: props.d ?? 75})}
      defaultProps={{pip: 'ref/pip.mp4', phone: 'ref/phone.mp4', label: 'الموديل', d: 75}} />
    <Composition id="GlassCard" component={GlassCard} durationInFrames={60} fps={30} width={1080} height={1920}
      calculateMetadata={({props}) => ({durationInFrames: props.d ?? 60})}
      defaultProps={{title: 'COMMANDES', value: 80, sub: 'في نهار', x: 600, y: 700, d: 60}} />
    <Composition id="SearchBar" component={SearchBar} durationInFrames={75} fps={30} width={1080} height={1920}
      calculateMetadata={({props}) => ({durationInFrames: props.d ?? 75})}
      defaultProps={{text: 'المشكلة ماشي في الموديل…', y: 1250, d: 75}} />
    <Composition id="CtaPills" component={CtaPills} durationInFrames={90} fps={30} width={1080} height={1920}
      calculateMetadata={({props}) => ({durationInFrames: props.d ?? 90})}
      defaultProps={{items: ['WhatsApp', 'Instagram', 'Partage'], y: 1300, d: 90}} />
  </>
);
