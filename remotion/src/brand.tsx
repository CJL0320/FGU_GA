import React from 'react';
import {AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// Palette C (Mustafa, violet + neon blue): night = background, deep = cards/depth, violet = main accent,
// blue = neon accent, ice/lav = light tints, edge = dark violet for 3D sides.
export const C = {night: '#140B34', deep: '#2A1B5E', violet: '#8B5CF6', blue: '#38BDF8', ice: '#BAE6FD', lav: '#C4B5FD',
  cream: '#EDE9FE', white: '#FFFFFF', edge: '#4C1D95'};

// Brand fonts: Readex Pro Bold (Arabic + Latin), Sora ExtraBold / SemiBold (Latin), Aref Ruqaa (script accents).
export const Fonts: React.FC = () => (
  <style>{`
    @font-face{font-family:Readex;src:url(${staticFile('ReadexPro-Bold.ttf')})}
    @font-face{font-family:Sora;src:url(${staticFile('Sora-ExtraBold.ttf')})}
    @font-face{font-family:SoraSemi;src:url(${staticFile('Sora-SemiBold.ttf')})}
    @font-face{font-family:Ruqaa;src:url(${staticFile('ArefRuqaa-Bold.ttf')})}
  `}</style>
);

export const arFont = (t: string) => (/[؀-ۿ]/.test(t) ? 'Readex' : 'Sora');

// Night-violet background: breathing violet glow + a neon-blue glow, perspective floor grid. Scales with the comp size.
export const NavyBg: React.FC = () => {
  const f = useCurrentFrame();
  const {width} = useVideoConfig();
  const s = width / 540;
  const r = (300 + 20 * Math.sin(f / 9)) * s;
  const r2 = (190 + 14 * Math.cos(f / 11)) * s;
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 30%, #1E1250 0%, ${C.night} 70%)`, overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: 270 * s - r, top: 230 * s - r, width: r * 2, height: r * 2, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.violet}55 0%, ${C.violet}00 70%)`}} />
      <div style={{position: 'absolute', left: 400 * s - r2, top: 420 * s - r2, width: r2 * 2, height: r2 * 2, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.blue}33 0%, ${C.blue}00 70%)`}} />
      <div style={{position: 'absolute', left: -300 * s, right: -300 * s, top: 520 * s, height: 900 * s,
        transform: 'perspective(500px) rotateX(62deg)', transformOrigin: 'top',
        backgroundImage: `linear-gradient(${C.deep} ${2 * s}px, transparent ${2 * s}px), linear-gradient(90deg, ${C.deep} ${2 * s}px, transparent ${2 * s}px)`,
        backgroundSize: `${60 * s}px ${60 * s}px`, backgroundPosition: `0 ${f * 2 * s}px`, opacity: 0.8}} />
    </AbsoluteFill>
  );
};

export const neon = (col: string) => `0 0 8px ${col}, 0 0 22px ${col}, 0 0 44px ${col}aa`;
