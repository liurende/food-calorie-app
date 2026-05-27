from fastapi import APIRouter
from database import get_db
from models import UserProfile

router = APIRouter(prefix="/api")

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def calc_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    """Mifflin-St Jeor equation."""
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "male":
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 1)


def calc_tdee(bmr: float, activity_level: str) -> float:
    return round(bmr * ACTIVITY_FACTORS.get(activity_level, 1.55), 1)


@router.get("/profile")
def get_profile(user_id: str = ""):
    if not user_id:
        return {"error": "user_id required"}, 400
    conn = get_db()
    row = conn.execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row is None:
        return {"profile": None, "bmr": None, "tdee": None}
    profile = dict(row)
    bmr = None
    tdee = None
    if profile.get("gender") and profile.get("weight_kg") and profile.get("height_cm") and profile.get("age"):
        bmr = calc_bmr(profile["gender"], profile["weight_kg"], profile["height_cm"], profile["age"])
        tdee = calc_tdee(bmr, profile.get("activity_level", "moderate"))
    return {"profile": profile, "bmr": bmr, "tdee": tdee}


@router.put("/profile")
def update_profile(profile: UserProfile):
    conn = get_db()
    conn.execute(
        """INSERT INTO user_profiles (user_id, name, gender, age, height_cm, weight_kg, activity_level, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(user_id) DO UPDATE SET
           name=excluded.name, gender=excluded.gender, age=excluded.age,
           height_cm=excluded.height_cm, weight_kg=excluded.weight_kg,
           activity_level=excluded.activity_level, updated_at=CURRENT_TIMESTAMP""",
        (profile.user_id, profile.name, profile.gender, profile.age,
         profile.height_cm, profile.weight_kg, profile.activity_level),
    )
    conn.commit()
    conn.close()

    # Re-read to compute BMR
    conn = get_db()
    row = conn.execute("SELECT * FROM user_profiles WHERE user_id=?", (profile.user_id,)).fetchone()
    conn.close()
    result = dict(row)
    bmr = None
    tdee = None
    if result.get("gender") and result.get("weight_kg") and result.get("height_cm") and result.get("age"):
        bmr = calc_bmr(result["gender"], result["weight_kg"], result["height_cm"], result["age"])
        tdee = calc_tdee(bmr, result.get("activity_level", "moderate"))
    return {"profile": result, "bmr": bmr, "tdee": tdee}
