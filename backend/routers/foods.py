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
