import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
import {C, Fonts, NavyBg, arFont, neon} from './brand';

// Real CSS-3D cube (product box) spinning in with a spring, glossy faces in brand colours (violet sides, neon-blue lid).
const S = 190;
const face = (tf: string, bg: string, label?: string): React.CSSProperties & {label?: string} => ({
  position: 'absolute', width: S, height: S, transform: tf, background: bg, border: `3px solid ${C.blue}`,
  boxShadow: `inset 0 0 40px #0006`, display: 'flex', alignItems: 'center', justifyContent: 'center', label});

export const Cube3D: React.FC<{title: string; sub: string}> = ({title, sub}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f, fps, config: {damping: 13, stiffness: 90}});
  const ry = interpolate(k, [0, 1], [-200, -28]) + Math.sin(f / 10) * 6;
  const rx = -18 + Math.sin(f / 13) * 4;
  const faces = [
    face(`translateZ(${S / 2}px)`, `linear-gradient(160deg, ${C.lav}, ${C.violet})`),
    face(`rotateY(90deg) translateZ(${S / 2}px)`, `linear-gradient(160deg, ${C.violet}, #5B21B6)`),
    face(`rotateY(180deg) translateZ(${S / 2}px)`, C.edge),
    face(`rotateY(-90deg) translateZ(${S / 2}px)`, `linear-gradient(160deg, ${C.violet}, #6D28D9)`),
    face(`rotateX(90deg) translateZ(${S / 2}px)`, `linear-gradient(160deg, ${C.ice}, ${C.blue})`),
    face(`rotateX(-90deg) translateZ(${S / 2}px)`, '#2E1065'),
  ];
  return (
    <AbsoluteFill>
      <Fonts /><NavyBg />
      <div style={{position: 'absolute', left: 270 - 130, top: 395, width: 260, height: 36, borderRadius: '50%',
        background: 'radial-gradient(#000c, #0000 70%)', transform: `scale(${k})`}} />
      <div style={{position: 'absolute', left: 270 - S / 2, top: 150, width: S, height: S, perspective: 900}}>
        <div style={{width: S, height: S, position: 'relative', transformStyle: 'preserve-3d',
          transform: `translateY(${(1 - k) * -300 + Math.sin(f / 8) * 8}px) rotateX(${rx}deg) rotateY(${ry}deg)`}}>
          {faces.map((st, i) => <div key={i} style={st}>{i === 0 &&
            <div style={{width: 46, height: S, background: '#E0F2FE88'}} />}</div>)}
        </div>
      </div>
      <div style={{position: 'absolute', top: 455, width: '100%', textAlign: 'center', fontFamily: arFont(title), fontSize: title.length > 12 ? 58 : 72, direction: 'rtl',
        color: C.cream, textShadow: neon(C.violet), transform: `translateY(${(1 - k) * 40}px)`, opacity: k}}>{title}</div>
      <div style={{position: 'absolute', top: 545, width: '100%', textAlign: 'center', fontFamily: 'Ruqaa', fontSize: 50,
        color: C.white, direction: 'rtl', textShadow: '0 0 14px #fff8', opacity: interpolate(f, [14, 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{sub}</div>
    </AbsoluteFill>
  );
};
