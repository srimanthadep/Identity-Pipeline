'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Character, GenerationJob, PipelinePlanResponse, PipelineRun } from '../lib/types';
import {
  fetchCharacters,
  fetchCharacterDetail,
  fetchCharacterGenerations,
  createGenerationJob,
  getGenerationJob,
  retryGenerationJob,
  planPipeline,
  executePipeline,
  getPipeline,
  listPipelineRuns,
} from '../lib/api';
import { AvatarLibrary } from '../components/AvatarLibrary';
import { CharacterIdentityPanel } from '../components/CharacterIdentityPanel';
import { GenerateScene } from '../components/GenerateScene';
import { VideoPreview } from '../components/VideoPreview';
import { BlueprintPreview } from '../components/BlueprintPreview';
import { GenerationHistory } from '../components/GenerationHistory';
import { PromptInput } from '../components/PromptInput';
import { SceneBlueprintViewer } from '../components/SceneBlueprintViewer';
import { PipelineExecutor } from '../components/PipelineExecutor';
import { SceneResults } from '../components/SceneResults';

export default function Home() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [loadingCharacters, setLoadingCharacters] = useState(true);

  // Studio Mode: 'pipeline' (Multi-scene Gemini -> Wan I2V) vs 'single' (Quick single-shot)
  const [activeMode, setActiveMode] = useState<'pipeline' | 'single'>('pipeline');

  // Single-Scene State
  const [currentJob, setCurrentJob] = useState<GenerationJob | null>(null);
  const [historyJobs, setHistoryJobs] = useState<GenerationJob[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState('Walking across Marine Drive in Mumbai at golden hour with sea breeze');

  // Pipeline State
  const [isPlanning, setIsPlanning] = useState(false);
  const [isExecutingPipeline, setIsExecutingPipeline] = useState(false);
  const [pipelinePlan, setPipelinePlan] = useState<PipelinePlanResponse | null>(null);
  const [currentPipeline, setCurrentPipeline] = useState<PipelineRun | null>(null);
  const [pipelineRunsList, setPipelineRunsList] = useState<PipelineRun[]>([]);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 1. Initial Load: Fetch Characters & Pipeline Runs
  useEffect(() => {
    async function init() {
      try {
        const [chars, runs] = await Promise.all([
          fetchCharacters(),
          listPipelineRuns().catch(() => []),
        ]);
        setCharacters(chars);
        setPipelineRunsList(runs);
        if (chars.length > 0) {
          const detail = await fetchCharacterDetail(chars[0].character_id);
          setSelectedCharacter(detail);
        }
        if (runs.length > 0) {
          setCurrentPipeline(runs[0]);
        }
      } catch (err) {
        console.error('Failed to load initial data:', err);
      } finally {
        setLoadingCharacters(false);
      }
    }
    init();
  }, []);

  // 2. Fetch history when selected character changes
  useEffect(() => {
    if (!selectedCharacter) return;
    async function loadHistory() {
      try {
        const hist = await fetchCharacterGenerations(selectedCharacter!.id);
        setHistoryJobs(hist);
        if (hist.length > 0 && !isGenerating) {
          setCurrentJob(hist[0]);
        } else if (!isGenerating) {
          setCurrentJob(null);
        }
      } catch (err) {
        console.error('Failed to load history:', err);
      }
    }
    loadHistory();
  }, [selectedCharacter]);

  // Clean up polling interval
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  // Handle Character Selection
  const handleSelectCharacter = async (char: Character) => {
    try {
      const detail = await fetchCharacterDetail(char.character_id);
      setSelectedCharacter(detail);
    } catch (e) {
      setSelectedCharacter(char);
    }
  };

  // Poll single job status until done
  const pollJobStatus = (jobId: string) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    pollIntervalRef.current = setInterval(async () => {
      try {
        const updated = await getGenerationJob(jobId);
        setCurrentJob(updated);

        if (updated.status === 'COMPLETED' || updated.status === 'FAILED') {
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
          setIsGenerating(false);
          setIsRetrying(false);

          if (selectedCharacter) {
            const hist = await fetchCharacterGenerations(selectedCharacter.id);
            setHistoryJobs(hist);
          }
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
        setIsGenerating(false);
        setIsRetrying(false);
      }
    }, 1000);
  };

  // Handle Single Generation Trigger
  const handleGenerateSingle = async (prompt: string, adapterType: string, seed?: number) => {
    if (!selectedCharacter) return;
    setIsGenerating(true);

    try {
      const newJob = await createGenerationJob({
        character_id: selectedCharacter.id,
        scene_prompt: prompt,
        adapter_type: adapterType,
        seed: seed,
        max_retries: 3,
      });

      setCurrentJob(newJob);
      pollJobStatus(newJob.id);
    } catch (err: any) {
      alert(`Generation failed: ${err.message}`);
      setIsGenerating(false);
    }
  };

  // Handle Single Retry Trigger
  const handleRetrySingle = async () => {
    if (!currentJob) return;
    setIsRetrying(true);

    try {
      const retried = await retryGenerationJob(currentJob.id);
      setCurrentJob(retried);
      if (retried.status === 'COMPLETED' || retried.status === 'FAILED') {
        setIsRetrying(false);
        if (selectedCharacter) {
          const hist = await fetchCharacterGenerations(selectedCharacter.id);
          setHistoryJobs(hist);
        }
      } else {
        pollJobStatus(retried.id);
      }
    } catch (err: any) {
      alert(`Retry failed: ${err.message}`);
      setIsRetrying(false);
    }
  };

  // Handle Pipeline Blueprint Planning Trigger
  const handlePlanPipeline = async (prompt: string) => {
    if (!selectedCharacter) return;
    setIsPlanning(true);
    try {
      const plan = await planPipeline({
        character_id: selectedCharacter.character_id,
        user_prompt: prompt,
      });
      setPipelinePlan(plan);

      // Fetch the full run object
      const fullRun = await getPipeline(plan.pipeline_id);
      setCurrentPipeline(fullRun);

      // Refresh recent runs list
      const runs = await listPipelineRuns();
      setPipelineRunsList(runs);
    } catch (err: any) {
      alert(`Pipeline planning failed: ${err.message}`);
    } finally {
      setIsPlanning(false);
    }
  };

  // Handle Pipeline Full Execution Trigger
  const handleExecutePipeline = async (adapterType: string, seed?: number) => {
    if (!currentPipeline) return;
    setIsExecutingPipeline(true);
    try {
      const executed = await executePipeline(currentPipeline.id, {
        adapter_type: adapterType,
        seed: seed,
        max_retries: 3,
      });
      setCurrentPipeline(executed);

      // Refresh runs list
      const runs = await listPipelineRuns();
      setPipelineRunsList(runs);
    } catch (err: any) {
      alert(`Pipeline execution failed: ${err.message}`);
    } finally {
      setIsExecutingPipeline(false);
    }
  };

  // Handle Selecting a Previous Pipeline Run from History
  const handleSelectPipelineRun = async (run: PipelineRun) => {
    try {
      const full = await getPipeline(run.id);
      setCurrentPipeline(full);
      // Switch selected character if needed
      const matchingChar = characters.find(c => c.character_id === full.character_id || c.id === full.character_id);
      if (matchingChar) {
        const detail = await fetchCharacterDetail(matchingChar.character_id);
        setSelectedCharacter(detail);
      }
    } catch (e) {
      setCurrentPipeline(run);
    }
  };

  if (loadingCharacters) {
    return (
      <div style={{ display: 'flex', height: '80vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
        <div className="spinner" style={{ width: '36px', height: '36px', borderTopColor: 'var(--accent-amber)' }}></div>
        <p style={{ color: 'var(--text-muted)' }}>Initializing Character Identity Studio...</p>
      </div>
    );
  }

  // Live Blueprint Calculation for Single-Scene preview
  const liveBlueprint = selectedCharacter ? {
    character_id: selectedCharacter.character_id,
    identity_block: {
      name: selectedCharacter.name,
      gender: selectedCharacter.gender,
      age_range: selectedCharacter.age_range,
      traits: selectedCharacter.physical_traits || {},
    },
    scene_block: {
      raw_prompt: currentPrompt,
      augmented_prompt: `[IDENTITY: ${selectedCharacter.name}, ${selectedCharacter.gender}, ${selectedCharacter.age_range}] [SCENE: ${currentPrompt}]`,
    },
    generation_params: {
      prompt: `[IDENTITY: ${selectedCharacter.name}] [SCENE: ${currentPrompt}]`,
      image_url: selectedCharacter.canonical_portrait_url || `characters/${selectedCharacter.character_id}/portrait.png`,
      num_frames: 81,
      frames_per_second: 16,
      resolution: '720p',
      guidance_scale: 3.5,
      num_inference_steps: 27,
      enable_prompt_expansion: false,
      video_quality: 'high',
      seed: 42,
    },
  } : null;

  return (
    <div className="studio-layout">
      {/* 1. Left Column: Avatar Library */}
      <aside>
        <AvatarLibrary
          characters={characters}
          selectedCharacter={selectedCharacter}
          onSelectCharacter={handleSelectCharacter}
        />
      </aside>

      {/* 2. Middle Column: Studio Stage */}
      <section className="center-stage">
        {selectedCharacter && (
          <>
            {/* Studio Mode Selector */}
            <div style={{
              display: 'flex',
              gap: '0.5rem',
              marginBottom: '1.25rem',
              padding: '0.35rem',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(10, 15, 28, 0.9)',
              border: '1px solid var(--border-subtle)',
            }}>
              <button
                onClick={() => setActiveMode('pipeline')}
                style={{
                  flex: 1,
                  padding: '0.65rem 1rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: activeMode === 'pipeline' ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(217, 119, 6, 0.15))' : 'transparent',
                  color: activeMode === 'pipeline' ? 'var(--accent-amber-light)' : 'var(--text-muted)',
                  fontWeight: activeMode === 'pipeline' ? 700 : 500,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  boxShadow: activeMode === 'pipeline' ? 'inset 0 0 0 1px rgba(245, 158, 11, 0.4)' : 'none',
                  transition: 'all 0.2s ease',
                }}
              >
                <span>🎬</span> Multi-Scene Pipeline (Gemini 3.8 Flash → Wan I2V)
              </button>
              <button
                onClick={() => setActiveMode('single')}
                style={{
                  flex: 1,
                  padding: '0.65rem 1rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: activeMode === 'single' ? 'linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(2, 132, 199, 0.15))' : 'transparent',
                  color: activeMode === 'single' ? 'var(--accent-blue)' : 'var(--text-muted)',
                  fontWeight: activeMode === 'single' ? 700 : 500,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  boxShadow: activeMode === 'single' ? 'inset 0 0 0 1px rgba(56, 189, 248, 0.4)' : 'none',
                  transition: 'all 0.2s ease',
                }}
              >
                <span>⚡</span> Single-Scene Quick Studio
              </button>
            </div>

            {/* Common Character Identity Overview Panel */}
            <CharacterIdentityPanel character={selectedCharacter} />

            {/* MODE 1: MULTI-SCENE PIPELINE */}
            {activeMode === 'pipeline' && (
              <>
                <PromptInput
                  selectedCharacter={selectedCharacter}
                  onPlan={handlePlanPipeline}
                  isPlanning={isPlanning}
                />

                {currentPipeline && currentPipeline.blueprint && (
                  <>
                    <SceneBlueprintViewer
                      blueprint={currentPipeline.blueprint}
                      character={selectedCharacter}
                    />

                    <PipelineExecutor
                      pipeline={currentPipeline}
                      onExecute={handleExecutePipeline}
                      isExecuting={isExecutingPipeline}
                    />

                    {currentPipeline.scenes && currentPipeline.scenes.length > 0 && (
                      <SceneResults
                        scenes={currentPipeline.scenes}
                        character={selectedCharacter}
                      />
                    )}
                  </>
                )}
              </>
            )}

            {/* MODE 2: SINGLE-SCENE QUICK STUDIO */}
            {activeMode === 'single' && (
              <>
                <GenerateScene
                  selectedCharacter={selectedCharacter}
                  onGenerate={handleGenerateSingle}
                  isGenerating={isGenerating}
                  onPromptChange={setCurrentPrompt}
                />
                <VideoPreview
                  job={currentJob}
                  isLoading={isGenerating}
                  onRetry={handleRetrySingle}
                  isRetrying={isRetrying}
                />
              </>
            )}
          </>
        )}
      </section>

      {/* 3. Right Column: History & Inspection */}
      <aside className="studio-right-panel">
        {activeMode === 'pipeline' ? (
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <span>📜</span> Pipeline Runs History
            </h3>

            {pipelineRunsList.length === 0 ? (
              <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>No pipeline runs planned yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '70vh', overflowY: 'auto' }}>
                {pipelineRunsList.map((run) => {
                  const isSelected = currentPipeline?.id === run.id;
                  return (
                    <div
                      key={run.id}
                      onClick={() => handleSelectPipelineRun(run)}
                      style={{
                        padding: '0.85rem',
                        borderRadius: 'var(--radius-sm)',
                        background: isSelected ? 'rgba(245, 158, 11, 0.12)' : 'rgba(15, 22, 38, 0.7)',
                        border: isSelected ? '1px solid var(--accent-amber)' : '1px solid var(--border-subtle)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-amber)' }}>
                          {run.character_name || run.character_id}
                        </span>
                        <span style={{
                          fontSize: '0.65rem',
                          padding: '2px 6px',
                          borderRadius: '3px',
                          background: run.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                          color: run.status === 'COMPLETED' ? '#34d399' : '#fbbf24',
                          fontWeight: 600,
                        }}>
                          {run.status}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.35, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {run.user_prompt}
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.5rem' }}>
                        <span>{run.total_scenes} scenes</span>
                        <span>{run.created_at ? new Date(run.created_at).toLocaleDateString() : ''}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          <>
            <BlueprintPreview
              currentJob={currentJob}
              liveBlueprint={liveBlueprint}
            />
            <GenerationHistory
              jobs={historyJobs}
              selectedJobId={currentJob?.id}
              onSelectJob={(j) => setCurrentJob(j)}
            />
          </>
        )}
      </aside>
    </div>
  );
}
