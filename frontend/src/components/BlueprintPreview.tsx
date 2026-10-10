'use client';

import React, { useState } from 'react';
import { GenerationJob } from '../lib/types';

interface BlueprintPreviewProps {
  currentJob: GenerationJob | null;
  liveBlueprint?: Record<string, any> | null;
}

export const BlueprintPreview: React.FC<BlueprintPreviewProps> = ({ currentJob, liveBlueprint }) => {
  const [copied, setCopied] = useState(false);

  const dataToDisplay = currentJob?.video_blueprint || liveBlueprint;

  const handleCopy = () => {
    if (!dataToDisplay) return;
    navigator.clipboard.writeText(JSON.stringify(dataToDisplay, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel" id="blueprint-preview-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span>📐</span> VideoBlueprint (Wan 2.2)
        </div>
        {dataToDisplay && (
          <button
            onClick={handleCopy}
            className="preset-btn"
            style={{ fontSize: '0.7rem' }}
          >
            {copied ? '✓ Copied' : 'Copy JSON'}
          </button>
        )}
      </div>

      {dataToDisplay ? (
        <pre className="blueprint-box">
          {JSON.stringify(dataToDisplay, null, 2)}
        </pre>
      ) : (
        <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', fontStyle: 'italic', padding: '1rem 0' }}>
          Select an avatar and compose a scene prompt to inspect the identity-conditioned VideoBlueprint specification.
        </div>
      )}
    </div>
  );
};
