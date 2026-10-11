import pytest
from pydantic import ValidationError

from study_coach.models.student import StudentProfile, StudyRequest


def test_valid_student_profile() -> None:
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=60)
    assert profile.experience_level == "beginner"
    assert profile.daily_study_minutes == 60


def test_invalid_experience_level() -> None:
    with pytest.raises(ValidationError):
        StudentProfile(experience_level="expert", daily_study_minutes=60)  # type: ignore


def test_invalid_daily_study_minutes() -> None:
    with pytest.raises(ValidationError):
        StudentProfile(experience_level="beginner", daily_study_minutes=0)

    with pytest.raises(ValidationError):
        StudentProfile(experience_level="beginner", daily_study_minutes=500)


def test_valid_study_request() -> None:
    profile = StudentProfile(experience_level="intermediate", daily_study_minutes=90)
    request = StudyRequest(
        certification_name="GCP ACE", days_until_exam=30, student_profile=profile
    )
    assert request.certification_name == "GCP ACE"
    assert request.days_until_exam == 30
    assert request.student_profile.experience_level == "intermediate"


def test_invalid_exam_deadline() -> None:
    profile = StudentProfile(experience_level="advanced", daily_study_minutes=120)
    with pytest.raises(ValidationError):
        StudyRequest(
            certification_name="GCP PCA", days_until_exam=0, student_profile=profile
        )


def test_empty_certification_name() -> None:
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=60)
    with pytest.raises(ValidationError):
        StudyRequest(certification_name="", days_until_exam=30, student_profile=profile)


def test_valid_study_request_json() -> None:
    json_data = {
        "certification_name": "Google Cloud Generative AI Leader",
        "days_until_exam": 14,
        "student_profile": {
            "experience_level": "beginner",
            "daily_study_minutes": 90,
            "learning_preferences": ["video", "hands-on"],
        },
    }
    request = StudyRequest.model_validate(json_data)
    assert request.certification_name == "Google Cloud Generative AI Leader"
    assert request.student_profile.daily_study_minutes == 90
