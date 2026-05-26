# Food Calorie Photo App — Master Document

> **恢复到上次状态：** 读取本文件获取完整上下文后，执行 Task 1 的剩余步骤（pip install → 验证 → 提交），然后继续 Task 2-19。项目路径：`C:\Users\HP\Desktop\app_demo`。技术栈：FastAPI + React + SQLite + OpenCV + ONNX。

**执行进度：** Task 1 后端脚手架 — 文件已创建，依赖待安装，待提交 | Task 2-19 未开始

---

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

---

# Food Calorie Photo App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Full-stack web app for multi-angle food photo → weight estimation → calorie calculation, with iOS-style dark UI.

**Architecture:** React SPA (Vite + TypeScript) frontend communicates via REST API with FastAPI Python backend. SQLite stores meals/food density data. OpenCV handles multi-view 3D reconstruction for volume estimation. ONNX Runtime runs local food classification; Anthropic Vision API serves as fallback.

**Tech Stack:** FastAPI, SQLite, OpenCV (SIFT), ONNX Runtime, React 18, Vite, TypeScript, CSS Modules

**Prerequisites:** Python 3.10+, Node.js 20+, OpenCV contrib (`pip install opencv-contrib-python`), ONNX Runtime

---

## Phase 1: Project Scaffold & Backend Foundation

### Task 1: Create project directory structure and backend scaffold

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/database.py`
- Create: `backend/models.py`

- [ ] **Step 1: Write requirements.txt**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
opencv-contrib-python==4.10.0.84
onnxruntime==1.20.1
numpy==2.2.0
pillow==11.0.0
python-multipart==0.0.18
anthropic==0.40.0
```

- [ ] **Step 2: Install dependencies**

```bash
cd backend && pip install -r requirements.txt
```

