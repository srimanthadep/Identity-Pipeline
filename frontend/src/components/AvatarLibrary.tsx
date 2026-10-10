'use client';

import React, { useState } from 'react';
import { Character } from '../lib/types';
import { AvatarCard } from './AvatarCard';

interface AvatarLibraryProps {
  characters: Character[];
  selectedCharacter: Character | null;
  onSelectCharacter: (character: Character) => void;
}

export const AvatarLibrary: React.FC<AvatarLibraryProps> = ({
  characters,
  selectedCharacter,
  onSelectCharacter,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = characters.filter((c) =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.character_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.gender && c.gender.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="glass-panel" id="avatar-library-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span>👥</span> Avatar Library
        </div>
        <span className="panel-badge">{characters.length} Canonical</span>
      </div>

      <input
        type="text"
        placeholder="Filter by name, gender..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{
          width: '100%',
          padding: '0.6rem 0.85rem',
          background: 'rgba(0, 0, 0, 0.4)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--text-main)',
          fontSize: '0.8rem',
          outline: 'none',
        }}
      />

      <div className="avatar-grid">
        {filtered.map((character) => (
          <AvatarCard
            key={character.id}
            character={character}
            isSelected={selectedCharacter?.id === character.id}
            onSelect={onSelectCharacter}
          />
        ))}
      </div>
    </div>
  );
};
