import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, Fonts, NavyBg, arFont, neon} from './brand';

// Product b-roll for a clothing "model": a dress on a hanger swings in (3D sway), violet -> blue satin gradient,
// shine sweep, sparkles, title = the caption words.
export const Dress3D: React.FC<{title: string; sub: string}> = ({title, sub}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f, fps, config: {damping: 12, stiffness: 90}});
  const sway = Math.sin(f / 9) * 7 * k + (1 - k) * 35;
  const ry = Math.sin(f / 14) * 18;
  const shine = interpolate(f, [10, 45], [-60, 160], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const kt = spring({frame: f - 10, fps, config: {damping: 14}});
  return (
    <AbsoluteFill>
      <Fonts /><NavyBg />
      <div style={{position: 'absolute', left: 270 - 130, top: 410, width: 260, height: 30, borderRadius: '50%',
        background: 'radial-gradient(#000c, #0000 70%)', transform: `scale(${k})`}} />
      <div style={{position: 'absolute', left: 270 - 140, top: 40, width: 280, height: 380, perspective: 900}}>
        <div style={{width: 280, height: 380, transformOrigin: '50% 0%', transform: `translateY(${(1 - k) * -250}px) rotate(${sway}deg) rotateY(${ry}deg)`,
          filter: `drop-shadow(0 0 18px ${C.violet}aa)`}}>
          <svg width="280" height="380" viewBox="0 0 280 380">
            <defs>
              <linearGradient id="satin" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor="#C4B5FD" /><stop offset="0.45" stopColor={C.violet} /><stop offset="1" stopColor="#5B21B6" />
              </linearGradient>
              <linearGradient id="trim" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stopColor={C.violet} /><stop offset="1" stopColor={C.blue} />
              </linearGradient>
              <clipPath id="dressClip">
                <path d="M110 70 L96 60 L84 96 L104 150 L58 360 Q140 382 222 360 L176 150 L196 96 L184 60 L170 70 Q140 92 110 70 Z" />
              </clipPath>
            </defs>
            {/* hanger */}
            <path d="M140 18 Q140 6 150 8 Q160 12 152 22 L140 34" fill="none" stroke="#E0E7FF" strokeWidth="5" strokeLinecap="round" />
            <path d="M140 34 L74 66 L206 66 Z" fill="none" stroke="#E0E7FF" strokeWidth="5" strokeLinejoin="round" />
            {/* dress */}
            <path d="M110 70 L96 60 L84 96 L104 150 L58 360 Q140 382 222 360 L176 150 L196 96 L184 60 L170 70 Q140 92 110 70 Z" fill="url(#satin)" />
            <path d="M104 150 Q140 162 176 150" fill="none" stroke="url(#trim)" strokeWidth="9" strokeLinecap="round" />
            <g clipPath="url(#dressClip)" opacity="0.9">
              <path d="M120 160 Q110 260 92 362" stroke="#ffffff33" strokeWidth="6" fill="none" />
              <path d="M160 160 Q172 260 190 362" stroke="#00000033" strokeWidth="8" fill="none" />
              <rect x={shine} y="0" width="40" height="380" fill="#ffffff55" transform="skewX(-15)" />
            </g>
          </svg>
        </div>
      </div>
      {[0, 1, 2, 3].map((i) => {
        const p = ((f + i * 12) % 48) / 48;
        const x = 270 + Math.cos(i * 1.7) * (150 + 20 * p); const y = 120 + i * 70 - p * 30;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: 12, height: 12, borderRadius: 6,
          background: C.ice, boxShadow: neon(C.blue), opacity: Math.sin(p * Math.PI) * k}} />;
      })}
      <div style={{position: 'absolute', top: 470, width: '100%', textAlign: 'center', fontFamily: arFont(title), fontSize: title.length > 12 ? 58 : 72,
        direction: 'rtl', color: C.cream, textShadow: neon(C.violet), opacity: kt, transform: `translateY(${(1 - kt) * 40}px)`}}>{title}</div>
      {sub && <div style={{position: 'absolute', top: 560, width: '100%', textAlign: 'center', fontFamily: 'Ruqaa', fontSize: 50, color: C.white,
        direction: 'rtl', opacity: kt}}>{sub}</div>}
    </AbsoluteFill>
  );
};
