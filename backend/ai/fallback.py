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
