'use client';

import React, { useState } from 'react';
import { Character } from '../lib/types';

interface PromptInputProps {
  selectedCharacter: Character | null;
  onPlan: (prompt: string) => void;
  isPlanning: boolean;
}

const PRESET_PROMPTS = [
  'Priya explores a vibrant Mumbai textile market, touches a rich crimson silk scarf on display, admires her reflection in a stall mirror with a warm smile, and happily buys it.',
  'Arjun arrives at a bustling Bangalore tech campus, grabs a hot filter chai from a street stall, opens his laptop on a stone bench, and gestures enthusiastically during a video call.',
  'Devi enters a historic temple courtyard in Madurai during golden hour twilight, adjusts her classical attire, performs an expressive Bharatanatyam mudra, and pauses with serene grace.',
  'Vikram rides a motorcycle along a rugged Himalayan highway, stops at a mountain pass draped with colorful prayer flags, removes his helmet, and gazes at the snow peaks.',
];

export function PromptInput({ selectedCharacter, onPlan, isPlanning }: PromptInputProps) {
  const [prompt, setPrompt] = useState(PRESET_PROMPTS[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isPlanning) return;
    onPlan(prompt.trim());
  };

  return (
    <div className="card prompt-input-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🧠</span> Gemini 3.8 Flash Video Blueprint Planner
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Enter a narrative storyline. Gemini decomposes it into discrete 5-second scenes with camera angles optimized for {selectedCharacter?.name || 'the avatar'}.
          </p>
        </div>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.35rem 0.75rem',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(56, 189, 248, 0.12)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          color: 'var(--accent-blue)',
          fontSize: '0.75rem',
          fontWeight: 600,
        }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-blue)', display: 'inline-block' }}></span>
          Gemini 3.8 Flash JSON
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ position: 'relative' }}>
          <textarea
            className="input-textarea"
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={`Describe what ${selectedCharacter?.name || 'the character'} is doing across multiple scenes...`}
            style={{
              width: '100%',
              padding: '0.85rem 1rem',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(10, 15, 28, 0.8)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-main)',
              fontSize: '0.95rem',
              resize: 'vertical',
              fontFamily: 'inherit',
              lineHeight: 1.5,
            }}
          />
        </div>

        {/* Quick presets */}
        <div style={{ marginTop: '0.75rem', marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Sample Narrative Prompts:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {PRESET_PROMPTS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setPrompt(p)}
                style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  background: prompt === p ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                  border: prompt === p ? '1px solid var(--accent-amber)' : '1px solid var(--border-subtle)',
                  color: prompt === p ? 'var(--accent-amber-light)' : 'var(--text-muted)',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                }}
              >
                Story {idx + 1}: {p.slice(0, 38)}...
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            <span>Target Avatar:</span>
            <strong style={{ color: 'var(--accent-amber)' }}>{selectedCharacter?.name} ({selectedCharacter?.character_id})</strong>
          </div>

          <button
            type="submit"
            disabled={isPlanning || !prompt.trim()}
            style={{
              padding: '0.75rem 1.75rem',
              borderRadius: 'var(--radius-md)',
              background: isPlanning ? 'rgba(245, 158, 11, 0.4)' : 'linear-gradient(135deg, #f59e0b, #d97706)',
              border: 'none',
              color: '#07090e',
              fontWeight: 700,
              fontSize: '0.95rem',
              cursor: isPlanning ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 4px 14px rgba(245, 158, 11, 0.3)',
              transition: 'all 0.2s ease',
            }}
          >
            {isPlanning ? (
              <>
                <span className="spinner" style={{ width: '16px', height: '16px', borderTopColor: '#07090e' }}></span>
                Planning Scenes via Gemini...
              </>
            ) : (
              <>
                <span>✨</span> Plan Video Blueprint
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
