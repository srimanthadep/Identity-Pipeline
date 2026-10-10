# 10-Avatar Character Identity Studio — Architecture & Design

## 1. Executive Summary

The **Character Identity Studio** addresses identity drift in India-centric generative video pipelines. Inspired by the persistent character workflows of **Higgsfield Soul ID**, our system decouples identity conditioning from scene generation by orchestrating:
1. Canonical identity registry (10 predefined Indian avatars with rich visual traits and canonical reference portraits)
2. Immutable VideoBlueprint construction with verified **Wan 2.2** parameters
3. Strict **Version Pinning** on generation jobs and retries to eliminate silent asset drift
4. Dual-mode generation adapters (honest watermarked local simulation and optional Fal.ai Wan 2.2 integration)
5. Automated simulated quality assurance (QA) and bounded retry loops.

---

## 2. Higgsfield Soul ID Analysis: Verified Fact vs. Architectural Parallels

```
┌────────────────────────────────────────────────────────┐
│               HIGGSFIELD SOUL ID PARADIGM              │
│  20-80 Photos ──> Fast Training ──> Persistent Soul ID │
│                                             │          │
│                                             ▼          │
│                              Consistent Video Generation│
└────────────────────────────────────────────────────────┘
```

### 2.1 Verified Observable Behavior
- Requires 20-80 diverse, high-quality reference portraits.
- Training completes in minutes to produce a reusable identity ID.
- Selecting the Soul ID maintains facial features across varied scene prompts and camera angles.
- Higgsfield describes foundation as diffusion-transformer based.

### 2.2 Our Implementation Strategy
Rather than claiming to duplicate Higgsfield's proprietary internal fine-tuning, our system delivers the **exact user experience**:
- Pre-curated canonical identities assigned persistent IDs (`char_01_priya` ... `char_10_aditya`).
- Fixed prompt-level identity blocks + image-to-video reference conditioning.
- **Wan 2.2 Image-to-Video** conditioning (`fal-ai/wan/v2.2-a14b/image-to-video`) directly accepts reference images as initial visual anchor.
- `enable_prompt_expansion: false` is enforced to prevent LLM prompt expanders from modifying or hallucinating character appearance.

---

## 3. Data Model & Version Pinning Architecture

A critical vulnerability in generative asset pipelines is **silent drift**: if an administrator replaces an avatar's portrait image or tweaks metadata, existing generation jobs or ongoing retries might silently pull the new asset, corrupting reproducibility.

```
       ┌────────────────────────┐
       │   characters (v1)      │
       └───────────┬────────────┘
                   │ 1:N
       ┌───────────▼────────────┐
       │ character_assets (v1)  │
       └───────────┬────────────┘
                   │
    [Job Creation Snapshot]
                   ▼
┌──────────────────────────────────────┐
│        generation_jobs               │
│ - character_id                       │
│ - character_version = 1  [PINNED]    │
│ - reference_asset_id                 │
│ - reference_asset_version = 1 [PIN]  │
│ - reference_asset_uri [SNAPSHOT]     │
│ - video_blueprint [IMMUTABLE JSON]   │
│ - retry_count / max_retries          │
│ - is_simulated                       │
└──────────────────┬───────────────────┘
                   │
                   ▼ (1:N)
┌──────────────────────────────────────┐
│           qa_reports                 │
│ - identity_score                     │
│ - appearance_score                   │
│ - decision: PASS | FAIL | REVIEW     │
│ - is_simulated                       │
└──────────────────────────────────────┘
```

### Version Pinning Invariant
1. **At Creation**: `generation_jobs` captures the exact `character_version` and `reference_asset_version` alongside a frozen snapshot of `reference_asset_uri`.
2. **On Character/Asset Updates**: The source tables increment their versions (`v2`, `v3`). All previously created generation jobs remain strictly pinned to `v1`.
3. **On Retries**: The retry routine (`POST /generations/{id}/retry`) re-executes using the job's pinned version attributes without querying the latest version of the character.

---

## 4. Wan 2.2 Verified Parameters on Fal.ai

Our blueprint generator reflects the official schema for `fal-ai/wan/v2.2-a14b/image-to-video`:

| Parameter | Value | Rationale |
|:----------|:------|:----------|
| `prompt` | Identity + Scene | Combined immutable identity block + scene description |
| `image_url` | Canonical portrait URI | Visual anchor for Image-to-Video conditioning |
| `num_frames` | `81` | Official default (~5.06 seconds at 16fps) |
| `frames_per_second` | `16` | Official standard output frame rate |
| `resolution` | `"720p"` | Official default high-definition resolution |
| `num_inference_steps` | `27` | Official verified step count |
| `guidance_scale` | `3.5` | Official default balance between prompt adherence & quality |
| `enable_prompt_expansion` | `false` | **Mandatory False**: Prevents LLM re-writing of identity traits |
| `acceleration` | `"regular"` | High-quality inference mode |

---

## 5. Honest Simulation Labelling

To prevent confusing simulated outputs with real AI video inference:
1. **Visual Watermark**: Every frame synthesized by `SimulatedAdapter` includes a bright red/white top banner `[SIMULATED SYNTHESIS] - IDENTITY PIPELINE DEMO` and amber `[SIMULATED]` badge.
2. **Database Metadata**: `is_simulated = 1` stored in `generation_jobs` and `qa_reports`.
3. **API Contracts**: JSON payloads return `"is_simulated": true`.
4. **Frontend Badges**: Clearly styled amber badge `⚠️ SIMULATED PASS (0.92)` versus green `✓ PASS (0.92)` for real runs.
