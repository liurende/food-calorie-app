# Food Calorie Photo App — Design Document

## Overview

A full-stack web app that lets users take multi-angle photos of their meals to estimate food weight and calculate calories. Target: small group use (family/fitness group), simple user differentiation, no complex account system.

## Core Challenge: Weight Estimation

The key difficulty is accurately estimating food weight from photos. The approach:

1. **Multi-angle capture** — User takes 3 photos: front view (0°), diagonal (45°), side view (90°)
2. **Feature matching** — SIFT/SuperPoint extract keypoints across the 3 images
3. **Sparse 3D reconstruction** — Triangulate matched features to build a sparse point cloud of the food surface, estimate volume (cm³) from the reconstructed shape
4. **Density lookup** — Match classified food to a density database (g/cm³)
5. **Weight = Volume × Density**

**MVP constraint:** The user is guided to hold the camera ~30cm from the food to provide a known scale reference, avoiding the need for full-scale Structure from Motion calibration.

## Tech Stack

- **Frontend:** React SPA (mobile-first, iOS-style dark UI)
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **AI:** Local ONNX classification model (MobileNetV3, 50 food classes) + Vision API fallback for ambiguous cases

## Architecture

```
React SPA (mobile-first)
    │
    ▼  REST API (JSON + multipart/form-data)
FastAPI Backend
    ├── /upload        — Receive multi-angle images
    ├── /recognize     — Trigger recognition + weight estimation
    ├── /meals          — CRUD for meal records
    ├── /stats          — Daily/weekly calorie summaries
    └── /users          — Simple user name management
            │
            ▼
    Weight Estimation Engine
        ├── Multi-view feature matching (OpenCV)
        ├── Sparse point cloud → volume
        └── Density DB → weight → calories
            │
            ▼
    AI Layer
        ├── ONNX Runtime (MobileNetV3, 50 foods)
        └── Vision API fallback (complex/mixed dishes)
            │
            ▼
    SQLite
        ├── users (id, name, created_at)
        ├── meals (id, user_id, meal_type, recorded_at)
        ├── food_items (id, meal_id, name, weight_g, calories, protein, carbs, fat)
        └── food_density (id, name, density_g_cm3, calories_per_100g, protein, carbs, fat)
```

## Database Schema

```sql
CREATE TABLE food_density (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,           -- e.g. "白米饭", "宫保鸡丁"
    name_en TEXT,                 -- English alias
    density_g_cm3 REAL NOT NULL,  -- food density
    calories_per_100g REAL NOT NULL,
    protein_per_100g REAL,
    carbs_per_100g REAL,
    fat_per_100g REAL,
    category TEXT                 -- staple/meat/vegetable/soup/snack
);

CREATE TABLE meals (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    meal_type TEXT NOT NULL,      -- breakfast/lunch/dinner/snack
    image_paths TEXT,             -- JSON array of file paths
    total_calories REAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE food_items (
    id INTEGER PRIMARY KEY,
    meal_id INTEGER REFERENCES meals(id),
    name TEXT NOT NULL,
    weight_g REAL NOT NULL,
    calories REAL NOT NULL,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL,
    confidence REAL              -- recognition confidence 0-1
);
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/upload | Upload multi-angle images, return image IDs |
| POST | /api/recognize | Run recognition + weight estimation on uploaded images |
| POST | /api/meals | Save a meal record with food items |
| GET | /api/meals?user_id=&date= | List meals for a user on a date |
| DELETE | /api/meals/{id} | Delete a meal record |
| GET | /api/stats?user_id=&range= | Daily/weekly calorie & macro summaries |
| GET | /api/foods/search?q= | Search food density database |

## Recognition + Weight Pipeline

```
Photos (3 angles)  →  [OpenCV: SIFT feature extraction]
    →  Feature matching across image pairs
    →  Triangulation → sparse 3D point cloud
    →  Convex hull / bounding volume estimation → volume (cm³)
    →  ONNX classification → food name + confidence
    →  (if confidence < 0.7) → Vision API fallback
    →  Density DB lookup → density value
    →  Weight = volume × density
    →  Calories = weight × calories_per_g
    →  Return: [{food_name, weight_g, calories, protein, carbs, fat, confidence}]
```

## Frontend Pages

1. **Today Summary** — Progress ring showing daily intake vs target, meal cards (breakfast/lunch/dinner/snack), quick-capture CTA button
2. **Multi-Angle Capture** — Step-by-step guided photo capture (3 angles), viewfinder with guide frame and corner accents, angle badge, shutter button
3. **Analysis Result** — Large calorie number, food item cards (name, estimated weight, macros), macro nutrient bar (protein/carbs/fat), manual adjustment option
4. **History** — Calendar + list view, weekly trend chart

## UI Design System

- **Style:** iOS-inspired dark mode
- **Background:** #000 (pure black)
- **Surface:** rgba(30,30,32,0.6) + backdrop-filter: blur(60px)
- **Text primary:** #F5F5F7, secondary: rgba(245,245,247,0.45)
- **Accent:** #0A84FF (iOS system blue)
- **Typography:** -apple-system, SF Pro Display/Text, tabular-nums for numbers
- **Corner radius:** 16-20px for cards, 36px for viewfinder
- **Spacing:** Generous whitespace, 6-8px between list items

## MVP Scope

- 50 common foods (Chinese + international) in density database
- 100 foods in classification model
- 3-angle photo capture with guided positioning
- Sparse point cloud volume estimation with known-distance constraint
- Simple user selection (name-based, no auth)
- Basic daily/weekly stats

## Out of Scope (Future)

- Full SfM (COLMAP integration)
- User authentication system
- USDA API integration
- Barcode scanning
- Exercise tracking
- Social features
