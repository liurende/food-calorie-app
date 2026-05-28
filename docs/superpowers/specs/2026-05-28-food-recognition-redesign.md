# Food Recognition Redesign — Mixed Local + API

## Motivation

Current pipeline: ONNX model file is missing → simulated classifier (MD5-hash-based random pick) → Vision API fallback. Every recognition hits the API anyway, but the flow is unnecessarily complex and the simulated classifier is misleading. The user wants: (a) recognize only simple single-ingredient foods (rice, potatoes, vegetables, meat cuts, not mixed dishes), (b) low cost per recognition.

## Design

### Pipeline (simplified)

```
3 photos
    │
    ├──→ OpenCV SIFT + triangulation → volume (cm³)     [local]
    │
    └──→ 1 thumbnail (≤224px) → Claude Haiku → food name [API]
            │
            ▼
        density DB (200+ simple foods) → density lookup  [local]
            │
            ▼
        weight = volume × density → calories + macros
```

Only one API call per meal (send the primary/front-view image only). The 3D reconstruction uses all 3 images but runs locally.

### What changes

1. **`ai/classifier.py`** — Remove ONNX runtime import, remove `_simulated_classify`, remove `get_labels`. One function: `classify_food(image_path)` → calls Haiku Vision, returns `{"name": "...", "confidence": N, "source": "vision_api"}`.

2. **`ai/fallback.py`** — Delete this file. No more fallback concept; Haiku is the primary and only path.

3. **`routers/recognize.py`** — Remove the confidence < 0.7 branching. Just call `classify_food`, then `WeightCalculator.calculate`. Fewer imports, simpler control flow.

4. **`seed_data.py`** — Expand from ~55 foods to 200+. Categories:
   - 主食 (staples): 米、糙米、小米、黑米、糯米、馒头、花卷、面条、米粉、河粉、全麦面包、白面包、玉米(整)、玉米粒、红薯、紫薯、土豆、山药、芋头、燕麦片、小米粥、白粥、凉皮
   - 绿叶蔬菜: 菠菜、生菜、油麦菜、小白菜、空心菜、茼蒿、韭菜、芹菜茎、西兰花、花菜、卷心菜、大白菜
   - 根茎/瓜果蔬菜: 黄瓜、番茄、胡萝卜、白萝卜、茄子、西葫芦、冬瓜、南瓜、丝瓜、苦瓜、豆角、四季豆、荷兰豆、青椒、红椒
   - 菌菇: 香菇、平菇、金针菇、杏鲍菇、木耳、银耳
   - 肉类 (熟): 鸡胸肉、鸡腿肉、鸡翅(熟)、猪里脊、猪五花、猪排骨、牛肉(瘦)、牛腩、羊肉、羊排、鸭肉、鹅肉
   - 水产 (熟): 三文鱼、虾仁、带鱼、鲈鱼、鳕鱼、鲫鱼、草鱼、鲢鱼、龙利鱼柳、鱿鱼、章鱼
   - 豆制品: 豆腐(嫩)、豆腐(老)、豆干、千张、腐竹、毛豆、黄豆芽、绿豆芽
   - 蛋类: 煮鸡蛋、炒鸡蛋、蒸蛋、咸鸭蛋、鹌鹑蛋
   - 水果: 苹果、香蕉、橙子、葡萄、草莓、蓝莓、西瓜、哈密瓜、猕猴桃、桃子、梨、芒果、菠萝、柚子、樱桃、荔枝、龙眼、火龙果、牛油果、柠檬
   - 坚果种子: 花生、核桃、杏仁、腰果、开心果、瓜子、南瓜子、芝麻
   - 汤品: 蛋花汤、紫菜汤

5. **`requirements.txt`** — Remove `onnxruntime` (no longer used). Keep everything else: `numpy` and `opencv-contrib-python` are still needed by the 3D reconstruction engine; `pillow` for image resize; `anthropic` for Haiku.

6. **Frontend** — No structural changes needed. The API contract (`RecognizeResult`) stays the same.

### Cost

Claude Haiku image input: $0.25/million input tokens. A 224×224 thumbnail generates ~150-200 input tokens. That's ~ $0.00005 per image, or ~¥0.00035. 

Per meal: ~¥0.00035 (effectively free). Even at 100 meals/month, the cost is negligible.

### What's NOT changing

- 3D reconstruction pipeline (OpenCV SIFT, triangulation, convex hull) — unchanged
- `engine/weight.py` — unchanged
- All other routers (upload, meals, stats, foods, profile) — unchanged
- Frontend pages — unchanged
- Dockerfile — remove `libgl1-mesa-glx libglib2.0-0` apt packages (no OpenCV system deps needed? check) — actually OpenCV still needs these for SIFT

### Risks

- Haiku may misidentify visually similar foods (e.g., chicken breast vs turkey breast). Acceptable trade-off for MVP.
- The density DB lookup matches on exact name; if Haiku returns a name not in the DB, we fall back to sensible defaults (density=0.7, cal/100g=150). This is handled in `weight.py` already.
