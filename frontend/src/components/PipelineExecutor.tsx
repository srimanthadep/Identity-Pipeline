'use client';

import React, { useState } from 'react';
import { PipelineRun } from '../lib/types';

interface PipelineExecutorProps {
  pipeline: PipelineRun | null;
  onExecute: (adapterType: string, seed?: number) => void;
  isExecuting: boolean;
}

export function PipelineExecutor({ pipeline, onExecute, isExecuting }: PipelineExecutorProps) {
  const [adapterType, setAdapterType] = useState('simulated');
  const [seed, setSeed] = useState<number>(42);

  if (!pipeline) return null;

  const totalScenes = pipeline.total_scenes || (pipeline.blueprint ? pipeline.blueprint.total_scenes : 0);
  const completedScenes = pipeline.completed_scenes || 0;
  const progressPercent = totalScenes > 0 ? Math.round((completedScenes / totalScenes) * 100) : 0;

  const isCompleted = pipeline.status === 'COMPLETED';

  return (
    <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>⚡</span> Execute Multi-Scene Video Pipeline
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.2rem' }}>
            Generates each scene sequentially with Wan I2V conditioning on the same canonical portrait.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{
            padding: '0.35rem 0.75rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.75rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            background: isCompleted ? 'rgba(16, 185, 129, 0.15)' : isExecuting ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 255, 255, 0.05)',
            border: isCompleted ? '1px solid #10b981' : isExecuting ? '1px solid #f59e0b' : '1px solid var(--border-subtle)',
            color: isCompleted ? '#34d399' : isExecuting ? '#fbbf24' : 'var(--text-muted)',
          }}>
            Status: {pipeline.status}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
          <span>Generation Progress: {completedScenes} / {totalScenes} Scenes</span>
          <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{progressPercent}%</span>
        </div>
        <div style={{
          width: '100%',
          height: '8px',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(255, 255, 255, 0.06)',
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${progressPercent}%`,
            height: '100%',
            background: isCompleted
              ? 'linear-gradient(90deg, #10b981, #059669)'
              : 'linear-gradient(90deg, #f59e0b, #d97706)',
            borderRadius: 'var(--radius-full)',
            transition: 'width 0.4s ease',
          }}></div>
        </div>
      </div>

      {/* Version Pinning Audit Box */}
      <div style={{
        padding: '0.85rem 1rem',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(10, 15, 28, 0.8)',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        marginBottom: '1.25rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span>🔒</span> Multi-Scene Version Pinning Verification
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            All {totalScenes} scenes locked to: <strong>character_version = {pipeline.character_version}</strong> • <strong>reference_asset_version = 1</strong>
          </div>
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
          Anti-Drift Guarantee Active
        </div>
      </div>

      {/* Control Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>Adapter:</label>
            <select
              value={adapterType}
              onChange={(e) => setAdapterType(e.target.value)}
              disabled={isExecuting}
              style={{
                padding: '0.45rem 0.75rem',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(18, 25, 43, 0.9)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-main)',
                fontSize: '0.85rem',
              }}
            >
              <option value="simulated">Simulated Adapter (Demo / Instant)</option>
              <option value="wan_i2v">Live Wan 2.2 (Fal.ai)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>Random Seed:</label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value) || 0)}
              disabled={isExecuting}
              style={{
                width: '90px',
                padding: '0.45rem 0.6rem',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(18, 25, 43, 0.9)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-main)',
                fontSize: '0.85rem',
              }}
            />
          </div>
        </div>

        <button
          onClick={() => onExecute(adapterType, seed)}
          disabled={isExecuting}
          style={{
            padding: '0.8rem 2rem',
            borderRadius: 'var(--radius-md)',
            background: isExecuting
              ? 'rgba(245, 158, 11, 0.4)'
              : 'linear-gradient(135deg, #10b981, #059669)',
            border: 'none',
            color: '#ffffff',
            fontWeight: 700,
            fontSize: '0.95rem',
            cursor: isExecuting ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)',
            transition: 'all 0.2s ease',
          }}
        >
          {isExecuting ? (
            <>
              <span className="spinner" style={{ width: '16px', height: '16px', borderTopColor: '#ffffff' }}></span>
              Generating Scene {completedScenes + 1} of {totalScenes}...
            </>
          ) : isCompleted ? (
            <>
              <span>🔄</span> Re-Execute All Scenes
            </>
          ) : (
            <>
              <span>🎬</span> Execute All Scenes ({totalScenes} clips)
            </>
          )}
        </button>
      </div>

      {/* Honest simulated notice */}
      {adapterType === 'simulated' && (
        <div style={{
          marginTop: '1rem',
          padding: '0.5rem 0.75rem',
          borderRadius: 'var(--radius-sm)',
          background: 'var(--simulated-badge-bg)',
          border: '1px solid var(--simulated-badge-border)',
          color: 'var(--simulated-badge-text)',
          fontSize: '0.75rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}>
          <span>ℹ️</span>
          <span>
            <strong>Simulated Mode Active:</strong> Output images have watermark <code>[SIMULATED - DEMO]</code> and QA results are calculated deterministically for testing without GPU costs.
          </span>
        </div>
      )}
    </div>
  );
}
