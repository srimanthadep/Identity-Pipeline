# API Reference — Character Identity Studio

Base URL: `http://localhost:8000/api/v1`

---

## 1. Health

### `GET /health`
Returns system status and configuration summary.

**Response (200 OK):**
```json
{
  "status": "ok",
  "project": "10-Avatar Character Identity Studio",
  "version": "1.0.0",
  "default_adapter": "simulated",
  "database": "sqlite"
}
```

---

## 2. Character Registry

### `GET /characters`
Returns all 10 canonical avatars with metadata and portrait URLs.

**Response (200 OK):**
```json
[
  {
    "id": "e9634e2c-3965-4f3d-82d2-8b43fb4eef93",
    "character_id": "char_01_priya",
    "name": "Priya",
    "description": "Young Indian corporate professional; sharp, poised, and approachable.",
    "physical_traits": {
      "skin_tone": "Warm golden-brown",
      "hair_color": "Deep black",
      "hair_style": "Long wavy locks falling over shoulders",
      "eye_color": "Warm dark brown",
      "facial_features": "High cheekbones, bright expressive eyes, warm engaging smile",
      "default_attire": "Navy blue blazer with fine Indian embroidery accents",
      "distinguishing_marks": "Small gold hoop earrings"
    },
    "gender": "Female",
    "age_range": "22-28",
    "version": 1,
    "created_at": "2026-10-10T10:09:50.423456+00:00",
    "updated_at": "2026-10-10T10:09:50.423456+00:00",
    "canonical_portrait_url": "/assets/characters/char_01_priya/portrait.png"
  }
]
```

### `GET /characters/{character_id}`
Returns detailed character record including all registered assets.
`character_id` can be the UUID or the human-readable slug (`char_01_priya`).

---

## 3. Video Generations

### `POST /generations`
Creates a new generation job with version pinning.

**Query Parameters:**
- `run_sync` (boolean, optional, default: false): If true, runs execution immediately in-band instead of background task.

**Request Body:**
```json
{
  "character_id": "char_01_priya",
  "scene_prompt": "Giving a keynote presentation at a Bengaluru AI summit",
  "adapter_type": "simulated",
  "seed": 42,
  "max_retries": 3
}
```

**Response (201 Created):**
```json
{
  "id": "848b64e5-4ae2-45e6-bd69-65fe2b7ad5bc",
  "character_id": "e9634e2c-3965-4f3d-82d2-8b43fb4eef93",
  "character_version": 1,
  "reference_asset_id": "2d1421ab-6421-4fa3-9e5b-b99b5e39682b",
  "reference_asset_version": 1,
  "reference_asset_uri": "characters/char_01_priya/portrait.png",
  "scene_prompt": "Giving a keynote presentation at a Bengaluru AI summit",
  "adapter_type": "simulated",
  "status": "PENDING",
  "retry_count": 0,
  "max_retries": 3,
  "is_simulated": true,
  "video_blueprint": {
    "character_id": "char_01_priya",
    "identity_block": { ... },
    "scene_block": { ... },
    "generation_params": {
      "num_frames": 81,
      "frames_per_second": 16,
      "resolution": "720p",
      "guidance_scale": 3.5,
      "enable_prompt_expansion": false
    }
  }
}
```

### `GET /generations/{job_id}`
Returns generation status, output URI, and version pins.

### `GET /generations/{job_id}/qa`
Returns QA reports for the job with identity score and PASS/FAIL/REVIEW decision.

### `POST /generations/{job_id}/retry`
Triggers a bounded retry for a failed job. Reuses the exact pinned `character_version` and `reference_asset_version`.

### `GET /generations/by-character/{character_id}`
Returns all generation history for a specific character.
