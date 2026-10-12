'use client';

import React from 'react';
import { VideoBlueprintPlan, CharacterContext, Character } from '../lib/types';

interface SceneBlueprintViewerProps {
  blueprint: VideoBlueprintPlan;
  characterContext?: CharacterContext | null;
  character?: Character | null;
}

export function SceneBlueprintViewer({ blueprint, characterContext, character }: SceneBlueprintViewerProps) {
  const getAngleBadge = (angle: string) => {
    const a = angle.toLowerCase().replace('cameraangle.', '');
    switch (a) {
      case 'front':
        return { label: 'Front Angle 🎯', bg: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.4)', color: '#34d399', note: 'Max identity fidelity' };
      case 'three_quarter':
        return { label: '3/4 Angle 🔄', bg: 'rgba(56, 189, 248, 0.15)', border: 'rgba(56, 189, 248, 0.4)', color: '#38bdf8', note: 'Natural rotation' };
      case 'side_profile':
        return { label: 'Side Profile 👤', bg: 'rgba(245, 158, 11, 0.15)', border: 'rgba(245, 158, 11, 0.4)', color: '#fbbf24', note: 'Steered via prompt' };
      case 'wide':
        return { label: 'Wide Shot 🏞️', bg: 'rgba(168, 85, 247, 0.15)', border: 'rgba(168, 85, 247, 0.4)', color: '#c084fc', note: 'Atmospheric depth' };
      case 'close_up':
        return { label: 'Close-Up 🔍', bg: 'rgba(244, 63, 94, 0.15)', border: 'rgba(244, 63, 94, 0.4)', color: '#fb7185', note: 'Emotional focus' };
      default:
        return { label: angle, bg: 'rgba(255, 255, 255, 0.05)', border: 'var(--border-subtle)', color: 'var(--text-muted)', note: '' };
    }
  };

  return (
    <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ fontSize: '1.25rem' }}>🎬</span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {blueprint.title}
            </h3>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '750px', lineHeight: 1.5 }}>
            {blueprint.narrative_summary}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div style={{
            padding: '0.4rem 0.8rem',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(245, 158, 11, 0.12)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            fontSize: '0.8rem',
            fontWeight: 600,
            color: 'var(--accent-amber)',
          }}>
            {blueprint.total_scenes} Scenes (~{blueprint.total_scenes * 5}s total)
          </div>
        </div>
      </div>

      {/* Identity Anchoring Banner */}
      <div style={{
        padding: '0.85rem 1rem',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(10, 15, 28, 0.9)',
        border: '1px solid var(--border-subtle)',
        marginBottom: '1.25rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {character?.canonical_portrait_url && (
            <img
              src={character.canonical_portrait_url}
              alt={character.name}
              style={{ width: '42px', height: '42px', borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--accent-amber)' }}
            />
          )}
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
              3-Layer Identity Anchor: <span style={{ color: 'var(--accent-amber)' }}>{character?.name || characterContext?.name || blueprint.character_id}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>
              Pinned Portrait Asset: <code style={{ color: 'var(--accent-blue)' }}>{characterContext?.canonical_portrait_uri || `characters/${blueprint.character_id}/portrait.png`}</code> (Version 1 LOCKED)
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.75rem' }}>
          <span style={{ color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            ✓ Consistent Face
          </span>
          <span style={{ color: 'var(--text-dim)' }}>•</span>
          <span style={{ color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            ✓ Same Reference Image
          </span>
          <span style={{ color: 'var(--text-dim)' }}>•</span>
          <span style={{ color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            ✓ Locked Version
          </span>
        </div>
      </div>

      {/* Scene Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {blueprint.scenes.map((scene) => {
          const angleMeta = getAngleBadge(scene.camera_angle);
          return (
            <div
              key={scene.scene_number}
              style={{
                borderRadius: 'var(--radius-md)',
                background: 'rgba(15, 22, 38, 0.7)',
                border: '1px solid var(--border-subtle)',
                padding: '1.1rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'border-color 0.2s ease, transform 0.2s ease',
              }}
            >
              <div>
                {/* Scene Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: 'var(--accent-amber)',
                    letterSpacing: '0.05em',
                  }}>
                    Scene {scene.scene_number}
                  </span>
                  <span style={{
                    fontSize: '0.7rem',
                    padding: '0.2rem 0.5rem',
                    borderRadius: 'var(--radius-sm)',
                    background: angleMeta.bg,
                    border: `1px solid ${angleMeta.border}`,
                    color: angleMeta.color,
                    fontWeight: 600,
                  }}>
                    {angleMeta.label}
                  </span>
                </div>

                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  {scene.scene_title}
                </h4>

                <p style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)',
                  lineHeight: 1.45,
                  marginBottom: '0.75rem',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {scene.visual_description}
                </p>
              </div>

              {/* Scene Metadata Footer */}
              <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '0.65rem', marginTop: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>
                  <span>Shot Framing:</span>
                  <strong style={{ color: 'var(--text-main)' }}>{scene.shot_type.replace('_', ' ')}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>
                  <span>Duration:</span>
                  <strong style={{ color: 'var(--accent-blue)' }}>{scene.estimated_duration_seconds}s</strong>
                </div>
                {angleMeta.note && (
                  <div style={{ fontSize: '0.7rem', color: angleMeta.color, marginTop: '0.35rem', fontStyle: 'italic' }}>
                    Orientation Strategy: {angleMeta.note}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
