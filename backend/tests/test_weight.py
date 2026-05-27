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
    calc = WeightCalculator()
    result = calc.calculate("外星食物", 100.0)
    assert "error" in result
    assert result["confidence"] == 0.0
