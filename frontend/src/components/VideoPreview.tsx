'use client';

import React from 'react';
import { GenerationJob } from '../lib/types';
import { QAResultBadge } from './QAResultBadge';

interface VideoPreviewProps {
  job: GenerationJob | null;
  isLoading: boolean;
  onRetry?: () => void;
  isRetrying?: boolean;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({
  job,
  isLoading,
  onRetry,
  isRetrying,
}) => {
  const latestQA = job?.qa_reports && job.qa_reports.length > 0
    ? job.qa_reports[job.qa_reports.length - 1]
    : null;

  return (
    <div className="glass-panel" id="generation-output-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span>🎬</span> Generated Synthesis
        </div>
        {job && (
          <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
            <span className="pin-tag">Char v{job.character_version}</span>
            <span className="pin-tag">Asset v{job.reference_asset_version}</span>
            <span className="panel-badge">{job.adapter_type}</span>
          </div>
        )}
      </div>

      <div className="output-display">
        {isLoading || job?.status === 'RUNNING' || job?.status === 'PENDING' ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <div className="spinner" style={{ width: '32px', height: '32px', borderWidth: '3px', borderTopColor: 'var(--accent-amber)' }}></div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {job?.status === 'RUNNING' ? 'Synthesizing scene frames with identity conditioning...' : 'Queued in generation pipeline...'}
            </p>
          </div>
        ) : job?.output_url ? (
          <div style={{ position: 'relative', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {job.is_simulated && (
              <div className="simulated-banner-badge">
                <span>⚠️ [SIMULATED SYNTHESIS]</span>
              </div>
            )}
            <img
              src={job.output_url}
              alt="Generated scene output"
              className="output-media"
            />
          </div>
        ) : (
          <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '2rem' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📽️</div>
            <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)' }}>No generation yet</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Select an avatar, enter a prompt, and click Generate Scene</p>
          </div>
        )}
      </div>

      {latestQA && (
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.85rem' }}>
          <QAResultBadge report={latestQA} onRetry={onRetry} isRetrying={isRetrying} />
        </div>
      )}
    </div>
  );
};
