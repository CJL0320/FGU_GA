import React from 'react';
import {AbsoluteFill, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, Fonts, arFont} from './brand';

// "Reference reel" look (Mustafa liked it, 2026-10-09), in palette C. All 1080x1920.
// PhoneSplit = full-frame layout (bokeh bg + tilted 3D phone + his face shrinking into a PIP + neon label pill).
// GlassCard / SearchBar / CtaPills = transparent overlays (rendered as ProRes 4444) composited on his video.

const ar = (t: string) => /[؀-ۿ]/.test(t);

const Bokeh: React.FC = () => {
  const f = useCurrentFrame();
  const dots = Array.from({length: 26}, (_, i) => i);
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 35%, #2A1B5E 0%, ${C.night} 75%)`, overflow: 'hidden'}}>
      {dots.map((i) => {
        const x = (i * 397) % 1080, y = (i * 613) % 1920;
        const r = 18 + ((i * 7) % 30);
        const col = i % 3 === 0 ? C.blue : i % 3 === 1 ? C.violet : '#F5D0FE';
        const o = 0.25 + 0.25 * Math.sin(f / 14 + i);
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: r * 2, height: r * 2, borderRadius: '50%',
          background: col, opacity: o, filter: 'blur(10px)'}} />;
      })}
    </AbsoluteFill>
  );
};

export const Pill: React.FC<{text: string; k: number; big?: boolean}> = ({text, k, big}) => (
  <div style={{display: 'inline-block', transform: `scale(${0.6 + 0.4 * k})`, opacity: k, padding: big ? '14px 34px' : '10px 26px',
    borderRadius: 999, background: C.blue, color: C.night, fontFamily: arFont(text), fontSize: big ? 52 : 40,
    direction: ar(text) ? 'rtl' : 'ltr', boxShadow: `0 0 24px ${C.blue}aa, 0 8px 24px #0008`, whiteSpace: 'nowrap'}}>{text}</div>
);

export const PhoneSplit: React.FC<{pip: string; phone: string; label: string}> = ({pip, phone, label}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const shrink = spring({frame: f, fps, config: {damping: 16, stiffness: 120}});        // full frame -> PIP
  const ph = spring({frame: f - 4, fps, config: {damping: 14, stiffness: 110}});        // phone slides in
  const lab = spring({frame: f - 10, fps, config: {damping: 12}});
  const pw = interpolate(shrink, [0, 1], [1080, 400]), phh = pw * 1920 / 1080;
  const px = interpolate(shrink, [0, 1], [0, 1080 - 400 - 40]), py = interpolate(shrink, [0, 1], [0, 1920 - phh - 330]);
  const rad = interpolate(shrink, [0, 1], [0, 36]);
  return (
    <AbsoluteFill>
      <Fonts /><Bokeh />
      <div style={{position: 'absolute', left: 70, top: 170, width: 620, height: 1180, perspective: 1400,
        transform: `translateX(${(1 - ph) * -800}px)`}}>
        <div style={{width: '100%', height: '100%', transform: 'rotateY(16deg) rotateZ(-4deg)', borderRadius: 64, padding: 18,
          background: '#0B0620', boxShadow: `0 0 0 4px ${C.violet}, 0 0 40px ${C.violet}88, 30px 40px 60px #000a`}}>
          <div style={{width: '100%', height: '100%', borderRadius: 48, overflow: 'hidden', background: C.night}}>
            <OffthreadVideo src={staticFile(phone)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', left: px, top: py, width: pw, height: phh, borderRadius: rad, overflow: 'hidden',
        boxShadow: shrink > 0.05 ? `0 0 0 5px ${C.blue}, 0 0 30px ${C.blue}99, 0 20px 40px #000b` : 'none'}}>
        <OffthreadVideo src={staticFile(pip)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </div>
      <div style={{position: 'absolute', left: 1080 - 40 - 200, top: 1920 - 330 - 40, transform: 'translateX(-50%)'}}>
        <Pill text={label} k={lab} />
      </div>
    </AbsoluteFill>
  );
};

