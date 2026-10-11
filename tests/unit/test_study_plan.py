import pytest
from pydantic import ValidationError

from study_coach.models.study_plan import StudyActivity, StudyDay
from study_coach.tools.planning_tools import validate_study_plan


def test_valid_study_plan() -> None:
    plan_data = {
        "certification_name": "Google Cloud GenAI Leader",
        "days_until_exam": 2,
        "daily_study_minutes": 90,
        "total_planned_minutes": 90,
        "planning_notes": "A simple plan.",
        "days": [
            {
                "day_number": 1,
                "title": "Day 1",
                "total_minutes": 40,
                "activities": [
                    {
                        "topic_id": "genai_concepts",
                        "activity_type": "learning",
                        "description": "Learn concepts",
                        "duration_minutes": 40,
                    }
                ],
            },
            {
                "day_number": 2,
                "title": "Day 2",
                "total_minutes": 50,
                "activities": [
                    {
                        "topic_id": "llm_architecture",
                        "activity_type": "practice",
                        "description": "Practice LLMs",
                        "duration_minutes": 50,
                    }
                ],
            },
        ],
    }
    plan = validate_study_plan(plan_data)
    assert plan.days_until_exam == 2


def test_invalid_total_minutes() -> None:
    with pytest.raises(ValidationError):
        StudyDay(
            day_number=1,
            title="Day 1",
            total_minutes=50,  # Intentional mismatch
            activities=[
                StudyActivity(
                    topic_id="genai_concepts",
                    activity_type="learning",
                    description="Read",
                    duration_minutes=40,
                )
            ],
        )


def test_unknown_topic_id() -> None:
    plan_data = {
        "certification_name": "Google Cloud GenAI Leader",
        "days_until_exam": 1,
        "daily_study_minutes": 90,
        "total_planned_minutes": 40,
        "planning_notes": "A simple plan.",
        "days": [
            {
                "day_number": 1,
                "title": "Day 1",
                "total_minutes": 40,
                "activities": [
                    {
                        "topic_id": "invalid_topic",
                        "activity_type": "learning",
                        "description": "Learn concepts",
                        "duration_minutes": 40,
                    }
                ],
            }
        ],
    }
    with pytest.raises(ValueError):
        validate_study_plan(plan_data)
