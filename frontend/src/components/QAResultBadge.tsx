'use client';

import React from 'react';
import { QAReport } from '../lib/types';

interface QAResultBadgeProps {
  report: QAReport | null;
  onRetry?: () => void;
  isRetrying?: boolean;
}

export const QAResultBadge: React.FC<QAResultBadgeProps> = ({ report, onRetry, isRetrying }) => {
  if (!report) return null;

  const isSim = report.is_simulated;
  const decision = report.decision;
  const score = report.identity_score ? report.identity_score.toFixed(2) : 'N/A';

  let badgeClass = 'simulated-pass';
  let badgeLabel = '';

  if (isSim) {
    if (decision === 'PASS') {
      badgeClass = 'simulated-pass';
      badgeLabel = `⚠️ SIMULATED PASS (${score})`;
    } else if (decision === 'FAIL') {
      badgeClass = 'simulated-fail';
      badgeLabel = `⚠️ SIMULATED FAIL (${score})`;
    } else {
      badgeClass = 'review';
      badgeLabel = `⚠️ SIMULATED REVIEW (${score})`;
    }
  } else {
    if (decision === 'PASS') {
      badgeClass = 'real-pass';
      badgeLabel = `✓ PASS (${score})`;
    } else if (decision === 'FAIL') {
      badgeClass = 'simulated-fail';
      badgeLabel = `✗ FAIL (${score})`;
    } else {
      badgeClass = 'review';
      badgeLabel = `! REVIEW (${score})`;
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', flexWrap: 'wrap', gap: '0.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span className={`qa-status-pill ${badgeClass}`} id="qa-decision-badge">
          {badgeLabel}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Facial Similarity: <strong style={{ color: '#fff' }}>{report.identity_score?.toFixed(3) || '—'}</strong> | Appearance: <strong style={{ color: '#fff' }}>{report.appearance_score?.toFixed(3) || '—'}</strong>
        </span>
      </div>

      {decision === 'FAIL' && onRetry && (
        <button
          onClick={onRetry}
          disabled={isRetrying}
          className="preset-btn"
          style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#fca5a5', borderColor: '#ef4444' }}
        >
          {isRetrying ? 'Retrying...' : '↻ Bounded Retry (Pinned Versions)'}
        </button>
      )}
    </div>
  );
};
