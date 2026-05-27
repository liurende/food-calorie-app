from database import get_db


class WeightCalculator:
    """Converts food volume + classification → weight → calories using density DB."""

    def calculate(self, food_name: str, volume_cm3: float) -> dict:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM food_density WHERE name=? OR name_en=?",
            (food_name, food_name),
        ).fetchone()
        conn.close()

        if row is None:
            return {
                "name": food_name,
                "weight_g": 0,
                "calories": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "confidence": 0.0,
                "error": f"Food '{food_name}' not found in density database",
            }

        density = row["density_g_cm3"]
        weight_g = round(volume_cm3 * density, 1)
        calories = round(weight_g * row["calories_per_100g"] / 100.0, 1)
        protein = round(weight_g * (row["protein_per_100g"] or 0) / 100.0, 1)
        carbs = round(weight_g * (row["carbs_per_100g"] or 0) / 100.0, 1)
        fat = round(weight_g * (row["fat_per_100g"] or 0) / 100.0, 1)

        return {
            "name": row["name"],
            "weight_g": weight_g,
            "calories": calories,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "confidence": 0.0,
        }