export const GlassCard: React.FC<{title: string; value: number; sub: string; x: number; y: number}> = ({title, value, sub, x, y}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f, fps, config: {damping: 13, stiffness: 140}});
  const n = Math.round(interpolate(f, [4, 28], [0, value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <AbsoluteFill>
      <Fonts />
      <div style={{position: 'absolute', left: x, top: y, width: 420, padding: '26px 30px', borderRadius: 34,
        transform: `scale(${0.5 + 0.5 * k}) translateY(${(1 - k) * 40}px)`, opacity: k, transformOrigin: 'left center',
        background: 'linear-gradient(160deg, rgba(139,92,246,0.55), rgba(20,11,52,0.75))', backdropFilter: 'blur(14px)',
        border: '2px solid rgba(196,181,253,0.55)', boxShadow: `0 0 40px ${C.violet}77, 0 20px 50px #000a`}}>
        <div style={{fontFamily: 'SoraSemi', fontSize: 32, color: C.lav, letterSpacing: 2, display: 'flex', alignItems: 'center', gap: 12}}>
          <span style={{width: 16, height: 16, borderRadius: 8, background: C.blue, boxShadow: `0 0 12px ${C.blue}`}} />{title}
        </div>
        <div style={{fontFamily: 'Sora', fontSize: 130, lineHeight: 1.05, color: C.white, textShadow: `0 0 24px ${C.blue}`}}>{n}</div>
        <div style={{fontFamily: arFont(sub), fontSize: 40, color: C.cream, direction: ar(sub) ? 'rtl' : 'ltr'}}>{sub}</div>
      </div>
    </AbsoluteFill>
  );
};

export const SearchBar: React.FC<{text: string; y: number}> = ({text, y}) => {
  const f = useCurrentFrame(); const {fps, durationInFrames} = useVideoConfig();
  const k = spring({frame: f, fps, config: {damping: 14}});
  const chars = Array.from(text);
  const shown = Math.floor(interpolate(f, [6, Math.max(8, durationInFrames - 14)], [0, chars.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const caret = Math.floor(f / 8) % 2 === 0;
  return (
    <AbsoluteFill>
      <Fonts />
      <div style={{position: 'absolute', left: 60, right: 60, top: y, height: 130, borderRadius: 65, display: 'flex', alignItems: 'center',
        gap: 24, padding: '0 40px', direction: 'rtl', transform: `scale(${0.7 + 0.3 * k})`, opacity: k,
        background: 'rgba(20,11,52,0.82)', border: `3px solid ${C.violet}`, boxShadow: `0 0 30px ${C.violet}88, 0 16px 40px #000a`}}>
        <svg width="54" height="54" viewBox="0 0 24 24"><circle cx="10" cy="10" r="7" stroke={C.blue} strokeWidth="2.6" fill="none" /><path d="M15 15l6 6" stroke={C.blue} strokeWidth="2.6" strokeLinecap="round" /></svg>
        <div style={{fontFamily: 'Readex', fontSize: 50, color: C.white, whiteSpace: 'nowrap', overflow: 'hidden'}}>
          {chars.slice(0, shown).join('')}<span style={{color: C.blue, opacity: caret ? 1 : 0}}>|</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const CtaPills: React.FC<{items: string[]; y: number}> = ({items, y}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const step = 9;
  const tapAt = items.length * step + 4;
  const tap = interpolate(f, [tapAt, tapAt + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <Fonts />
      <div style={{position: 'absolute', top: y, width: '100%', display: 'flex', justifyContent: 'center', gap: 22}}>
        {items.map((t, i) => {
          const k = spring({frame: f - i * step, fps, config: {damping: 11, stiffness: 160}});
          return <div key={i} style={{position: 'relative'}}>
            <Pill text={t} k={k} />
            {i === 0 && tap > 0 && tap < 1 && <div style={{position: 'absolute', left: '50%', top: '50%', width: 120 * tap, height: 120 * tap,
              marginLeft: -60 * tap, marginTop: -60 * tap, borderRadius: '50%', border: `4px solid ${C.white}`, opacity: 1 - tap}} />}
          </div>;
        })}
      </div>
    </AbsoluteFill>
  );
};
