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
            density = 0.7
            cal_per_100g = 150.0
            protein_per_100g = 5.0
            carbs_per_100g = 15.0
            fat_per_100g = 7.0
        else:
            density = row["density_g_cm3"]
            cal_per_100g = row["calories_per_100g"]
            protein_per_100g = row["protein_per_100g"] or 0
            carbs_per_100g = row["carbs_per_100g"] or 0
            fat_per_100g = row["fat_per_100g"] or 0

        weight_g = round(volume_cm3 * density, 1)
        calories = round(weight_g * cal_per_100g / 100.0, 1)
        protein = round(weight_g * protein_per_100g / 100.0, 1)
        carbs = round(weight_g * carbs_per_100g / 100.0, 1)
        fat = round(weight_g * fat_per_100g / 100.0, 1)

        return {
            "name": food_name,
            "weight_g": weight_g,
            "calories": calories,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "confidence": 0.0,
        }
