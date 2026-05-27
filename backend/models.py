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
