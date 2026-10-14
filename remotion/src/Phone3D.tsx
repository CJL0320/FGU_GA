import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, Fonts, NavyBg} from './brand';

const msgs = [{t: 'السلام، المنتوج متوفر؟', me: false, at: 6}, {t: 'إيه خويا، متوفر', me: true, at: 14}, {t: 'نحب نكوموندي واحد', me: false, at: 22}];

// CSS-3D phone swinging to face the camera while WhatsApp-style messages pop in.
export const Phone3D: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f, fps, config: {damping: 14, stiffness: 80}});
  return (
    <AbsoluteFill>
      <Fonts /><NavyBg />
      <div style={{position: 'absolute', left: 270 - 150, top: 60, width: 300, height: 520, perspective: 1100}}>
        <div style={{width: 300, height: 520, borderRadius: 44, background: '#141418', padding: 12, boxSizing: 'border-box',
          transform: `rotateY(${(1 - k) * 55 - 8}deg) rotateX(${8 - (1 - k) * 10}deg) translateZ(${(1 - k) * -200}px)`,
          boxShadow: `0 40px 70px #000c, 0 0 0 3px ${C.violet}, 0 0 30px ${C.blue}66, -12px 0 0 #0a0a0d`}}>
          <div style={{width: '100%', height: '100%', borderRadius: 34, background: '#0b141a', overflow: 'hidden', direction: 'rtl'}}>
            <div style={{background: '#005C4B', color: '#fff', fontFamily: 'SoraSemi', fontSize: 24, padding: '18px 0', textAlign: 'center'}}>WhatsApp</div>
            {msgs.map((m, i) => {
              const s = spring({frame: f - m.at, fps, config: {damping: 12, stiffness: 160}});
              return (
                <div key={i} style={{display: 'flex', justifyContent: m.me ? 'flex-end' : 'flex-start', padding: '10px 14px'}}>
                  <div style={{transform: `scale(${s})`, transformOrigin: m.me ? 'left' : 'right', background: m.me ? '#005C4B' : '#202C33',
                    color: '#fff', fontFamily: 'Readex', fontSize: 21, padding: '10px 14px', borderRadius: 16}}>{m.t}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
