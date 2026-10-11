import pytest

from study_coach.tools.planning_tools import (
    calculate_available_minutes,
    calculate_plan_totals,
)


def test_calculate_available_minutes() -> None:
    assert calculate_available_minutes(10, 60) == 600
    with pytest.raises(ValueError):
        calculate_available_minutes(-1, 60)


def test_calculate_plan_totals() -> None:
    plan_dict = {
        "days": [
            {"activities": [{"duration_minutes": 30}, {"duration_minutes": 20}]},
            {"activities": [{"duration_minutes": 40}]},
        ]
    }
    result = calculate_plan_totals(plan_dict)
    assert result["days"][0]["total_minutes"] == 50
    assert result["days"][1]["total_minutes"] == 40
    assert result["total_planned_minutes"] == 90
