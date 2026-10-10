# Setup & Developer Guide — Character Identity Studio

This guide explains how to install, test, and run the 10-Avatar Character Identity Studio locally.

---

## 1. Prerequisites

- **Python 3.12+** (tested on Python 3.14)
- **Node.js 18+** (tested on Node.js v24.21 with npm 11.19)
- **Git**

No external Docker containers or PostgreSQL services are required for the demo — SQLite is used out of the box.

---

## 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed 10 canonical avatars into SQLite
python -m app.seed.run_seed

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

FastAPI server runs at `http://localhost:8000`.
Interactive Swagger UI is available at `http://localhost:8000/docs`.

---

## 3. Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install

# Start Next.js development server
npm run dev
```

Next.js web application is accessible at `http://localhost:3000`.
API requests are automatically proxied through Next.js rewrites to the FastAPI server.

---

## 4. Running the Automated Test Suite

From the `backend` directory:

```bash
# Run all tests with verbose output
python -m pytest -v
```

### Test Coverage Highlights
- `test_characters.py`: Validates 10 canonical avatars, portraits on disk, and REST endpoints.
- `test_blueprint.py`: Enforces verified Wan 2.2 schema and verifies `enable_prompt_expansion: false`.
- `test_version_pinning.py`: Verifies that `character_version` and `reference_asset_version` are locked on job creation, remain intact during character updates, and persist across retries.
- `test_adapters.py`: Tests `SimulatedAdapter` watermarking and image synthesis.
- `test_qa.py`: Verifies simulated QA scoring thresholds (PASS, REVIEW, FAIL).
- `test_generation.py`: End-to-end API lifecycle from job creation to completed QA evaluation.
