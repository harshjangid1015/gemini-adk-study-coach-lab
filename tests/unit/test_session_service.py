import pytest

from study_coach.models.student import StudentProfile
from study_coach.services.learning_session import LearningSessionService


@pytest.mark.anyio
async def test_session_lifecycle_and_creation() -> None:
    svc = LearningSessionService()
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    sess = await svc.get_or_create_session(
        session_id="s1",
        user_id="user1",
        student_profile=profile,
        certification_name="Google Cloud Generative AI Leader",
        days_remaining=14,
    )
    assert sess.session_id == "s1"
    assert sess.user_id == "user1"
    assert sess.student_profile.daily_study_minutes == 90
    assert sess.exam_deadline_or_days_remaining == 14

    # Fetching again retrieves same state
    fetched = await svc.get_session(session_id="s1", user_id="user1")
    assert fetched is not None
    assert fetched.session_id == "s1"
    assert fetched.user_id == "user1"


@pytest.mark.anyio
async def test_session_isolation_between_students() -> None:
    svc = LearningSessionService()
    profile1 = StudentProfile(experience_level="beginner", daily_study_minutes=60)
    profile2 = StudentProfile(experience_level="advanced", daily_study_minutes=45)

    sess1 = await svc.get_or_create_session(
        session_id="s1",
        user_id="alice",
        student_profile=profile1,
        days_remaining=7,
    )
    sess2 = await svc.get_or_create_session(
        session_id="s2",
        user_id="bob",
        student_profile=profile2,
        days_remaining=21,
    )

    assert sess1.user_id == "alice"
    assert sess2.user_id == "bob"
    assert sess1.exam_deadline_or_days_remaining == 7
    assert sess2.exam_deadline_or_days_remaining == 21

    # Modify sess1 and verify sess2 is unaffected
    sess1.weak_topics = ["genai_concepts"]
    await svc.save_session(sess1)

    fetched2 = await svc.get_session(session_id="s2", user_id="bob")
    assert fetched2 is not None
    assert fetched2.weak_topics == []


@pytest.mark.anyio
async def test_delete_session() -> None:
    svc = LearningSessionService()
    sess = await svc.get_or_create_session(
        session_id="temp_sess",
        user_id="temp_user",
    )
    assert sess is not None

    await svc.delete_session(session_id="temp_sess", user_id="temp_user")
    fetched = await svc.get_session(session_id="temp_sess", user_id="temp_user")
    assert fetched is None
