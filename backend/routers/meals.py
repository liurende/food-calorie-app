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