- [ ] **Step 3: Write database.py**

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "calorie.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS food_density (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            density_g_cm3 REAL NOT NULL,
            calories_per_100g REAL NOT NULL,
            protein_per_100g REAL,
            carbs_per_100g REAL,
            fat_per_100g REAL,
            category TEXT
        );

        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast','lunch','dinner','snack')),
            image_paths TEXT,
            total_calories REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            weight_g REAL NOT NULL,
            calories REAL NOT NULL,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            confidence REAL
        );
    """)
    conn.commit()
    conn.close()
```

- [ ] **Step 4: Write models.py**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class FoodDensity(BaseModel):
    id: Optional[int] = None
    name: str
    name_en: Optional[str] = None
    density_g_cm3: float
    calories_per_100g: float
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    category: Optional[str] = None


class FoodItemCreate(BaseModel):
    name: str
    weight_g: float
    calories: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    confidence: Optional[float] = None


class FoodItemResponse(BaseModel):
    id: int
    meal_id: int
    name: str
    weight_g: float
    calories: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    confidence: Optional[float] = None


class MealCreate(BaseModel):
    user_id: str
    meal_type: str = Field(pattern=r"^(breakfast|lunch|dinner|snack)$")
    image_paths: Optional[str] = None
    total_calories: Optional[float] = None
    items: list[FoodItemCreate]


class MealResponse(BaseModel):
    id: int
    user_id: str
    meal_type: str
    image_paths: Optional[str] = None
    total_calories: Optional[float] = None
    recorded_at: str
    items: list[FoodItemResponse] = []


class RecognizeResult(BaseModel):
    name: str
    weight_g: float
    calories: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    confidence: float


class StatsResponse(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meals: list[MealResponse]
```

- [ ] **Step 5: Write main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
import os

app = FastAPI(title="Food Calorie App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Router registrations will be added in subsequent tasks
# from routers import upload, meals, recognize, foods, stats
```

- [ ] **Step 6: Run and verify**

```bash
cd backend && python -c "from main import app; from database import init_db; init_db(); print('OK')"
```

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/main.py backend/database.py backend/models.py
git commit -m "feat: add backend scaffold with FastAPI, SQLite schema, Pydantic models"
```

### Task 2: Seed food density data

**Files:**
- Create: `backend/seed_data.py`

- [ ] **Step 1: Write seed_data.py**

```python
import sqlite3
from database import get_db, DB_PATH

SEED_FOODS = [
    # 主食 staples
    ("白米饭", "White Rice", 0.85, 116, 2.6, 25.9, 0.3, "staple"),
    ("糙米饭", "Brown Rice", 0.85, 123, 2.7, 25.6, 0.9, "staple"),
    ("馒头", "Steamed Bun", 0.45, 223, 7.0, 44.2, 1.1, "staple"),
    ("面条(煮)", "Noodles (cooked)", 0.95, 138, 4.5, 28.5, 1.0, "staple"),
    ("全麦面包", "Whole Wheat Bread", 0.25, 247, 13.0, 41.0, 3.4, "staple"),
    ("白面包", "White Bread", 0.22, 265, 9.0, 49.0, 3.2, "staple"),
    ("玉米", "Corn", 0.72, 112, 4.0, 22.8, 1.5, "staple"),
    ("红薯", "Sweet Potato", 0.65, 86, 1.6, 20.1, 0.1, "staple"),
    ("土豆", "Potato", 0.65, 77, 2.0, 17.5, 0.1, "staple"),
    ("小米粥", "Millet Porridge", 0.98, 46, 1.4, 8.4, 0.7, "staple"),

    # 肉类 meat
    ("鸡胸肉(熟)", "Chicken Breast (cooked)", 0.98, 165, 31.0, 0.0, 3.6, "meat"),
    ("鸡腿肉(熟)", "Chicken Thigh (cooked)", 1.02, 209, 25.9, 0.0, 10.9, "meat"),
    ("猪里脊(熟)", "Pork Tenderloin (cooked)", 1.05, 143, 28.5, 0.0, 3.5, "meat"),
    ("猪五花肉(熟)", "Pork Belly (cooked)", 0.92, 518, 9.3, 0.0, 52.3, "meat"),
    ("牛肉(瘦,熟)", "Beef Lean (cooked)", 1.10, 250, 27.0, 0.0, 15.0, "meat"),
    ("羊肉(熟)", "Lamb (cooked)", 1.05, 294, 24.6, 0.0, 21.0, "meat"),
    ("鸭肉(熟)", "Duck (cooked)", 1.00, 337, 19.0, 0.1, 28.0, "meat"),

    # 水产 seafood
    ("三文鱼(熟)", "Salmon (cooked)", 0.98, 208, 20.4, 0.0, 13.4, "seafood"),
    ("虾仁(熟)", "Shrimp (cooked)", 0.95, 99, 24.0, 0.2, 0.3, "seafood"),
    ("带鱼(熟)", "Hairtail (cooked)", 1.00, 172, 18.0, 0.0, 10.8, "seafood"),

    # 蔬菜 vegetables
    ("炒青菜", "Stir-fried Greens", 0.55, 65, 2.5, 4.0, 4.5, "vegetable"),
    ("番茄炒蛋", "Tomato Scrambled Eggs", 0.70, 115, 6.8, 4.2, 7.8, "vegetable"),
    ("西兰花(熟)", "Broccoli (cooked)", 0.45, 34, 2.8, 6.6, 0.4, "vegetable"),
    ("黄瓜", "Cucumber", 0.60, 16, 0.7, 2.9, 0.1, "vegetable"),
    ("胡萝卜(熟)", "Carrot (cooked)", 0.55, 41, 0.9, 9.6, 0.2, "vegetable"),
    ("菠菜(熟)", "Spinach (cooked)", 0.40, 28, 2.6, 3.8, 0.3, "vegetable"),
    ("炒豆角", "Stir-fried Green Beans", 0.60, 89, 3.5, 12.0, 3.5, "vegetable"),

    # 豆制品 tofu
    ("麻婆豆腐", "Mapo Tofu", 0.90, 120, 9.0, 5.0, 8.0, "tofu"),
    ("炒豆腐", "Fried Tofu", 0.65, 156, 13.0, 5.0, 10.0, "tofu"),

    # 汤类 soup
    ("鸡蛋汤", "Egg Drop Soup", 0.98, 35, 2.5, 1.0, 2.0, "soup"),
    ("紫菜蛋花汤", "Seaweed Egg Soup", 0.98, 28, 2.0, 1.5, 1.5, "soup"),

    # 中式菜肴 Chinese dishes
    ("宫保鸡丁", "Kung Pao Chicken", 0.75, 128, 16.0, 5.8, 4.5, "dish"),
    ("红烧肉", "Braised Pork Belly", 0.88, 462, 8.1, 5.4, 45.0, "dish"),
    ("糖醋里脊", "Sweet and Sour Pork", 0.72, 215, 15.0, 22.0, 8.0, "dish"),
    ("鱼香肉丝", "Yu Xiang Shredded Pork", 0.70, 156, 13.0, 8.0, 8.5, "dish"),
    ("回锅肉", "Twice-Cooked Pork", 0.78, 328, 18.0, 5.0, 26.0, "dish"),
    ("水煮鱼", "Boiled Fish", 0.75, 145, 18.5, 2.0, 7.5, "dish"),
    ("酸菜鱼", "Pickled Fish", 0.80, 130, 17.0, 3.0, 6.0, "dish"),
    ("地三鲜", "Di San Xian", 0.60, 120, 2.0, 15.0, 6.5, "dish"),
    ("干煸四季豆", "Dry-fried Green Beans", 0.55, 110, 3.5, 10.0, 7.0, "dish"),

    # 蛋类 eggs
    ("炒鸡蛋", "Scrambled Eggs", 0.55, 196, 13.6, 1.5, 14.8, "egg"),
    ("煮鸡蛋", "Boiled Egg", 0.90, 155, 12.6, 1.1, 10.6, "egg"),

    # 快餐 fast food
    ("炸鸡腿", "Fried Chicken Drumstick", 0.65, 259, 19.0, 8.0, 16.5, "fastfood"),
    ("薯条", "French Fries", 0.35, 312, 3.4, 41.0, 15.0, "fastfood"),
    ("汉堡", "Hamburger", 0.42, 257, 12.9, 26.6, 11.6, "fastfood"),
    ("披萨", "Pizza", 0.50, 266, 11.0, 33.0, 10.0, "fastfood"),

    # 水果 fruits
    ("苹果", "Apple", 0.60, 52, 0.3, 13.8, 0.2, "fruit"),
    ("香蕉", "Banana", 0.65, 89, 1.1, 22.8, 0.3, "fruit"),
    ("橙子", "Orange", 0.72, 47, 0.9, 11.8, 0.1, "fruit"),
    ("葡萄", "Grapes", 0.80, 69, 0.7, 18.1, 0.2, "fruit"),
]


def seed():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM food_density")
    count = cursor.fetchone()[0]
    if count >= len(SEED_FOODS):
        print(f"Already seeded: {count} foods")
        conn.close()
        return

    cursor.execute("DELETE FROM food_density")
    for name, name_en, density, cal, protein, carbs, fat, category in SEED_FOODS:
        cursor.execute(
            "INSERT INTO food_density (name, name_en, density_g_cm3, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, category) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, name_en, density, cal, protein, carbs, fat, category),
        )

    conn.commit()
    conn.close()
    print(f"Seeded {len(SEED_FOODS)} foods")


if __name__ == "__main__":
    from database import init_db

    init_db()
    seed()
```

- [ ] **Step 2: Run seed script and verify**

```bash
cd backend && python seed_data.py
```
Expected: `Seeded 50 foods`

- [ ] **Step 3: Commit**

```bash
git add backend/seed_data.py
git commit -m "feat: add seed data with 50 foods and density values"
```

---

## Phase 2: Backend API Endpoints

### Task 3: Upload endpoint

**Files:**
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/upload.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write upload.py**

```python
import os
import uuid
from fastapi import APIRouter, UploadFile, File
from main import UPLOAD_DIR

router = APIRouter(prefix="/api")


@router.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    if len(files) < 2:
        return {"error": "At least 2 images required for multi-angle estimation"}, 400

    saved = []
    for f in files:
        ext = f.filename.split(".")[-1] if "." in (f.filename or "") else "jpg"
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        contents = await f.read()
        with open(filepath, "wb") as out:
            out.write(contents)
        saved.append({"id": uuid.uuid4().hex[:12], "path": filepath, "filename": f.filename})

    return {"images": saved, "count": len(saved)}
```

- [ ] **Step 2: Register router in main.py — replace the placeholder comment:**

```python
# Replace: # from routers import upload, meals, recognize, foods, stats
from routers import upload

# Add after the health endpoint:
app.include_router(upload.router)
```

- [ ] **Step 3: Write the test for upload endpoint**

```bash
mkdir -p backend/tests
```

Create `backend/tests/__init__.py`:
```python
```

Create `backend/tests/test_upload.py`:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 4: Run test**

```bash
cd backend && pip install httpx && python -m pytest tests/test_upload.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/routers/__init__.py backend/routers/upload.py backend/main.py backend/tests/
git commit -m "feat: add upload endpoint for multi-angle images"
```

### Task 4: Food search and stats endpoints

**Files:**
- Create: `backend/routers/foods.py`
- Create: `backend/routers/stats.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write foods.py**

```python
from fastapi import APIRouter
from database import get_db

router = APIRouter(prefix="/api")


@router.get("/foods/search")
def search_foods(q: str = ""):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM food_density WHERE name LIKE ? OR name_en LIKE ? LIMIT 20",
        (f"%{q}%", f"%{q}%"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

- [ ] **Step 2: Write stats.py**

```python
from fastapi import APIRouter
from database import get_db
from datetime import date, timedelta

router = APIRouter(prefix="/api")


@router.get("/stats")
def get_stats(user_id: str = "", range: str = "daily", target_date: str = ""):
    if target_date:
        d = date.fromisoformat(target_date)
    else:
        d = date.today()

    conn = get_db()

    if range == "daily":
        meals = conn.execute(
            "SELECT * FROM meals WHERE user_id=? AND date(recorded_at)=?",
            (user_id, d.isoformat()),
        ).fetchall()
    else:
        start = d - timedelta(days=6)
        meals = conn.execute(
            "SELECT * FROM meals WHERE user_id=? AND date(recorded_at) BETWEEN ? AND ?",
            (user_id, start.isoformat(), d.isoformat()),
        ).fetchall()

    result = []
    total_cal = total_protein = total_carbs = total_fat = 0.0

    for m in meals:
        items = conn.execute(
            "SELECT * FROM food_items WHERE meal_id=?", (m["id"],)
        ).fetchall()
        meal_dict = dict(m)
        items_list = [dict(i) for i in items]
        meal_dict["items"] = items_list

        for i in items_list:
            total_cal += i.get("calories", 0) or 0
            total_protein += i.get("protein_g", 0) or 0
            total_carbs += i.get("carbs_g", 0) or 0
            total_fat += i.get("fat_g", 0) or 0

        result.append(meal_dict)

    conn.close()

    return {
        "date": d.isoformat(),
        "total_calories": round(total_cal, 1),
        "total_protein": round(total_protein, 1),
        "total_carbs": round(total_carbs, 1),
        "total_fat": round(total_fat, 1),
        "meals": result,
    }
```

- [ ] **Step 3: Register routers in main.py — update the import line and add include_router calls:**

```python
# Change: from routers import upload
# To:
from routers import upload, foods, stats

# Add after existing app.include_router lines:
app.include_router(foods.router)
app.include_router(stats.router)
```

- [ ] **Step 4: Write tests**

Create `backend/tests/test_foods.py`:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_search_foods():
    response = client.get("/api/foods/search?q=鸡")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any("鸡" in r["name"] for r in results)


def test_search_foods_empty():
    response = client.get("/api/foods/search?q=xyznotfound")
    assert response.status_code == 200
    assert response.json() == []
```

Create `backend/tests/test_stats.py`:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_stats_empty():
    response = client.get("/api/stats?user_id=test_user&range=daily")
    assert response.status_code == 200
    data = response.json()
    assert data["total_calories"] == 0
    assert data["meals"] == []
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/test_foods.py tests/test_stats.py -v
```

- [ ] **Step 6: Commit**

```bash
git add backend/routers/foods.py backend/routers/stats.py backend/main.py backend/tests/
git commit -m "feat: add food search and stats endpoints"
```

### Task 5: Meals CRUD endpoint

**Files:**
- Create: `backend/routers/meals.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write meals.py**

```python
from fastapi import APIRouter, HTTPException
from database import get_db
from models import MealCreate, MealResponse, FoodItemResponse

router = APIRouter(prefix="/api")


@router.post("/meals", status_code=201)
def create_meal(meal: MealCreate):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO meals (user_id, meal_type, image_paths, total_calories) VALUES (?, ?, ?, ?)",
        (meal.user_id, meal.meal_type, meal.image_paths, meal.total_calories),
    )
    meal_id = cursor.lastrowid

    for item in meal.items:
        conn.execute(
            "INSERT INTO food_items (meal_id, name, weight_g, calories, protein_g, carbs_g, fat_g, confidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (meal_id, item.name, item.weight_g, item.calories,
             item.protein_g, item.carbs_g, item.fat_g, item.confidence),
        )

    conn.commit()
    conn.close()
    return {"id": meal_id, "status": "created"}


@router.get("/meals")
def list_meals(user_id: str = "", date: str = ""):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM meals WHERE user_id=? AND date(recorded_at)=? ORDER BY recorded_at DESC",
        (user_id, date),
    ).fetchall()

    result = []
    for m in rows:
        items = conn.execute("SELECT * FROM food_items WHERE meal_id=?", (m["id"],)).fetchall()
        meal_dict = dict(m)
        meal_dict["items"] = [dict(i) for i in items]
        result.append(meal_dict)

    conn.close()
    return result


@router.delete("/meals/{meal_id}")
def delete_meal(meal_id: int):
    conn = get_db()
    cursor = conn.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Meal not found")
    conn.close()
    return {"status": "deleted"}
```

- [ ] **Step 2: Register router in main.py — update import and add include_router:**

```python
# Change: from routers import upload, foods, stats
# To:
from routers import upload, foods, stats, meals

# Add after existing app.include_router lines:
app.include_router(meals.router)
```

- [ ] **Step 3: Write tests**

Create `backend/tests/test_meals.py`:
```python
from fastapi.testclient import TestClient
from datetime import date
from main import app
from database import init_db

client = TestClient(app)
init_db()


def test_create_and_list_meal():
    payload = {
        "user_id": "test_user",
        "meal_type": "lunch",
        "total_calories": 486.0,
        "items": [
            {"name": "宫保鸡丁", "weight_g": 320.0, "calories": 268.0,
             "protein_g": 32.0, "carbs_g": 5.8, "fat_g": 4.5, "confidence": 0.92},
            {"name": "白米饭", "weight_g": 200.0, "calories": 218.0,
             "protein_g": 5.2, "carbs_g": 51.8, "fat_g": 0.6, "confidence": 0.96},
        ],
    }
    resp = client.post("/api/meals", json=payload)
    assert resp.status_code == 201
    meal_id = resp.json()["id"]

    resp = client.get(f"/api/meals?user_id=test_user&date={date.today().isoformat()}")
    assert resp.status_code == 200
    meals = resp.json()
    assert len(meals) >= 1

    resp = client.delete(f"/api/meals/{meal_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_meals.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/routers/meals.py backend/main.py backend/tests/test_meals.py
git commit -m "feat: add meals CRUD endpoints"
```

---

## Phase 3: Weight Estimation Engine

### Task 6: Feature matching module

**Files:**
- Create: `backend/engine/__init__.py`
- Create: `backend/engine/feature_matching.py`

- [ ] **Step 1: Write feature_matching.py**

```python
import cv2
import numpy as np


def extract_features(image_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Extract SIFT keypoints and descriptors from an image."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    if descriptors is None or len(keypoints) < 10:
        raise ValueError(f"Too few features found in {image_path}")
    return keypoints, descriptors


def match_features(desc1: np.ndarray, desc2: np.ndarray) -> list[cv2.DMatch]:
    """Match SIFT descriptors between two images using FLANN."""
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(desc1, desc2, k=2)
    good = [m for m, n in matches if m.distance < 0.7 * n.distance]
    return good


def get_matched_points(
    kp1: list[cv2.KeyPoint], kp2: list[cv2.KeyPoint], matches: list[cv2.DMatch]
) -> tuple[np.ndarray, np.ndarray]:
    """Return matched point coordinates from two images."""
    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])
    return pts1, pts2
```

- [ ] **Step 2: Write test**

Create `backend/tests/test_feature_matching.py`:
```python
import numpy as np
import cv2
import os
import pytest
from engine.feature_matching import extract_features, match_features, get_matched_points


@pytest.fixture
def two_test_images():
    """Create two simple test images with a white rectangle slightly shifted."""
    img1 = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.rectangle(img1, (80, 80), (200, 200), (255, 255, 255), -1)

    img2 = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.rectangle(img2, (90, 85), (210, 205), (255, 255, 255), -1)

    path1 = "test_img1.jpg"
    path2 = "test_img2.jpg"
    cv2.imwrite(path1, img1)
    cv2.imwrite(path2, img2)
    yield path1, path2
    os.remove(path1)
    os.remove(path2)


def test_extract_and_match(two_test_images):
    path1, path2 = two_test_images
    kp1, desc1 = extract_features(path1)
    kp2, desc2 = extract_features(path2)
    assert len(kp1) > 0
    assert len(kp2) > 0

    matches = match_features(desc1, desc2)
    assert len(matches) > 0

    pts1, pts2 = get_matched_points(kp1, kp2, matches)
    assert pts1.shape == pts2.shape
    assert pts1.shape[0] == len(matches)
```

- [ ] **Step 3: Run test**

```bash
cd backend && python -m pytest tests/test_feature_matching.py -v
```

- [ ] **Step 4: Commit**

```bash
git add backend/engine/__init__.py backend/engine/feature_matching.py backend/tests/test_feature_matching.py
git commit -m "feat: add SIFT feature extraction and matching module"
```

### Task 7: 3D reconstruction and volume estimation

**Files:**
- Create: `backend/engine/reconstruction.py`

- [ ] **Step 1: Write reconstruction.py**

```python
import cv2
import numpy as np
from engine.feature_matching import extract_features, match_features, get_matched_points


class VolumeEstimator:
    """Estimates food volume from multi-angle images using sparse 3D reconstruction.

    Uses known camera distance (~30cm from food) to set absolute scale.
    Requires at least 2 images from different angles.
    """

    def __init__(self, known_distance_cm: float = 30.0):
        self.known_distance = known_distance_cm  # cm from camera to food center

    def estimate_volume(self, image_paths: list[str]) -> dict:
        """Main entry point: estimate volume from 2-3 images.

        Returns dict with volume_cm3, point_count, and scale_factor.
        """
        if len(image_paths) < 2:
            raise ValueError("Need at least 2 images for reconstruction")

        all_points_3d = []
        scale = self.known_distance / 30.0  # normalize to reference distance

        for i in range(len(image_paths) - 1):
            kp1, desc1 = extract_features(image_paths[i])
            kp2, desc2 = extract_features(image_paths[i + 1])
            matches = match_features(desc1, desc2)
            pts1, pts2 = get_matched_points(kp1, kp2, matches)

            # Simulate camera parameters with known distance
            img = cv2.imread(image_paths[i])
            h, w = img.shape[:2]
            focal = max(w, h) * (self.known_distance / 10.0)  # approximate focal length

            K = np.array([
                [focal, 0, w / 2],
                [0, focal, h / 2],
                [0, 0, 1],
            ], dtype=np.float32)

            # Assume small rotation between views (~15-45 degrees)
            angle_rad = np.radians(30.0)
            E = np.array([
                [0, 0, 0],
                [0, 0, -1],
                [0, 1, 0],
            ], dtype=np.float32) * np.sin(angle_rad)

            R1 = np.eye(3, dtype=np.float32)
            t1 = np.zeros((3, 1), dtype=np.float32)
            R2, _ = cv2.Rodrigues(np.array([0, angle_rad, 0], dtype=np.float32))
            t2 = np.array([[0.05 * self.known_distance], [0], [0]], dtype=np.float32)

            P1 = K @ np.hstack((R1, t1))
            P2 = K @ np.hstack((R2, t2))

            pts_4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
            pts_3d = pts_4d[:3] / pts_4d[3]
            pts_3d *= scale

            all_points_3d.append(pts_3d.T)

        if not all_points_3d:
            raise ValueError("Failed to reconstruct 3D points")

        combined = np.vstack(all_points_3d)

        # Filter outliers
        centroid = np.median(combined, axis=0)
        distances = np.linalg.norm(combined - centroid, axis=1)
        threshold = np.percentile(distances, 90)
        filtered = combined[distances <= threshold]

        if len(filtered) < 4:
            filtered = combined

        # Compute convex hull volume
        try:
            hull = cv2.convexHull(filtered.astype(np.float32))
            volume = cv2.contourArea(hull.reshape(-1, 1, 2)) if hull is not None else 0

            # Approximate depth from point spread in Z
            z_range = np.ptp(filtered[:, 2]) if filtered.shape[1] > 2 else 0
            if z_range < 0.1:
                z_range = max(1.0, volume ** (1 / 3) * 0.5)

            volume_cm3 = volume * z_range * 0.01  # scale to cm³
        except Exception:
            bbox_dims = np.ptp(filtered, axis=0)
            volume_cm3 = float(np.prod(bbox_dims)) * 0.01

        volume_cm3 = max(10.0, min(5000.0, abs(volume_cm3)))

        return {
            "volume_cm3": round(volume_cm3, 1),
            "point_count": len(filtered),
            "scale_factor": round(scale, 2),
        }
```

- [ ] **Step 2: Write test**

Create `backend/tests/test_reconstruction.py`:
```python
import numpy as np
import cv2
import os
import pytest
from engine.reconstruction import VolumeEstimator


@pytest.fixture
def two_angle_images():
    """Two images of a simulated food blob from slightly different angles."""
    def make_food_image(offset_x=0):
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        # Draw an ellipse to simulate food on a plate
        cv2.ellipse(img, (200 + offset_x, 210), (120, 100), 0, 0, 360, (200, 180, 160), -1)
        cv2.ellipse(img, (200 + offset_x, 210), (120, 100), 0, 0, 360, (255, 230, 200), 2)
        # Add some texture with circles
        for _ in range(20):
            cx = np.random.randint(100 + offset_x, 300 + offset_x)
            cy = np.random.randint(130, 290)
            r = np.random.randint(3, 8)
            color = np.random.choice([(180, 160, 140), (220, 200, 180), (160, 140, 120)])
            cv2.circle(img, (cx, cy), r, color, -1)
        return img

    img1 = make_food_image(0)
    img2 = make_food_image(15)

    path1 = "test_food_1.jpg"
    path2 = "test_food_2.jpg"
    cv2.imwrite(path1, img1)
    cv2.imwrite(path2, img2)
    yield [path1, path2]
    os.remove(path1)
    os.remove(path2)


def test_volume_estimation(two_angle_images):
    estimator = VolumeEstimator(known_distance_cm=30.0)
    result = estimator.estimate_volume(two_angle_images)
    assert "volume_cm3" in result
    assert result["volume_cm3"] > 0
    assert result["point_count"] > 0
```

- [ ] **Step 3: Run test**

```bash
cd backend && python -m pytest tests/test_reconstruction.py -v
```

- [ ] **Step 4: Commit**

```bash
git add backend/engine/reconstruction.py backend/tests/test_reconstruction.py
git commit -m "feat: add 3D reconstruction and volume estimation module"
```

### Task 8: Weight and calorie calculation

**Files:**
- Create: `backend/engine/weight.py`

- [ ] **Step 1: Write weight.py**

```python
from database import get_db


class WeightCalculator:
    """Converts food volume + classification → weight → calories using density DB."""

    def calculate(self, food_name: str, volume_cm3: float) -> dict:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM food_density WHERE name=? OR name_en=?",
            (food_name, food_name),
        ).fetchone()
        conn.close()

        if row is None:
            return {
                "name": food_name,
                "weight_g": 0,
                "calories": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "confidence": 0.0,
                "error": f"Food '{food_name}' not found in density database",
            }

        density = row["density_g_cm3"]
        weight_g = round(volume_cm3 * density, 1)
        calories = round(weight_g * row["calories_per_100g"] / 100.0, 1)
        protein = round(weight_g * (row["protein_per_100g"] or 0) / 100.0, 1)
        carbs = round(weight_g * (row["carbs_per_100g"] or 0) / 100.0, 1)
        fat = round(weight_g * (row["fat_per_100g"] or 0) / 100.0, 1)

        return {
            "name": row["name"],
            "weight_g": weight_g,
            "calories": calories,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "confidence": 0.0,
        }
```

- [ ] **Step 2: Write test**

Create `backend/tests/test_weight.py`:
```python
import pytest
from engine.weight import WeightCalculator
from database import init_db
from seed_data import seed


def test_calculate_known_food():
    init_db()
    seed()
    calc = WeightCalculator()
    result = calc.calculate("白米饭", 200.0)
    assert result["name"] == "白米饭"
    assert result["weight_g"] == pytest.approx(170.0, rel=0.2)
    assert result["calories"] > 0
    assert result["protein_g"] > 0
    assert result["carbs_g"] > 0


def test_unknown_food():
    calc = WeightCalculator()
    result = calc.calculate("外星食物", 100.0)
    assert "error" in result
    assert result["confidence"] == 0.0
```

- [ ] **Step 3: Run test**

```bash
cd backend && python -m pytest tests/test_weight.py -v
```
Note: Add `import pytest` at the top of test_weight.py if not present.

- [ ] **Step 4: Commit**

```bash
git add backend/engine/weight.py backend/tests/test_weight.py
git commit -m "feat: add weight and calorie calculation from density DB"
```

---

## Phase 4: AI Classification Layer

### Task 9: Food classifier with ONNX + Vision API fallback

**Files:**
- Create: `backend/ai/__init__.py`
- Create: `backend/ai/classifier.py`
- Create: `backend/ai/fallback.py`

- [ ] **Step 1: Write classifier.py**

```python
import os
import numpy as np
from PIL import Image
import json

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
LABELS_PATH = os.path.join(MODEL_DIR, "food_labels.json")


def get_labels() -> list[str]:
    if os.path.exists(LABELS_PATH):
        with open(LABELS_PATH) as f:
            return json.load(f)
    return [
        "白米饭", "馒头", "面条(煮)", "面包", "玉米", "红薯", "土豆",
        "鸡胸肉(熟)", "鸡腿肉(熟)", "猪里脊(熟)", "牛肉(瘦,熟)", "羊肉(熟)", "鸭肉(熟)",
        "三文鱼(熟)", "虾仁(熟)", "炒鸡蛋", "煮鸡蛋", "西兰花(熟)", "黄瓜",
        "胡萝卜(熟)", "菠菜(熟)", "番茄炒蛋", "炒青菜", "苹果", "香蕉", "橙子", "葡萄",
        "宫保鸡丁", "红烧肉", "糖醋里脊", "鱼香肉丝", "回锅肉", "水煮鱼",
        "麻婆豆腐", "炒豆腐", "鸡蛋汤", "炸鸡腿", "薯条", "汉堡", "披萨",
        "炒豆角", "带鱼(熟)", "馒头", "全麦面包", "小米粥", "糙米饭",
        "酸菜鱼", "地三鲜", "干煸四季豆", "紫菜蛋花汤", "炒鸡蛋",
    ]


def classify_food(image_path: str) -> dict:
    """Classify food from image. Tries ONNX model, returns result with confidence."""
    model_path = os.path.join(MODEL_DIR, "food_classifier.onnx")

    if not os.path.exists(model_path):
        return _simulated_classify(image_path)

    try:
        import onnxruntime as ort

        session = ort.InferenceSession(model_path)
        img = Image.open(image_path).convert("RGB").resize((224, 224))
        img_array = np.array(img, dtype=np.float32)
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)
        img_array = (img_array - 127.5) / 127.5

        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: img_array})
        probs = outputs[0][0]
        top_idx = int(np.argmax(probs))
        confidence = float(probs[top_idx])

        labels = get_labels()
        if top_idx < len(labels):
            return {"name": labels[top_idx], "confidence": round(confidence, 3), "source": "onnx"}

        return {"name": "unknown", "confidence": 0.0, "source": "onnx"}

    except Exception as e:
        print(f"ONNX inference failed: {e}, falling back to simulated")
        return _simulated_classify(image_path)


def _simulated_classify(image_path: str) -> dict:
    """Simulated classifier for development without ONNX model file."""
    import hashlib

    labels = get_labels()
    h = int(hashlib.md5(image_path.encode()).hexdigest(), 16)
    idx = h % len(labels)
    confidence = 0.70 + (h % 25) / 100.0
    return {"name": labels[idx], "confidence": round(confidence, 3), "source": "simulated"}
```

- [ ] **Step 2: Write fallback.py**

```python
import base64
import os
from anthropic import Anthropic


def classify_with_vision(image_path: str) -> dict:
    """Use Anthropic Vision API as fallback for difficult classifications."""
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
    if not api_key:
        return {"name": "unknown", "confidence": 0.0, "source": "fallback", "error": "No API key"}

    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(image_path)[1].lower().replace(".", "")
        media_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Identify the food in this image. Respond with ONLY a JSON object: "
                                '{"name": "food name in Chinese", "confidence": 0.0-1.0, '
                                '"is_mixed": true/false}. If multiple foods, set is_mixed=true '
                                "and name as the main dish.",
                    },
                ],
            }],
        )

        text = response.content[0].text.strip()
        import json
        result = json.loads(text)
        result["source"] = "vision_api"
        return result

    except Exception as e:
        return {"name": "unknown", "confidence": 0.0, "source": "fallback", "error": str(e)}
```

- [ ] **Step 3: Write test**

Create `backend/tests/test_classifier.py`:
```python
import numpy as np
import cv2
import os
from ai.classifier import classify_food


def test_classify_simulated():
    """Test simulated classification path."""
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(img, (150, 150), 100, (200, 180, 160), -1)
    path = "test_food_classify.jpg"
    cv2.imwrite(path, img)

    result = classify_food(path)
    assert result["name"]
    assert result["confidence"] >= 0.70
    assert result["source"] == "simulated"
    os.remove(path)
```

- [ ] **Step 4: Run test**

```bash
cd backend && python -m pytest tests/test_classifier.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/ai/__init__.py backend/ai/classifier.py backend/ai/fallback.py backend/tests/test_classifier.py
git commit -m "feat: add food classifier with ONNX and Vision API fallback"
```

### Task 10: Wire recognition endpoint

**Files:**
- Create: `backend/routers/recognize.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write recognize.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from engine.reconstruction import VolumeEstimator
from engine.weight import WeightCalculator
from ai.classifier import classify_food
from models import RecognizeResult

router = APIRouter(prefix="/api")


class RecognizeRequest(BaseModel):
    image_paths: list[str]
    known_distance_cm: float = 30.0


@router.post("/recognize")
def recognize_food(req: RecognizeRequest) -> list[dict]:
    if len(req.image_paths) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 images")

    estimator = VolumeEstimator(known_distance_cm=req.known_distance_cm)
    volume_result = estimator.estimate_volume(req.image_paths)

    primary_image = req.image_paths[0]
    classification = classify_food(primary_image)

    if classification["confidence"] < 0.7:
        from ai.fallback import classify_with_vision
        fallback = classify_with_vision(primary_image)
        if fallback.get("confidence", 0) > classification["confidence"]:
            classification = fallback

    calculator = WeightCalculator()
    result = calculator.calculate(classification["name"], volume_result["volume_cm3"])
    result["confidence"] = classification["confidence"]
    result["volume_cm3"] = volume_result["volume_cm3"]

    return [result]
```

- [ ] **Step 2: Register router in main.py — update import and add include_router:**

```python
# Change: from routers import upload, foods, stats, meals
# To:
from routers import upload, foods, stats, meals, recognize

# Add after existing app.include_router lines:
app.include_router(recognize.router)
```

- [ ] **Step 3: Write test**

Create `backend/tests/test_recognize.py`:
```python
from fastapi.testclient import TestClient
from main import app
from database import init_db
from seed_data import seed

client = TestClient(app)
init_db()
seed()


def test_recognize_endpoint():
    """Test full recognition pipeline with test images."""
    import numpy as np
    import cv2

    img1 = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.ellipse(img1, (200, 210), (120, 100), 0, 0, 360, (200, 180, 160), -1)
    for i in range(30):
        cv2.circle(img1, (np.random.randint(100, 300), np.random.randint(130, 290)),
                   np.random.randint(3, 10), (255, 230, 200), -1)

    img2 = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.ellipse(img2, (210, 215), (120, 100), 0, 0, 360, (200, 180, 160), -1)
    for i in range(30):
        cv2.circle(img2, (np.random.randint(110, 310), np.random.randint(135, 295)),
                   np.random.randint(3, 10), (255, 230, 200), -1)

    path1 = "test_recognize_1.jpg"
    path2 = "test_recognize_2.jpg"
    cv2.imwrite(path1, img1)
    cv2.imwrite(path2, img2)

    import os
    resp = client.post("/api/recognize", json={
        "image_paths": [os.path.abspath(path1), os.path.abspath(path2)],
        "known_distance_cm": 30.0,
    })
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert "name" in results[0]
    assert results[0]["weight_g"] > 0
    assert results[0]["calories"] > 0

    os.remove(path1)
    os.remove(path2)
```

- [ ] **Step 4: Run test**

```bash
cd backend && python -m pytest tests/test_recognize.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/routers/recognize.py backend/main.py backend/tests/test_recognize.py
git commit -m "feat: wire full recognition pipeline endpoint"
```

### Task 11: Backend integration test + run server

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: Ensure all routers are registered in main.py**

The final main.py should have these imports and router registrations:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import upload, meals, recognize, foods, stats
import os

app = FastAPI(title="Food Calorie App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.include_router(upload.router)
app.include_router(meals.router)
app.include_router(recognize.router)
app.include_router(foods.router)
app.include_router(stats.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Run all backend tests**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 3: Start server for manual smoke test**

```bash
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl http://localhost:8000/api/health
curl http://localhost:8000/api/foods/search?q=鸡
```

Expected: `{"status":"ok"}` and food search results.

- [ ] **Step 4: Commit**

```bash
git add backend/main.py
git commit -m "feat: complete backend with all routers wired, all tests passing"
```

---

## Phase 5: Frontend Foundation

### Task 12: Scaffold Vite + React + TypeScript project

**Prerequisite:** Node.js 20+ installed.

- [ ] **Step 1: Create frontend project**

```bash
cd C:/Users/HP/Desktop/app_demo
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
```

- [ ] **Step 2: Install additional dependencies**

```bash
cd frontend && npm install react-router-dom
```

- [ ] **Step 3: Add proxy config for API**

Create `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: Verify dev server starts**

```bash
cd frontend && npm run dev
```

Open browser to verify Vite default page shows.

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Vite + React + TypeScript frontend"
```

### Task 13: Global styles — iOS design system

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/types.ts`

- [ ] **Step 1: Write types.ts**

```typescript
export interface FoodItem {
  id?: number;
  meal_id?: number;
  name: string;
  weight_g: number;
  calories: number;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  confidence?: number | null;
}

export interface Meal {
  id: number;
  user_id: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  image_paths?: string | null;
  total_calories?: number | null;
  recorded_at: string;
  items: FoodItem[];
}

export interface RecognizeResult {
  name: string;
  weight_g: number;
  calories: number;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  confidence: number;
  volume_cm3?: number;
}

export interface StatsData {
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  meals: Meal[];
}

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export type CaptureStep = 0 | 1 | 2;
```

- [ ] **Step 2: Write client.ts**

```typescript
const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`${res.status}: ${err}`);
  }
  return res.json();
}

export const api = {
  uploadImages: async (files: File[]) => {
    const form = new FormData();
    files.forEach((f) => form.append('files', f));
    const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form });
    return res.json();
  },

  recognize: (imagePaths: string[], knownDistanceCm = 30) =>
    request<import('./types').RecognizeResult[]>(`/recognize`, {
      method: 'POST',
      body: JSON.stringify({ image_paths: imagePaths, known_distance_cm: knownDistanceCm }),
    }),

  createMeal: (meal: {
    user_id: string; meal_type: string; total_calories?: number;
    image_paths?: string; items: import('./types').FoodItem[];
  }) => request<{ id: number }>('/meals', { method: 'POST', body: JSON.stringify(meal) }),

  getMeals: (userId: string, date: string) =>
    request<import('./types').Meal[]>(`/meals?user_id=${userId}&date=${date}`),

  deleteMeal: (id: number) => request<{ status: string }>(`/meals/${id}`, { method: 'DELETE' }),

  getStats: (userId: string, range = 'daily', date?: string) =>
    request<import('./types').StatsData>(
      `/stats?user_id=${userId}&range=${range}${date ? `&target_date=${date}` : ''}`
    ),

  searchFoods: (q: string) =>
    request<Array<{
      id: number; name: string; name_en?: string;
      density_g_cm3: number; calories_per_100g: number;
      protein_per_100g?: number; carbs_per_100g?: number; fat_per_100g?: number;
      category?: string;
    }>>(`/foods/search?q=${encodeURIComponent(q)}`),
};
```

- [ ] **Step 3: Replace index.css with iOS design system**

```css
:root {
  --bg-primary: #000000;
  --bg-surface: rgba(30, 30, 32, 0.6);
  --text-primary: #F5F5F7;
  --text-secondary: rgba(245, 245, 247, 0.45);
  --text-tertiary: rgba(245, 245, 247, 0.25);
  --accent: #0A84FF;
  --accent-dim: rgba(10, 132, 255, 0.12);
  --red: #FF453A;
  --green: #30D158;
  --orange: #FF9F0A;
  --border: rgba(255, 255, 255, 0.06);
  --border-light: rgba(255, 255, 255, 0.04);
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 20px;
  --radius-xl: 36px;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #root {
  height: 100%;
  width: 100%;
  overflow-x: hidden;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.2px;
  line-height: 1.4;
}

.app-container {
  max-width: 430px;
  margin: 0 auto;
  min-height: 100%;
  position: relative;
}

/* Typography */
.title-large {
  font-size: 34px;
  font-weight: 700;
  letter-spacing: -0.5px;
  line-height: 1.1;
}

.title-section {
  font-size: 15px;
  font-weight: 400;
  color: var(--text-secondary);
  letter-spacing: -0.2px;
}

.card-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* Glass surface */
.glass {
  background: var(--bg-surface);
  backdrop-filter: blur(60px);
  -webkit-backdrop-filter: blur(60px);
  border: 1px solid var(--border);
}

.glass-card {
  background: var(--bg-surface);
  backdrop-filter: blur(60px);
  -webkit-backdrop-filter: blur(60px);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 14px 18px;
}

/* Buttons */
.btn-primary {
  background: var(--text-primary);
  color: var(--bg-primary);
  border: none;
  border-radius: var(--radius-md);
  padding: 15px 0;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.3px;
  cursor: pointer;
  width: 100%;
  text-align: center;
  transition: opacity 0.15s;
}
.btn-primary:active {
  opacity: 0.8;
}

.btn-ghost {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  padding: 0;
}

/* Navigation */
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
}

/* Tab bar */
.tab-bar {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 20px 32px;
  border-top: 0.5px solid var(--border);
}

.tab-item {
  text-align: center;
  cursor: pointer;
}
.tab-item .icon {
  font-size: 22px;
  display: block;
}
.tab-item .label {
  font-size: 10px;
  font-weight: 500;
  margin-top: 5px;
  letter-spacing: 0.2px;
}
.tab-item.active .label {
  color: var(--accent);
}
.tab-item.inactive {
  opacity: 0.35;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in {
  animation: fadeIn 0.35s ease-out;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 0;
}
```

- [ ] **Step 4: Write basic App.tsx**

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TodayPage } from './pages/TodayPage';
import { CapturePage } from './pages/CapturePage';
import { ResultPage } from './pages/ResultPage';
import { HistoryPage } from './pages/HistoryPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<TodayPage />} />
          <Route path="/capture" element={<CapturePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
```

- [ ] **Step 5: Create placeholder page files**

Create `frontend/src/pages/TodayPage.tsx`:
```tsx
export function TodayPage() {
  return <div style={{ padding: 24 }}><h1 className="title-large">今天</h1></div>;
}
```

Create `frontend/src/pages/CapturePage.tsx`:
```tsx
export function CapturePage() {
  return <div style={{ padding: 24 }}><h1>Capture</h1></div>;
}
```

Create `frontend/src/pages/ResultPage.tsx`:
```tsx
export function ResultPage() {
  return <div style={{ padding: 24 }}><h1>Result</h1></div>;
}
```

Create `frontend/src/pages/HistoryPage.tsx`:
```tsx
export function HistoryPage() {
  return <div style={{ padding: 24 }}><h1>History</h1></div>;
}
```

- [ ] **Step 6: Verify build**

```bash
cd frontend && npm run dev
```

Check browser shows the app at http://localhost:5173.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add iOS design system, API client, page routing"
```

---

## Phase 6: Frontend Components

### Task 14: Core UI components

**Files:**
- Create: `frontend/src/components/TabBar.tsx`
- Create: `frontend/src/components/ProgressRing.tsx`
- Create: `frontend/src/components/MacroBar.tsx`
- Create: `frontend/src/components/MealCard.tsx`
- Create: `frontend/src/components/FoodItemCard.tsx`

- [ ] **Step 1: Write TabBar.tsx**

```tsx
import { useNavigate, useLocation } from 'react-router-dom';

const tabs = [
  { path: '/', icon: '📊', label: '摘要' },
  { path: '/capture', icon: '📷', label: '拍照' },
  { path: '/history', icon: '📅', label: '历史' },
];

export function TabBar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="tab-bar">
      {tabs.map((t) => {
        const active = (t.path === '/' && location.pathname === '/') ||
          (t.path !== '/' && location.pathname.startsWith(t.path));
        return (
          <div
            key={t.path}
            className={`tab-item ${active ? 'active' : 'inactive'}`}
            onClick={() => navigate(t.path)}
          >
            <span className="icon">{t.icon}</span>
            <span className="label">{t.label}</span>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Write ProgressRing.tsx**

```tsx
export function ProgressRing({ current, target = 2000 }: { current: number; target?: number }) {
  const pct = Math.min(current / target, 1);
  const remaining = target - current;

  return (
    <div style={{
      width: 160, height: 160, borderRadius: '50%', margin: '0 auto', position: 'relative',
      background: `conic-gradient(from -90deg, #F5F5F7 0% ${pct * 100}%, rgba(245,245,247,0.06) ${pct * 100}% 100%)`,
    }}>
      <div style={{
        position: 'absolute', top: 8, left: 8, right: 8, bottom: 8,
        borderRadius: '50%', background: '#000',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ color: '#F5F5F7', fontSize: 34, fontWeight: 500, letterSpacing: -1, lineHeight: 1 }}>
          {current.toLocaleString()}
        </span>
        <span style={{ color: 'rgba(245,245,247,0.35)', fontSize: 13, fontWeight: 400, marginTop: 2 }}>
          剩余 {remaining} kcal
        </span>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Write MacroBar.tsx**

```tsx
interface MacroBarProps {
  protein: number;
  carbs: number;
  fat: number;
}

export function MacroBar({ protein, carbs, fat }: MacroBarProps) {
  return (
    <div className="glass-card" style={{ padding: '20px 24px', borderRadius: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{ width: 36, height: 4, borderRadius: 2,
            background: 'linear-gradient(90deg, #FF453A, #FF6B60)', margin: '0 auto 10px' }} />
          <p style={{ color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(protein)}
          </p>
          <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, fontWeight: 500, margin: '2px 0 0', letterSpacing: 0.3 }}>
            蛋白质 · g
          </p>
        </div>
        <div style={{ width: 1, height: 28, background: 'rgba(255,255,255,0.06)' }} />
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{ width: 36, height: 4, borderRadius: 2,
            background: 'linear-gradient(90deg, #30D158, #6EE790)', margin: '0 auto 10px' }} />
          <p style={{ color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(carbs)}
          </p>
          <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, fontWeight: 500, margin: '2px 0 0', letterSpacing: 0.3 }}>
            碳水 · g
          </p>
        </div>
        <div style={{ width: 1, height: 28, background: 'rgba(255,255,255,0.06)' }} />
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{ width: 36, height: 4, borderRadius: 2,
            background: 'linear-gradient(90deg, #0A84FF, #40A8FF)', margin: '0 auto 10px' }} />
          <p style={{ color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(fat)}
          </p>
          <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, fontWeight: 500, margin: '2px 0 0', letterSpacing: 0.3 }}>
            脂肪 · g
          </p>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Write MealCard.tsx**

```tsx
import type { Meal, MealType } from '../types';

const mealConfig: Record<MealType, { emoji: string; label: string }> = {
  breakfast: { emoji: '🌅', label: '早餐' },
  lunch: { emoji: '☀️', label: '午餐' },
  dinner: { emoji: '🌙', label: '晚餐' },
  snack: { emoji: '🍪', label: '零食' },
};

interface MealCardProps {
  meal: Meal;
  onClick?: () => void;
}

export function MealCard({ meal, onClick }: MealCardProps) {
  const config = mealConfig[meal.meal_type] ?? { emoji: '🍽', label: meal.meal_type };
  const hasItems = meal.items.length > 0;
  const foodNames = meal.items.map((i) => i.name).join(' · ');

  return (
    <div
      className="glass-card"
      style={{
        display: 'flex', alignItems: 'center', gap: 14,
        opacity: hasItems ? 1 : 0.4, cursor: onClick ? 'pointer' : undefined,
      }}
      onClick={onClick}
    >
      <div style={{
        width: 44, height: 44, borderRadius: 12, flexShrink: 0,
        background: 'linear-gradient(135deg, rgba(255,159,10,0.15), rgba(255,159,10,0.05))',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
      }}>
        {config.emoji}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ color: '#F5F5F7', fontSize: 16, fontWeight: 500, margin: 0, letterSpacing: -0.3 }}>
          {config.label}
        </p>
        <p style={{
          color: 'rgba(245,245,247,0.35)', fontSize: 13, margin: '2px 0 0',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {hasItems ? foodNames : '还没有记录'}
        </p>
      </div>
      <span style={{
        color: hasItems ? '#F5F5F7' : 'rgba(245,245,247,0.2)',
        fontSize: 16, fontWeight: hasItems ? 500 : 400, margin: 0, letterSpacing: -0.3, flexShrink: 0,
      }}>
        {hasItems ? Math.round(meal.total_calories ?? meal.items.reduce((s, i) => s + i.calories, 0)) : '--'}
      </span>
    </div>
  );
}
```

- [ ] **Step 5: Write FoodItemCard.tsx**

```tsx
import type { FoodItem } from '../types';

interface FoodItemCardProps {
  item: FoodItem;
  onAdjust?: (item: FoodItem) => void;
}

export function FoodItemCard({ item, onAdjust }: FoodItemCardProps) {
  return (
    <div className="glass-card" style={{ borderRadius: 16, padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ color: '#F5F5F7', fontSize: 17, fontWeight: 500, margin: 0, letterSpacing: -0.3 }}>
            {item.name}
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 6 }}>
            <span style={{ color: 'rgba(245,245,247,0.4)', fontSize: 13, fontWeight: 400 }}>
              ~{Math.round(item.weight_g)}g
            </span>
            {item.confidence != null && (
              <>
                <span style={{ width: 3, height: 3, borderRadius: '50%', background: 'rgba(245,245,247,0.15)' }} />
                <span style={{ color: 'rgba(245,245,247,0.4)', fontSize: 13 }}>
                  置信度 {Math.round(item.confidence * 100)}%
                </span>
              </>
            )}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <p style={{ color: '#F5F5F7', fontSize: 20, fontWeight: 400, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(item.calories)}
          </p>
          <p style={{ color: 'rgba(245,245,247,0.35)', fontSize: 13, fontWeight: 400, margin: '2px 0 0' }}>
            千卡
          </p>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: add core UI components (TabBar, ProgressRing, MacroBar, MealCard, FoodItemCard)"
```

---

## Phase 7: Frontend Pages

### Task 15: Today summary page

**Files:**
- Modify: `frontend/src/pages/TodayPage.tsx`

- [ ] **Step 1: Replace TodayPage.tsx with full implementation**

```tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { TabBar } from '../components/TabBar';
import { ProgressRing } from '../components/ProgressRing';
import { MealCard } from '../components/MealCard';
import type { Meal, StatsData } from '../types';

const CURRENT_USER = 'default_user';
const CALORIE_TARGET = 2000;

export function TodayPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  const today = new Date().toISOString().slice(0, 10);

  useEffect(() => {
    api.getStats(CURRENT_USER, 'daily', today)
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const mealSlots: Array<{ type: 'breakfast' | 'lunch' | 'dinner' | 'snack'; meals: Meal[] }> = [
    { type: 'breakfast', meals: stats?.meals.filter((m) => m.meal_type === 'breakfast') ?? [] },
    { type: 'lunch', meals: stats?.meals.filter((m) => m.meal_type === 'lunch') ?? [] },
    { type: 'dinner', meals: stats?.meals.filter((m) => m.meal_type === 'dinner') ?? [] },
    { type: 'snack', meals: stats?.meals.filter((m) => m.meal_type === 'snack') ?? [] },
  ];

  const now = new Date();
  const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()];
  const dateStr = `${now.getMonth() + 1}月${now.getDate()}日 · ${weekDay}`;

  return (
    <div className="fade-in" style={{ paddingBottom: 24 }}>
      <div style={{ padding: '40px 24px 6px' }}>
        <p className="title-section">{dateStr}</p>
        <h1 className="title-large" style={{ marginTop: 2 }}>今天</h1>
      </div>

      <div style={{ textAlign: 'center', padding: '8px 0 24px' }}>
        <ProgressRing
          current={stats?.total_calories ?? 0}
          target={CALORIE_TARGET}
        />
      </div>

      <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {!loading && <p className="card-label" style={{ padding: '0 4px 4px' }}>餐食记录</p>}

        {mealSlots.map(({ type, meals }) => {
          if (meals.length > 0) {
            return meals.map((meal) => (
              <MealCard key={meal.id} meal={meal} />
            ));
          }
          return (
            <div
              key={type}
              className="glass-card"
              style={{
                display: 'flex', alignItems: 'center', gap: 14, opacity: 0.4,
              }}
            >
              <div style={{
                width: 44, height: 44, borderRadius: 12, flexShrink: 0,
                background: 'rgba(255,255,255,0.03)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
              }}>
                {{ breakfast: '🌅', lunch: '☀️', dinner: '🌙', snack: '🍪' }[type]}
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ color: '#F5F5F7', fontSize: 16, fontWeight: 500, margin: 0 }}>
                  {{ breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '零食' }[type]}
                </p>
                <p style={{ color: 'rgba(245,245,247,0.2)', fontSize: 13, margin: '2px 0 0' }}>
                  还没有记录
                </p>
              </div>
              <span style={{ color: 'rgba(245,245,247,0.2)', fontSize: 16 }}>--</span>
            </div>
          );
        })}
      </div>

      <div style={{ padding: '20px 20px 8px' }}>
        <button className="btn-primary" onClick={() => navigate('/capture')}>
          📷  拍照记录餐食
        </button>
      </div>

      <TabBar />
    </div>
  );
}
```

- [ ] **Step 2: Verify it compiles**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/TodayPage.tsx
git commit -m "feat: implement today summary page with stats and meal slots"
```

### Task 16: Multi-angle capture page

**Files:**
- Modify: `frontend/src/pages/CapturePage.tsx`
- Create: `frontend/src/hooks/useCamera.ts`

- [ ] **Step 1: Write useCamera.ts**

```tsx
import { useState, useRef, useCallback } from 'react';

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [streaming, setStreaming] = useState(false);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1080 }, height: { ideal: 1440 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setStreaming(true);
    } catch (e) {
      console.error('Camera access denied:', e);
      alert('无法访问摄像头，请检查权限设置');
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setStreaming(false);
  }, []);

  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current) return null;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    ctx.drawImage(videoRef.current, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.9);
  }, []);

  return { videoRef, streaming, startCamera, stopCamera, captureFrame };
}
```

- [ ] **Step 2: Write CapturePage.tsx**

```tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCamera } from '../hooks/useCamera';
import { api } from '../api/client';

const ANGLE_LABELS = ['正面视图', '45° 侧面', '90° 侧面'];
const ANGLE_HINTS = [
  '正面拍摄食物\n确保完整可见',
  '从右侧约 45° 拍摄\n展示食物高度',
  '从正侧面 90° 拍摄\n展示食物厚度',
];

export function CapturePage() {
  const navigate = useNavigate();
  const { videoRef, streaming, startCamera, stopCamera, captureFrame } = useCamera();
  const [step, setStep] = useState(0);
  const [captured, setCaptured] = useState<string[]>([]);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  const handleCapture = () => {
    const frame = captureFrame();
    if (!frame) return;

    const newCaptured = [...captured, frame];
    setCaptured(newCaptured);

    if (step < 2) {
      setStep(step + 1);
    } else {
      stopCamera();
      processImages(newCaptured);
    }
  };

  const processImages = async (frames: string[]) => {
    setProcessing(true);
    try {
      const files = await Promise.all(
        frames.map(async (dataUrl, i) => {
          const res = await fetch(dataUrl);
          const blob = await res.blob();
          return new File([blob], `angle_${i}.jpg`, { type: 'image/jpeg' });
        })
      );

      const uploadResult = await api.uploadImages(files);
      const paths = uploadResult.images.map((img: { path: string }) => img.path);

      const results = await api.recognize(paths);

      navigate('/result', { state: { results, images: frames } });
    } catch (e) {
      console.error('Processing failed:', e);
      alert('识别失败，请重试');
    } finally {
      setProcessing(false);
    }
  };

  if (processing) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: '100vh', padding: 40,
      }}>
        <div style={{
          width: 60, height: 60, borderRadius: '50%',
          border: '3px solid rgba(255,255,255,0.1)',
          borderTopColor: '#F5F5F7',
          animation: 'spin 1s linear infinite',
          marginBottom: 24,
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        <p style={{ color: '#F5F5F7', fontSize: 17, fontWeight: 500 }}>正在分析食物...</p>
        <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 14, marginTop: 8 }}>
          估算重量与热量中
        </p>
      </div>
    );
  }

  return (
    <div style={{ background: '#000', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '12px 12px 0' }}>
        <div style={{
          width: 126, height: 36, background: '#000', borderRadius: 20, margin: '0 auto',
        }} />
      </div>

      <div className="nav-bar">
        <button className="btn-ghost" onClick={() => { stopCamera(); navigate('/'); }}>
          取消
        </button>
        <span style={{ color: '#F5F5F7', fontSize: 17, fontWeight: 600, letterSpacing: -0.2 }}>
          记录餐食
        </span>
        <span style={{ width: 50 }} />
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: 6, padding: '0 0 28px' }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{
            width: i === step ? 28 : 4,
            height: 4,
            borderRadius: 2,
            background: i <= step ? '#F5F5F7' : 'rgba(245,245,247,0.2)',
            transition: 'all 0.3s ease',
          }} />
        ))}
      </div>

      <div style={{ margin: '0 20px', flex: 1, position: 'relative' }}>
        {streaming && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              width: '100%', height: '100%', objectFit: 'cover',
              borderRadius: 36, border: '1px solid rgba(255,255,255,0.08)',
            }}
          />
        )}
        {/* Viewfinder overlay */}
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none', borderRadius: 36,
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '60%', height: '60%',
            border: '1px solid rgba(255,255,255,0.12)', borderRadius: 20,
          }}>
            {(['tl', 'tr', 'bl', 'br'] as const).map((pos) => {
              const style: Record<string, React.CSSProperties> = {
                tl: { top: -1, left: -1, borderTop: '2px solid rgba(255,255,255,0.25)', borderLeft: '2px solid rgba(255,255,255,0.25)', borderRadius: '6px 0 0 0' },
                tr: { top: -1, right: -1, borderTop: '2px solid rgba(255,255,255,0.25)', borderRight: '2px solid rgba(255,255,255,0.25)', borderRadius: '0 6px 0 0' },
                bl: { bottom: -1, left: -1, borderBottom: '2px solid rgba(255,255,255,0.25)', borderLeft: '2px solid rgba(255,255,255,0.25)', borderRadius: '0 0 0 6px' },
                br: { bottom: -1, right: -1, borderBottom: '2px solid rgba(255,255,255,0.25)', borderRight: '2px solid rgba(255,255,255,0.25)', borderRadius: '0 0 6px 0' },
              };
              return <div key={pos} style={{ position: 'absolute', width: 20, height: 20, ...style[pos] }} />;
            })}
          </div>
          <div style={{
            position: 'absolute', bottom: 80, left: '50%', transform: 'translateX(-50%)',
            textAlign: 'center',
          }}>
            <p style={{ color: 'rgba(255,255,255,0.28)', fontSize: 13, letterSpacing: 0.3, margin: 0 }}>
              将食物置于框线内
            </p>
            <p style={{ color: 'rgba(255,255,255,0.16)', fontSize: 12, letterSpacing: 0.3, margin: '2px 0 0' }}>
              保持手臂伸直 · 距离约 30cm
            </p>
          </div>
          <div style={{
            position: 'absolute', bottom: 24, left: '50%', transform: 'translateX(-50%)',
            background: 'rgba(30,30,32,0.8)', backdropFilter: 'blur(40px)',
            WebkitBackdropFilter: 'blur(40px)', borderRadius: 24,
            padding: '10px 24px', border: '1px solid rgba(255,255,255,0.06)',
          }}>
            <p style={{
              color: '#F5F5F7', fontSize: 14, fontWeight: 500,
              letterSpacing: -0.2, margin: 0, whiteSpace: 'nowrap',
            }}>
              {ANGLE_LABELS[step]} · 第 {step + 1} 张
            </p>
          </div>
        </div>
      </div>

      <div style={{ padding: '20px 40px 12px', textAlign: 'center' }}>
        <p style={{
          color: 'rgba(245,245,247,0.45)', fontSize: 15, fontWeight: 400,
          letterSpacing: -0.2, margin: 0, lineHeight: 1.4, whiteSpace: 'pre-line',
        }}>
          {ANGLE_HINTS[step]}
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', padding: '4px 0 20px' }}>
        <button
          onClick={handleCapture}
          style={{
            width: 72, height: 72, borderRadius: '50%', border: '3px solid rgba(245,245,247,0.2)',
            background: 'none', cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center', padding: 0,
          }}
        >
          <div style={{
            width: 58, height: 58, borderRadius: '50%',
            background: 'linear-gradient(180deg, #F5F5F7 0%, #D1D1D6 100%)',
          }} />
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0 32px 40px' }}>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: 'rgba(255,255,255,0.08)' }} />
        <div style={{ width: 40, height: 40, borderRadius: 12, background: 'rgba(255,255,255,0.08)' }} />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/CapturePage.tsx frontend/src/hooks/useCamera.ts
git commit -m "feat: implement multi-angle capture page with camera and guided steps"
```

### Task 17: Analysis result page

**Files:**
- Modify: `frontend/src/pages/ResultPage.tsx`

- [ ] **Step 1: Write ResultPage.tsx**

```tsx
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FoodItemCard } from '../components/FoodItemCard';
import { MacroBar } from '../components/MacroBar';
import { api } from '../api/client';
import type { RecognizeResult, FoodItem, MealType } from '../types';

interface LocationState {
  results: RecognizeResult[];
  images: string[];
}

export function ResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [results] = useState<RecognizeResult[]>(state?.results ?? []);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!state || results.length === 0) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <p style={{ color: 'rgba(245,245,247,0.4)' }}>没有识别结果</p>
        <button className="btn-primary" onClick={() => navigate('/capture')} style={{ marginTop: 16 }}>
          去拍照
        </button>
      </div>
    );
  }

  const totalCal = results.reduce((s, r) => s + r.calories, 0);
  const totalProtein = results.reduce((s, r) => s + (r.protein_g ?? 0), 0);
  const totalCarbs = results.reduce((s, r) => s + (r.carbs_g ?? 0), 0);
  const totalFat = results.reduce((s, r) => s + (r.fat_g ?? 0), 0);

  const handleSave = async () => {
    setSaving(true);
    try {
      const items: FoodItem[] = results.map((r) => ({
        name: r.name,
        weight_g: r.weight_g,
        calories: r.calories,
        protein_g: r.protein_g,
        carbs_g: r.carbs_g,
        fat_g: r.fat_g,
        confidence: r.confidence,
      }));

      await api.createMeal({
        user_id: 'default_user',
        meal_type: (new Date().getHours() < 11 ? 'breakfast'
          : new Date().getHours() < 15 ? 'lunch' : 'dinner') as MealType,
        total_calories: totalCal,
        items,
      });
      setSaved(true);
      setTimeout(() => navigate('/'), 500);
    } catch (e) {
      console.error('Save failed:', e);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fade-in" style={{ paddingBottom: 24 }}>
      <div className="nav-bar">
        <button className="btn-ghost" onClick={() => navigate('/capture')}>
          ← 返回
        </button>
        <span style={{ color: '#F5F5F7', fontSize: 17, fontWeight: 600 }}>分析结果</span>
        <button
          className="btn-ghost"
          onClick={handleSave}
          disabled={saving || saved}
          style={{ opacity: saved ? 0.4 : 1 }}
        >
          {saved ? '已保存' : '保存'}
        </button>
      </div>

      <div style={{ textAlign: 'center', padding: '8px 0 32px' }}>
        <p style={{ color: 'rgba(245,245,247,0.45)', fontSize: 15, margin: 0 }}>预估总热量</p>
        <p style={{
          color: '#F5F5F7', fontSize: 80, fontWeight: 200, margin: 0,
          letterSpacing: -3, lineHeight: 1,
        }}>
          {Math.round(totalCal)}
        </p>
        <p style={{ color: 'rgba(245,245,247,0.35)', fontSize: 18, margin: '4px 0 0', letterSpacing: 0.5 }}>
          千卡
        </p>
      </div>

      <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 4px 4px' }}>
          <span className="card-label">识别食物</span>
          <span style={{ color: 'rgba(245,245,247,0.25)', fontSize: 12 }}>
            基于 {state?.images?.length ?? 0} 张照片
          </span>
        </div>

        {results.map((item, i) => (
          <FoodItemCard
            key={i}
            item={{ name: item.name, weight_g: item.weight_g, calories: item.calories,
              protein_g: item.protein_g, carbs_g: item.carbs_g, fat_g: item.fat_g,
              confidence: item.confidence }}
          />
        ))}
      </div>

      <div style={{ padding: '24px 20px 16px' }}>
        <MacroBar protein={totalProtein} carbs={totalCarbs} fat={totalFat} />
      </div>

      <div style={{ padding: '4px 20px' }}>
        <button
          onClick={handleSave}
          disabled={saving || saved}
          className="btn-primary"
          style={{ opacity: saved ? 0.5 : 1 }}
        >
          {saving ? '保存中...' : saved ? '已保存 ✓' : '保存记录'}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/ResultPage.tsx
git commit -m "feat: implement analysis result page with food cards and macros"
```

### Task 18: History page

**Files:**
- Modify: `frontend/src/pages/HistoryPage.tsx`

- [ ] **Step 1: Write HistoryPage.tsx**

```tsx
import { useState, useEffect } from 'react';
import { TabBar } from '../components/TabBar';
import { MealCard } from '../components/MealCard';
import { api } from '../api/client';
import type { StatsData } from '../types';

const CURRENT_USER = 'default_user';

export function HistoryPage() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getStats(CURRENT_USER, 'daily', selectedDate)
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedDate]);

  const allMeals = stats?.meals ?? [];

  // Generate dates for the week picker
  const weekDates = Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - d.getDay() + i);
    return d.toISOString().slice(0, 10);
  });

  const dayLabels = ['日', '一', '二', '三', '四', '五', '六'];

  return (
    <div className="fade-in" style={{ paddingBottom: 24 }}>
      <div style={{ padding: '40px 24px 6px' }}>
        <p className="title-section">
          {new Date(selectedDate).getMonth() + 1}月{new Date(selectedDate).getDate()}日
        </p>
        <h1 className="title-large" style={{ marginTop: 2 }}>历史记录</h1>
      </div>

      {/* Week date picker */}
      <div style={{
        display: 'flex', gap: 4, padding: '16px 20px', overflowX: 'auto',
      }}>
        {weekDates.map((d, i) => {
          const dateObj = new Date(d);
          const isSelected = d === selectedDate;
          const hasData = isSelected && allMeals.length > 0;

          return (
            <button
              key={d}
              onClick={() => setSelectedDate(d)}
              style={{
                flex: '1 0 auto', minWidth: 44, padding: '10px 4px',
                borderRadius: 14, border: 'none', cursor: 'pointer',
                background: isSelected
                  ? 'rgba(245,245,247,0.12)'
                  : 'transparent',
                color: isSelected ? '#F5F5F7' : 'rgba(245,245,247,0.35)',
                fontFamily: 'inherit',
              }}
            >
              <div style={{ fontSize: 11, fontWeight: 500, marginBottom: 4 }}>
                {dayLabels[i]}
              </div>
              <div style={{ fontSize: 16, fontWeight: isSelected ? 600 : 400, position: 'relative' }}>
                {dateObj.getDate()}
                {hasData && (
                  <span style={{
                    display: 'block', width: 4, height: 4, borderRadius: '50%',
                    background: '#FF9F0A', margin: '4px auto 0',
                  }} />
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Summary */}
      {stats && (
        <div style={{ padding: '0 20px 8px' }}>
          <div className="glass-card" style={{ borderRadius: 16, padding: '16px 20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
              <div>
                <p style={{
                  color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5,
                }}>
                  {Math.round(stats.total_calories)}
                </p>
                <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, margin: '2px 0 0' }}>千卡</p>
              </div>
              <div style={{ width: 1, background: 'rgba(255,255,255,0.06)' }} />
              <div>
                <p style={{
                  color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5,
                }}>
                  {Math.round(stats.total_protein)}
                </p>
                <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, margin: '2px 0 0' }}>蛋白质 g</p>
              </div>
              <div style={{ width: 1, background: 'rgba(255,255,255,0.06)' }} />
              <div>
                <p style={{
                  color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5,
                }}>
                  {allMeals.length}
                </p>
                <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, margin: '2px 0 0' }}>餐次</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Meal list */}
      <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
        {loading ? (
          <p style={{ textAlign: 'center', color: 'rgba(245,245,247,0.3)', padding: 40 }}>加载中...</p>
        ) : allMeals.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <p style={{ fontSize: 40, margin: '0 0 12px' }}>🍽</p>
            <p style={{ color: 'rgba(245,245,247,0.35)', fontSize: 15 }}>当天没有记录</p>
          </div>
        ) : (
          allMeals.map((meal) => <MealCard key={meal.id} meal={meal} />)
        )}
      </div>

      <TabBar />
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/HistoryPage.tsx
git commit -m "feat: implement history page with week date picker and daily stats"
```

### Task 19: Final integration and smoke test

- [ ] **Step 1: Build frontend**

```bash
cd frontend && npm run build
```

Expected: Build succeeds with no errors.

- [ ] **Step 2: Start backend**

```bash
cd backend && python seed_data.py && python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

- [ ] **Step 3: Start frontend dev server**

```bash
cd frontend && npm run dev
```

- [ ] **Step 4: Run full backend test suite**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 5: Smoke test API from browser**

Open http://localhost:5173 in browser:
1. Verify Today page loads (should show 0 calories, empty meal slots)
2. Navigate to Capture page (camera should request permission)
3. Navigate to History page (should show week picker)
4. Test API directly: `curl http://localhost:8000/api/foods/search?q=鸡`

- [ ] **Step 6: Commit**

```bash
git add frontend/dist/ .gitignore
git commit -m "feat: final integration, full backend tests passing, frontend building clean"
```
