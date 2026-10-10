# 10-Avatar Character Identity Studio

A persistent character identity pipeline for India-centric AI video generation, inspired by Higgsfield Soul ID and powered by Wan 2.2 / Fal.ai architecture.

---

## Overview

Character consistency across multi-scene video generation is one of the hardest challenges in generative media. The **10-Avatar Character Identity Studio** provides:

1. **Persistent Character Registry**: 10 diverse, India-centric canonical avatars with verified physical traits and canonical portraits.
2. **Version-Pinned Generation Jobs**: Every generation snapshot pins `character_version` and `reference_asset_version` ensuring reproducibility and preventing asset drift across retries.
3. **Identity Blueprinting**: Immutable identity blocks paired with scene descriptions and Wan 2.2 verified inference parameters (`enable_prompt_expansion: false`).
4. **Honest Simulation Labelling**: All simulated generations carry visible watermarks, `is_simulated = True` flags in API responses, and distinctive UI badges.
5. **Quality Assurance & Retry Loop**: Simulated identity QA scoring with automated bounded retries using pinned reference snapshots.
6. **Optional Real Wan 2.2 Generation**: Zero-cost demo mode by default, switchable to real Wan 2.2 I2V on Fal.ai with `FAL_KEY`.

---

## 10 Predefined Avatars

| # | Character ID | Name | Gender | Age | Style / Persona |
|:--|:-------------|:-----|:-------|:----|:----------------|
| 1 | `char_01_priya` | Priya | Female | 22-28 | Young professional, warm brown skin, long wavy hair |
| 2 | `char_02_arjun` | Arjun | Male | 25-32 | Athletic build, short cropped hair, strong jawline |
| 3 | `char_03_devi` | Devi | Female | 45-55 | Elegant matriarch, silver-streaked hair, traditional saree |
| 4 | `char_04_raj` | Raj | Male | 30-40 | Tech entrepreneur, neatly groomed beard, confident |
| 5 | `char_05_ananya` | Ananya | Female | 18-24 | Gen-Z student, bright eyes, curly hair, casual wear |
| 6 | `char_06_vikram` | Vikram | Male | 50-60 | Distinguished elder, salt-and-pepper hair, thoughtful |
| 7 | `char_07_meera` | Meera | Female | 28-35 | Creative artist, expressive eyes, vibrant attire |
| 8 | `char_08_kiran` | Kiran | Non-binary | 20-28 | Modern minimalist, sharp androgynous style |
| 9 | `char_09_lakshmi` | Lakshmi | Female | 35-45 | Classical dancer, expressive grace, traditional motifs |
| 10 | `char_10_aditya` | Aditya | Male | 22-30 | Outdoor adventurer, sun-bronzed, active wear |

---

## Architecture & Tech Stack

- **Backend**: FastAPI (Python 3.14 / 3.12+), SQLAlchemy 2.0, Alembic, SQLite (`data/identity_studio.db`), Pillow
- **Frontend**: Next.js (App Router), Vanilla CSS / Tailwind Modern Dark Theme
- **Inference Providers**:
  - `simulated`: Local watermarked synthesis with zero external dependencies
  - `wan_i2v`: Fal.ai Wan 2.2-A14B Image-to-Video endpoint (`fal-ai/wan/v2.2-a14b/image-to-video`)

---

## Getting Started

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix:
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
python -m app.seed.run_seed
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to access the Character Identity Studio UI.
API documentation is available at `http://localhost:8000/docs`.
