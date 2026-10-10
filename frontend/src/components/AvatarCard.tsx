'use client';

import React from 'react';
import { Character } from '../lib/types';

interface AvatarCardProps {
  character: Character;
  isSelected: boolean;
  onSelect: (character: Character) => void;
}

export const AvatarCard: React.FC<AvatarCardProps> = ({ character, isSelected, onSelect }) => {
  const portraitUrl = character.canonical_portrait_url || `/assets/characters/${character.character_id}/portrait.png`;

  return (
    <div
      className={`avatar-card ${isSelected ? 'active' : ''}`}
      onClick={() => onSelect(character)}
      id={`avatar-card-${character.character_id}`}
    >
      <div className="avatar-thumb-wrapper">
        <img
          src={portraitUrl}
          alt={character.name}
          className="avatar-thumb"
          loading="lazy"
        />
      </div>
      <div className="avatar-info">
        <div className="avatar-name-row">
          <span className="avatar-name">{character.name}</span>
          <span className="avatar-version-pill">v{character.version}</span>
        </div>
        <div className="avatar-meta">
          {character.gender} • {character.age_range}
        </div>
      </div>
    </div>
  );
};
