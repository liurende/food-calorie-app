from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from engine.reconstruction import VolumeEstimator
from engine.weight import WeightCalculator
from ai.classifier import classify_food

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

    calculator = WeightCalculator()
    result = calculator.calculate(classification["name"], volume_result["volume_cm3"])
    result["confidence"] = classification["confidence"]
    result["volume_cm3"] = volume_result["volume_cm3"]

    return [result]
