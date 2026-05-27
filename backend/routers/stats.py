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
