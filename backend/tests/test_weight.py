import pytest
from engine.weight import WeightCalculator
from database import init_db
from seed_data import seed


def test_calculate_known_food():
    init_db()
    seed()
    calc = WeightCalculator()
    result = calc.calculate("白米饭", 200.0)
    assert result["name"] == "白米饭"
    assert result["weight_g"] == pytest.approx(170.0, rel=0.2)
    assert result["calories"] > 0
    assert result["protein_g"] > 0
    assert result["carbs_g"] > 0


def test_unknown_food():
    """Unknown food uses sensible defaults (density=0.7, cal=150/100g)."""
    calc = WeightCalculator()
    result = calc.calculate("外星食物", 100.0)
    assert result["name"] == "外星食物"
    assert result["weight_g"] == pytest.approx(70.0, rel=0.1)  # 100cm³ × 0.7
    assert result["calories"] == pytest.approx(105.0, rel=0.1)  # 70g × 150/100
