# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run dev server (port 8000)
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Seed the food density database (run once after init)
cd backend && python seed_data.py

# Run all tests
cd backend && python -m pytest tests/ -v

# Run a single test file
cd backend && python -m pytest tests/test_recognize.py -v
```

### Frontend (React/Vite/TypeScript)

```bash
# Install dependencies
cd frontend && npm install

# Run dev server (port 5173, proxies /api to localhost:8000)
cd frontend && npm run dev

# Type-check and build
cd frontend && npm run build

# Lint
cd frontend && npm run lint
```

## Architecture

**Food Calorie Photo App** — users take 3 multi-angle photos of a meal, the app estimates food weight via 3D reconstruction and calculates calories via density lookup.

```
React SPA (mobile-first, iOS-style light theme)
    │  REST JSON + multipart/form-data
    ▼
FastAPI Backend (main.py)
    ├── routers/upload.py      POST /api/upload
    ├── routers/recognize.py   POST /api/recognize
    ├── routers/meals.py       POST/GET/DELETE /api/meals
    ├── routers/stats.py       GET /api/stats
    ├── routers/foods.py       GET /api/foods/search
    ├── routers/profile.py     GET/PUT /api/profile
    ├── engine/                Weight estimation pipeline
    │   ├── feature_matching.py  SIFT keypoints + FLANN matching
    │   ├── reconstruction.py    Triangulation → sparse 3D → convex hull volume
    │   └── weight.py            Volume × density → weight & calories
    ├── ai/
    │   ├── classifier.py        ONNX MobileNetV3 (50 Chinese foods), simulated fallback
    │   └── fallback.py          Anthropic Vision API fallback for confidence < 0.7
    ├── database.py              SQLite with row_factory = Row
    ├── models.py                Pydantic models (shared request/response shapes)
    └── seed_data.py             50+ Chinese/international foods in food_density table
```

**Weight estimation pipeline:** upload 2-3 images → SIFT feature extraction → FLANN matching across pairs → triangulatePoints → filter outliers → convex hull area × Z-depth → volume (cm³) → ONNX classification → (if confidence < 0.7, Vision API fallback) → density DB lookup → weight = volume × density → calories = weight × cal_per_100g / 100

**Frontend pages:** Today (calorie ring + meal cards) → Capture (3-step guided photo) → Result (food breakdown + macros) → History (calendar + list). Profile page with BMR/TDEE calculation (Mifflin-St Jeor). Tab bar at bottom for navigation.

**Database:** SQLite (`backend/calorie.db`), auto-created on startup. Tables: `food_density`, `meals`, `food_items`, `user_profiles`. No migrations — `CREATE TABLE IF NOT EXISTS` in `init_db()`.

**User system:** Simple name-based, no auth. Frontend hardcodes `default_user` as the user ID. Profile stores gender/age/height/weight/activity_level for BMR/TDEE.

## Key Conventions

- Vite dev server proxies `/api/*` to `http://localhost:8000` — run both servers for full-stack dev
- Frontend types (`types.ts`) mirror backend Pydantic models (`models.py`) — keep them in sync
- ONNX model file goes at `backend/models/food_classifier.onnx`; if absent, classifier uses a deterministic hash-based simulation
- Tests are standard pytest files in `backend/tests/`, each testing the corresponding router/engine/ai module
- Uploaded images go to `backend/uploads/` (gitignored)
- The SIFT algorithm requires `opencv-contrib-python` (not plain `opencv-python`)
