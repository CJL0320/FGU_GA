import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, Fonts, NavyBg, neon} from './brand';

// Animated end card (1080x1920, 3 s): logo pops in with a neon glow, handle + CTA slide up, WhatsApp pill with a
// violet->blue neon border and a light sweep. Content stays inside the Instagram safe zone (y 420..1450).
export const EndCard: React.FC<{handle: string; whatsapp: string; cta: string; tag: string}> = ({handle, whatsapp, cta, tag}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const pop = spring({frame: f, fps, config: {damping: 11, stiffness: 120}});
  const up = (start: number) => spring({frame: f - start, fps, config: {damping: 14, stiffness: 110}});
  const k1 = up(8), k2 = up(14), k3 = up(20), k4 = up(28);
  const float = Math.sin(f / 9) * 8;
  const pulse = 0.75 + 0.25 * Math.sin(f / 5);
  const sweep = interpolate(f, [34, 58], [-40, 140], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <Fonts /><NavyBg />
      {/* logo */}
      <div style={{position: 'absolute', left: 540 - 170, top: 430 + float, width: 340, height: 340,
        transform: `scale(${pop}) rotate(${(1 - pop) * -14}deg)`,
        filter: `drop-shadow(0 0 ${30 * pulse}px ${C.violet}) drop-shadow(0 0 ${60 * pulse}px ${C.blue}66)`}}>
        <Img src={staticFile('logo_icon.png')} style={{width: 340, height: 340}} />
      </div>
      {/* handle + underline */}
      <div style={{position: 'absolute', top: 830, width: '100%', textAlign: 'center', fontFamily: 'Sora', fontSize: 92,
        color: C.white, textShadow: neon(`${C.violet}`), opacity: k1, transform: `translateY(${(1 - k1) * 60}px)`}}>{handle}</div>
      <div style={{position: 'absolute', top: 960, left: 540 - 150 * k1, width: 300 * k1, height: 10, borderRadius: 5,
        background: `linear-gradient(90deg, ${C.violet}, ${C.blue})`, boxShadow: `0 0 18px ${C.blue}`}} />
      {/* CTA */}
      <div style={{position: 'absolute', top: 1010, width: '100%', textAlign: 'center', fontFamily: 'Readex', fontSize: 66,
        color: C.cream, direction: 'rtl', opacity: k2, transform: `translateY(${(1 - k2) * 60}px)`}}>{cta}</div>
      {/* WhatsApp pill */}
      <div style={{position: 'absolute', top: 1145, left: 120, width: 840, height: 150, borderRadius: 75, padding: 5,
        boxSizing: 'border-box', background: `linear-gradient(90deg, ${C.violet}, ${C.blue})`,
        boxShadow: `0 0 ${34 * pulse}px ${C.blue}aa, 0 20px 40px #0009`,
        opacity: k3, transform: `scale(${0.85 + 0.15 * k3})`}}>
        <div style={{position: 'relative', width: '100%', height: '100%', borderRadius: 70, overflow: 'hidden',
          background: `linear-gradient(90deg, ${C.night}, ${C.deep})`, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 26}}>
          <svg width="74" height="74" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="29" fill="#25D366" />
            <path d="M22 18c2-1 4 0 5 2l2 5c0 1 0 2-1 3l-2 2c2 4 5 7 9 9l2-2c1-1 2-1 3-1l5 2c2 1 3 3 2 5-1 3-4 5-7 4-10-2-18-10-20-20-1-3 1-6 2-7z" fill="#fff" />
          </svg>
          <div style={{fontFamily: 'Sora', fontSize: 70, color: C.white, letterSpacing: 1}}>{whatsapp}</div>
          <div style={{position: 'absolute', top: 0, bottom: 0, left: `${sweep}%`, width: '18%',
            background: 'linear-gradient(90deg, #ffffff00, #ffffff40, #ffffff00)', transform: 'skewX(-18deg)'}} />
        </div>
      </div>
      {/* tagline */}
      <div style={{position: 'absolute', top: 1350, width: '100%', textAlign: 'center', fontFamily: 'SoraSemi', fontSize: 30,
        color: C.lav, letterSpacing: 4, opacity: k4}}>{tag}</div>
    </AbsoluteFill>
  );
};
