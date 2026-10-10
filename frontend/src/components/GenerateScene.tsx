'use client';

import React, { useState } from 'react';
import { Character } from '../lib/types';

interface GenerateSceneProps {
  selectedCharacter: Character;
  onGenerate: (prompt: string, adapterType: string, seed?: number) => void;
  isGenerating: boolean;
  onPromptChange?: (prompt: string) => void;
}

const PRESET_PROMPTS = [
  "Walking across Marine Drive in Mumbai at golden hour with sea breeze",
  "Delivering a visionary keynote presentation at a Bengaluru AI summit",
  "Practicing expressive mudras in a sunlit ancient temple courtyard",
  "Brainstorming creative designs in a bustling urban cafe",
  "Sipping chai while taking in Himalayan mountain vistas at dawn"
];

export const GenerateScene: React.FC<GenerateSceneProps> = ({
  selectedCharacter,
  onGenerate,
  isGenerating,
  onPromptChange
}) => {
  const [prompt, setPrompt] = useState(PRESET_PROMPTS[0]);
  const [adapterType, setAdapterType] = useState('simulated');
  const [seed, setSeed] = useState<string>('42');

  const handlePromptUpdate = (newVal: string) => {
    setPrompt(newVal);
    if (onPromptChange) onPromptChange(newVal);
  };

  const handleGenerateClick = () => {
    if (!prompt.trim()) return;
    const seedNum = seed ? parseInt(seed, 10) : undefined;
    onGenerate(prompt, adapterType, isNaN(seedNum as number) ? undefined : seedNum);
  };

  return (
    <div className="glass-panel" id="generate-scene-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span>✨</span> Generate Scene for {selectedCharacter.name}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="panel-badge">Identity Pinned (v{selectedCharacter.version})</span>
        </div>
      </div>

      <div className="prompt-composer">
        <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Scene / Action Description (Conditioned on Canonical Portrait)
        </label>
        <textarea
          className="prompt-textarea"
          value={prompt}
          onChange={(e) => handlePromptUpdate(e.target.value)}
          placeholder="Describe scene action, background, lighting, and camera movement..."
        />

        <div className="preset-prompts-bar">
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Presets:</span>
          {PRESET_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              className="preset-btn"
              onClick={() => handlePromptUpdate(p)}
            >
              Preset {idx + 1}
            </button>
          ))}
        </div>

        <div className="controls-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <div className="adapter-selector">
              <button
                className={`adapter-option ${adapterType === 'simulated' ? 'active' : ''}`}
                onClick={() => setAdapterType('simulated')}
                title="Zero-cost simulated generation with [SIMULATED] watermark"
              >
                Simulated (Local $0)
              </button>
              <button
                className={`adapter-option ${adapterType === 'wan_i2v' ? 'active' : ''}`}
                onClick={() => setAdapterType('wan_i2v')}
                title="Real Wan 2.2 I2V inference via Fal.ai (requires FAL_KEY)"
              >
                Wan 2.2 (Fal.ai)
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Seed:</span>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                style={{
                  width: '65px',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '4px',
                  color: '#fff',
                  padding: '0.25rem 0.5rem',
                  fontSize: '0.8rem',
                }}
              />
            </div>
          </div>

          <button
            className="generate-btn"
            onClick={handleGenerateClick}
            disabled={isGenerating || !prompt.trim()}
            id="generate-button"
          >
            {isGenerating ? (
              <>
                <div className="spinner"></div>
                Generating...
              </>
            ) : (
              <>
                <span>🚀</span> Generate Scene
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
