'use client';

import React from 'react';
import { Character } from '../lib/types';

interface CharacterIdentityPanelProps {
  character: Character;
}

export const CharacterIdentityPanel: React.FC<CharacterIdentityPanelProps> = ({ character }) => {
  const portraitUrl = character.canonical_portrait_url || `/assets/characters/${character.character_id}/portrait.png`;
  const traits = character.physical_traits || {};

  return (
    <div className="glass-panel" id="character-identity-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span>🧬</span> Character Identity Layer
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span className="pill-badge engine">Soul ID Ready</span>
          <span className="panel-badge">Version {character.version}</span>
        </div>
      </div>

      <div className="profile-hero">
        <img
          src={portraitUrl}
          alt={character.name}
          className="profile-portrait-large"
        />

        <div className="profile-details">
          <div className="profile-title-row">
            <h2 className="profile-name">{character.name}</h2>
            <span className="identity-slug">{character.character_id}</span>
          </div>

          <p className="profile-desc">{character.description}</p>

          <div className="trait-tags-row">
            {Object.entries(traits).map(([key, val]) => (
              <span key={key} className="trait-tag">
                <strong>{key.replace('_', ' ')}:</strong> {val}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
