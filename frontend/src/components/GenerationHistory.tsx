'use client';

import React from 'react';
import { GenerationJob } from '../lib/types';

interface GenerationHistoryProps {
  jobs: GenerationJob[];
  selectedJobId?: string;
  onSelectJob: (job: GenerationJob) => void;
}

export const GenerationHistory: React.FC<GenerationHistoryProps> = ({
  jobs,
  selectedJobId,
  onSelectJob,
}) => {
  return (
    <div className="glass-panel" id="generation-history-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span>📜</span> Identity History
        </div>
        <span className="panel-badge">{jobs.length} Runs</span>
      </div>

      {jobs.length === 0 ? (
        <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', fontStyle: 'italic', padding: '1rem 0' }}>
          No generation history for this avatar yet.
        </div>
      ) : (
        <div className="history-list">
          {jobs.map((j) => {
            const latestQA = j.qa_reports && j.qa_reports.length > 0 ? j.qa_reports[j.qa_reports.length - 1] : null;
            return (
              <div
                key={j.id}
                className={`history-item ${selectedJobId === j.id ? 'active' : ''}`}
                onClick={() => onSelectJob(j)}
              >
                <div className="history-item-top">
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {j.status === 'COMPLETED' ? '✓ Completed' : j.status}
                  </span>
                  {latestQA && (
                    <span style={{
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      color: latestQA.decision === 'PASS' ? '#fef08a' : '#fca5a5',
                    }}>
                      {j.is_simulated ? 'SIM ' : ''}{latestQA.decision} ({latestQA.identity_score?.toFixed(2)})
                    </span>
                  )}
                </div>

                <div className="history-prompt">
                  "{j.scene_prompt.length > 55 ? j.scene_prompt.slice(0, 52) + '...' : j.scene_prompt}"
                </div>

                <div className="history-pins">
                  <span className="pin-tag">Char v{j.character_version}</span>
                  <span className="pin-tag">Asset v{j.reference_asset_version}</span>
                  {j.retry_count > 0 && (
                    <span className="pin-tag" style={{ color: '#f59e0b' }}>Retry #{j.retry_count}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
