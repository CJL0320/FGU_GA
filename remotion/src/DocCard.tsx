import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, Easing} from 'remotion';
import {C, Fonts} from './brand';

// Documentary look: newspaper paper, slow Ken-Burns push, neon-blue highlighter sweeping right->left, grain + vignette.
export const DocCard: React.FC<{text: string; kicker: string}> = ({text, kicker}) => {
  const f = useCurrentFrame();
  const hl = interpolate(f, [8, 30], [0, 100], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const zoom = interpolate(f, [0, 60], [1, 1.07]);
  return (
    <AbsoluteFill style={{background: '#2a1f15'}}>
      <Fonts />
      <AbsoluteFill style={{transform: `scale(${zoom}) rotate(-1.2deg)`, background: '#F5EEE1', margin: 18, borderRadius: 6,
        boxShadow: '0 30px 60px #000a'}}>
        <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontFamily: 'SoraSemi', fontSize: 22, color: '#7a6e5f',
          letterSpacing: 3}}>{kicker}</div>
        <div style={{position: 'absolute', top: 100, left: 50, right: 50, height: 2, background: '#7a6e5f'}} />
        <div style={{position: 'absolute', top: 180, width: '100%', display: 'flex', justifyContent: 'center'}}>
          <div style={{position: 'relative', direction: 'rtl', fontFamily: 'Readex', fontSize: 60, color: '#1a1612', padding: '4px 18px'}}>
            <div style={{position: 'absolute', top: 10, bottom: 6, right: 0, width: `${hl}%`, background: `${C.blue}99`,
              borderRadius: 8, transform: 'skewX(-6deg)'}} />
            <span style={{position: 'relative'}}>{text}</span>
          </div>
        </div>
        {Array.from({length: 9}).map((_, i) => (
          <div key={i} style={{position: 'absolute', top: 330 + i * 46, right: 50, width: `${80 - (i % 3) * 12}%`, height: 14,
            borderRadius: 7, background: '#cfc6b5'}} />
        ))}
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, #0000 55%, #000a 100%)'}} />
      <AbsoluteFill style={{opacity: 0.08, backgroundImage:
        `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence baseFrequency='0.9' seed='${f % 7}'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>")`}} />
    </AbsoluteFill>
  );
};
