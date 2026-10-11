"""Evaluations for Study Planner schema validity, daily time constraints, and curriculum topic coverage."""

import pytest
from pydantic import ValidationError

from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyActivity, StudyDay, StudyPlan
from study_coach.tools.planning_tools import validate_study_plan


def test_study_planner_constraint_evaluation_scenario_1() -> None:
    """Evaluate 14 days, beginner, 90 minutes daily plan constraints."""
    activities = [
        StudyActivity(
            activity_type="learning",
            topic_id="genai_concepts",
            description="Overview of Generative AI concepts",
            duration_minutes=45,
        ),
        StudyActivity(
            activity_type="practice",
            topic_id="genai_concepts",
            description="Formative Practice Quiz",
            duration_minutes=45,
        ),
    ]
    days = [
        StudyDay(
            day_number=i,
            title=f"Day {i} Theme",
            total_minutes=90,
            activities=activities,
        )
        for i in range(1, 15)
    ]
    plan = StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=14,
        daily_study_minutes=90,
        days=days,
        total_planned_minutes=14 * 90,
        planning_notes="Well-balanced beginner curriculum schedule.",
    )

    validated = validate_study_plan(plan.model_dump())
    assert validated.days_until_exam == 14
    assert len(validated.days) == 14
    for day in validated.days:
        assert day.total_minutes <= 90
        assert sum(a.duration_minutes for a in day.activities) == day.total_minutes


def test_study_planner_rejects_exceeded_daily_minutes() -> None:
    """Deterministic evaluation: day exceeding daily budget must fail validation."""
    days = [
        StudyDay(
            day_number=1,
            title="Overloaded Day",
            total_minutes=120,
            activities=[
                StudyActivity(
                    activity_type="learning",
                    topic_id="genai_concepts",
                    description="Heavy Reading",
                    duration_minutes=120,
                )
            ],
        )
    ]
    plan_dict = {
        "certification_name": "Google Cloud Generative AI Leader",
        "days_until_exam": 1,
        "daily_study_minutes": 60,
        "days": [d.model_dump() for d in days],
        "total_planned_minutes": 120,
        "planning_notes": "Exceeds daily budget test.",
    }

    with pytest.raises(ValidationError, match="exceeds daily limit"):
        validate_study_plan(plan_dict)


def test_study_planner_handles_invalid_minutes_scenario_10() -> None:
    """Scenario 10: daily_study_minutes <= 0 rejected by StudentProfile schema."""
    with pytest.raises(ValidationError):
        StudentProfile(experience_level="beginner", daily_study_minutes=0)
