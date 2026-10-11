from typing import Any

from study_coach.models.study_plan import StudyPlan


def calculate_available_minutes(days: int, daily_minutes: int) -> int:
    """Calculates the total available study minutes."""
    if days < 0 or daily_minutes < 0:
        raise ValueError("Days and daily_minutes must be non-negative")
    return days * daily_minutes


def calculate_plan_totals(plan_dict: dict[str, Any]) -> dict[str, Any]:
    """Recalculates totals in a plan dictionary to ensure consistency."""
    total_planned_minutes = 0
    for day in plan_dict.get("days", []):
        day_total = 0
        for act in day.get("activities", []):
            day_total += act.get("duration_minutes", 0)
        day["total_minutes"] = day_total
        total_planned_minutes += day_total
    plan_dict["total_planned_minutes"] = total_planned_minutes
    return plan_dict


def validate_study_plan(plan_data: dict[str, Any]) -> StudyPlan:
    """Validates the study plan dict against the Pydantic models."""
    from study_coach.tools.curriculum_tools import load_curriculum

    plan = StudyPlan.model_validate(plan_data)

    curriculum = load_curriculum()
    valid_topic_ids = {topic["id"] for topic in curriculum.get("topics", [])}

    for day in plan.days:
        for act in day.activities:
            if act.topic_id not in valid_topic_ids:
                raise ValueError(f"Unknown topic ID: {act.topic_id}")

    return plan
