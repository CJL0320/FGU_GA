import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, Fonts, NavyBg} from './brand';

// Faceless motion-graphics reel (1080x1920) in palette C: kinetic typography scenes + neon glass icons.
// Each scene: optional kicker, big neon title (gradient), white sub line, optional icon. Text is Darija / French.
export type Scene = {d: number; kicker?: string; title: string; sub?: string; icon?: string; big?: boolean};

const grad = 'linear-gradient(180deg, #BAE6FD 0%, #38BDF8 45%, #8B5CF6 100%)';
const ar = (t: string) => /[؀-ۿ]/.test(t);

const SceneView: React.FC<{s: Scene}> = ({s}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = (start: number) => spring({frame: f - start, fps, config: {damping: 13, stiffness: 130}});
  const out = interpolate(f, [s.d - 6, s.d], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const k1 = k(0), k2 = k(6), k3 = k(12);
  const words = s.title.split(' ');
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: out, padding: 90, boxSizing: 'border-box'}}>
      {s.icon && (
        <div style={{transform: `scale(${k1}) rotate(${(1 - k1) * -20}deg) translateY(${Math.sin(f / 9) * 8}px)`, marginBottom: 10}}>
          <Img src={staticFile(`ic_${s.icon}.png`)} style={{width: 470, height: 470}} />
        </div>
      )}
      {s.kicker && (
        <div style={{fontFamily: 'Sora', fontSize: 44, letterSpacing: 6, color: C.lav, opacity: k1, marginBottom: 24,
          transform: `translateY(${(1 - k1) * 30}px)`, direction: ar(s.kicker) ? 'rtl' : 'ltr'}}>{s.kicker}</div>
      )}
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 28px', direction: ar(s.title) ? 'rtl' : 'ltr',
        filter: 'drop-shadow(0 0 26px rgba(139,92,246,0.85))'}}>
        {words.map((w, i) => {
          const kw = k(3 + i * 4);
          return (
            <span key={i} style={{fontFamily: ar(w) ? 'Readex' : 'Sora', fontSize: s.big ? 150 : 118, lineHeight: 1.25,
              background: grad, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
              display: 'inline-block', transform: `translateY(${(1 - kw) * 70}px) scale(${0.7 + 0.3 * kw})`, opacity: kw}}>{w}</span>
          );
        })}
      </div>
      {s.sub && (
        <div style={{marginTop: 40, fontFamily: ar(s.sub) ? 'Readex' : 'Sora', fontSize: 58, color: C.white, textAlign: 'center',
          direction: ar(s.sub) ? 'rtl' : 'ltr', opacity: k3, transform: `translateY(${(1 - k3) * 40}px)`,
          padding: '18px 36px', borderRadius: 30, border: '3px solid transparent',
          background: `linear-gradient(rgba(42,27,94,0.85), rgba(28,18,69,0.85)) padding-box, linear-gradient(90deg, ${C.violet}, ${C.blue}) border-box`}}>{s.sub}</div>
      )}
      <div style={{position: 'absolute', bottom: 260, width: 260 * k2, height: 8, borderRadius: 4, background: `linear-gradient(90deg, ${C.violet}, ${C.blue})`}} />
    </AbsoluteFill>
  );
};

export const TipReel: React.FC<{scenes: Scene[]}> = ({scenes}) => {
  const f = useCurrentFrame(); const {durationInFrames} = useVideoConfig();
  let at = 0;
  return (
    <AbsoluteFill>
      <Fonts /><NavyBg />
      {scenes.map((s, i) => {
        const from = at; at += s.d;
        return <Sequence key={i} from={from} durationInFrames={s.d}><SceneView s={s} /></Sequence>;
      })}
      {/* top-left handle + progress bar */}
      <div style={{position: 'absolute', top: 70, left: 60, display: 'flex', alignItems: 'center', gap: 18}}>
        <Img src={staticFile('logo_icon.png')} style={{width: 96, height: 96}} />
        <div style={{fontFamily: 'Sora', fontSize: 40, color: C.white}}>@kabli_ms</div>
      </div>
      <div style={{position: 'absolute', top: 0, left: 0, height: 12, width: `${(f / durationInFrames) * 100}%`, background: C.blue}} />
    </AbsoluteFill>
  );
};
