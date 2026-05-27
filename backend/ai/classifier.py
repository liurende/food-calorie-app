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
