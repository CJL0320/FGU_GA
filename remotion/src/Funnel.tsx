import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, Fonts, NavyBg, neon} from './brand';

const stages = [{l: 'إعلان', w: 430}, {l: 'رسائل', w: 330}, {l: 'طلبيات', w: 230}];

export const Funnel: React.FC<{title: string}> = ({title}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return (
    <AbsoluteFill>
      <Fonts /><NavyBg />
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontFamily: 'Readex', fontSize: 50,
        color: C.cream, textShadow: neon(C.violet), opacity: interpolate(f, [0, 8], [0, 1]), direction: 'rtl'}}>{title}</div>
      {stages.map((s, i) => {
        const k = spring({frame: f - 6 - i * 8, fps, config: {damping: 11, stiffness: 140}});
        const next = stages[i + 1]?.w ?? s.w * 0.75;
        return (
          <div key={i} style={{position: 'absolute', top: 170 + i * 118, left: 270 - s.w / 2, width: s.w, height: 100,
            transform: `perspective(700px) rotateX(${(1 - k) * 80}deg) scale(${k})`, transformOrigin: 'top',
            clipPath: `polygon(0 0, 100% 0, ${50 + (next / s.w) * 50}% 100%, ${50 - (next / s.w) * 50}% 100%)`,
            background: `linear-gradient(180deg, ${C.blue} 0%, ${C.violet} 55%, #5B21B6 100%)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'Readex', fontSize: 38, color: C.white, textShadow: '0 3px 8px #0008'}}>{s.l}</div>
        );
      })}
      {Array.from({length: 12}).map((_, j) => {
        const p = ((f - 30 + j * 4) % 44) / 44;
        if (f < 30 || p < 0) return null;
        const x = 270 + Math.sin(j * 2.3) * (1 - p) * 150; const y = 150 + p * 360;
        return <div key={j} style={{position: 'absolute', left: x - 7, top: y - 7, width: 14, height: 14, borderRadius: 7,
          background: C.ice, boxShadow: neon(C.blue), opacity: 1 - p * 0.6}} />;
      })}
    </AbsoluteFill>
  );
};
