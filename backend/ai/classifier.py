import os
import base64
from anthropic import Anthropic
from PIL import Image


THUMBNAIL_SIZE = 224


def _resize_to_base64(image_path: str) -> tuple[str, str]:
    """Resize image to thumbnail and return (base64_data, media_type)."""
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    media_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    img = Image.open(image_path).convert("RGB")
    img.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE), Image.LANCZOS)

    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    return base64.b64encode(buf.getvalue()).decode("utf-8"), "image/jpeg"


def classify_food(image_path: str) -> dict:
    """Identify food in image using Claude Haiku Vision."""
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
    if not api_key:
        return {"name": "unknown", "confidence": 0.0, "source": "none", "error": "No API key"}

    image_data, media_type = _resize_to_base64(image_path)

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20,
        thinking={"type": "disabled"},
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
                    "text": '这张照片里是一种什么食物？只回复食物名称（中文），例如土豆块、白米饭、鸡胸肉。不要其他内容。',
                },
            ],
        }],
    )

    for block in response.content:
        if hasattr(block, "text"):
            name = block.text.strip()
            return {"name": name, "confidence": 0.9, "source": "haiku"}

    return {"name": "unknown", "confidence": 0.0, "source": "haiku", "error": "No text in response"}
