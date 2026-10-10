'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Character, GenerationJob } from '../lib/types';
import {
  fetchCharacters,
  fetchCharacterDetail,
  fetchCharacterGenerations,
  createGenerationJob,
  getGenerationJob,
  retryGenerationJob,
} from '../lib/api';
import { AvatarLibrary } from '../components/AvatarLibrary';
import { CharacterIdentityPanel } from '../components/CharacterIdentityPanel';
import { GenerateScene } from '../components/GenerateScene';
import { VideoPreview } from '../components/VideoPreview';
import { BlueprintPreview } from '../components/BlueprintPreview';
import { GenerationHistory } from '../components/GenerationHistory';

export default function Home() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [currentJob, setCurrentJob] = useState<GenerationJob | null>(null);
  const [historyJobs, setHistoryJobs] = useState<GenerationJob[]>([]);
  const [loadingCharacters, setLoadingCharacters] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState('Walking across Marine Drive in Mumbai at golden hour with sea breeze');

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 1. Initial Load: Fetch Characters
  useEffect(() => {
    async function init() {
      try {
        const chars = await fetchCharacters();
        setCharacters(chars);
        if (chars.length > 0) {
          const detail = await fetchCharacterDetail(chars[0].character_id);
          setSelectedCharacter(detail);
        }
      } catch (err) {
        console.error('Failed to load characters:', err);
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

  // Poll job status until done
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

          // Refresh history
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

  // Handle Generation Trigger
  const handleGenerate = async (prompt: string, adapterType: string, seed?: number) => {
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

  // Handle Retry Trigger
  const handleRetry = async () => {
    if (!currentJob) return;
    setIsRetrying(true);

    try {
      const retried = await retryGenerationJob(currentJob.id);
      setCurrentJob(retried);
      // If completed immediately, refresh
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

  if (loadingCharacters) {
    return (
      <div style={{ display: 'flex', height: '80vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
        <div className="spinner" style={{ width: '36px', height: '36px', borderTopColor: 'var(--accent-amber)' }}></div>
        <p style={{ color: 'var(--text-muted)' }}>Initializing Character Identity Studio...</p>
      </div>
    );
  }

  // Live Blueprint Calculation
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

      {/* 2. Middle Column: Character Panel & Generation Studio */}
      <section className="center-stage">
        {selectedCharacter && (
          <>
            <CharacterIdentityPanel character={selectedCharacter} />
            <GenerateScene
              selectedCharacter={selectedCharacter}
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
              onPromptChange={setCurrentPrompt}
            />
            <VideoPreview
              job={currentJob}
              isLoading={isGenerating}
              onRetry={handleRetry}
              isRetrying={isRetrying}
            />
          </>
        )}
      </section>

      {/* 3. Right Column: Blueprint Preview & Generation History */}
      <aside className="studio-right-panel">
        <BlueprintPreview
          currentJob={currentJob}
          liveBlueprint={liveBlueprint}
        />
        <GenerationHistory
          jobs={historyJobs}
          selectedJobId={currentJob?.id}
          onSelectJob={(j) => setCurrentJob(j)}
        />
      </aside>
    </div>
  );
}
