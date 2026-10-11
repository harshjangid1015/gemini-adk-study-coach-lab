"""Unit and integration tests for WorkshopFacade."""

import pytest

from study_coach.models.quiz import Quiz, QuizQuestion, QuizSubmission
from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyActivity, StudyDay, StudyPlan
from study_coach.services.learning_session import LearningSessionService
from study_coach.services.workshop_facade import WorkshopFacade
from study_coach.workflows.adaptive_study import AdaptiveStudyWorkflow


def create_sample_quiz() -> Quiz:
    return Quiz(
        certification_name="Google Cloud Generative AI Leader",
        topic_ids=["genai_concepts", "llm_architecture"],
        experience_level="beginner",
        questions=[
            QuizQuestion(
                question_id="q1",
                topic_id="genai_concepts",
                question_text="What is Generative AI primarily capable of doing?",
                options={
                    "A": "Creating new novel text, images, and content",
                    "B": "Only filtering tabular spreadsheets",
                    "C": "Compressing database log files",
                    "D": "Executing CPU BIOS instructions",
                },
                correct_answer="A",
                explanation="Generative AI creates new content from learned data distributions.",
                difficulty="beginner",
            ),
            QuizQuestion(
                question_id="q2",
                topic_id="llm_architecture",
                question_text="Which architecture serves as the foundation for modern LLMs?",
                options={
                    "A": "Transformer architecture",
                    "B": "Linear regression models",
                    "C": "Single layer perceptron",
                    "D": "Decision trees",
                },
                correct_answer="A",
                explanation="Transformers provide the foundational attention mechanism for modern LLMs.",
                difficulty="beginner",
            ),
        ],
    )


def test_facade_curriculum_topics_lookup() -> None:
    facade = WorkshopFacade()
    topics = facade.get_supported_curriculum_topics()
    assert len(topics) >= 4
    topic_ids = [t["id"] for t in topics]
    assert "genai_concepts" in topic_ids
    assert "llm_architecture" in topic_ids
    assert "responsible_ai" in topic_ids
    assert "vertex_ai_studio" in topic_ids


@pytest.mark.anyio
async def test_facade_session_management_and_isolation() -> None:
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    facade = WorkshopFacade(session_service=svc, workflow=workflow)

    profile_1 = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    profile_2 = StudentProfile(experience_level="advanced", daily_study_minutes=45)

    sess_1 = await facade.get_or_create_session(
        session_id="ui_sess_1",
        user_id="alice",
        student_profile=profile_1,
        certification_name="Google Cloud Generative AI Leader",
        days_remaining=14,
    )
    sess_2 = await facade.get_or_create_session(
        session_id="ui_sess_2",
        user_id="bob",
        student_profile=profile_2,
        certification_name="Google Cloud Generative AI Leader",
        days_remaining=7,
    )

    assert sess_1.user_id == "alice"
    assert sess_2.user_id == "bob"
    assert sess_1.student_profile.daily_study_minutes == 90
    assert sess_2.student_profile.daily_study_minutes == 45

    # Check persistence across calls
    fetched = await facade.get_session("ui_sess_1", "alice")
    assert fetched is not None
    assert fetched.session_id == "ui_sess_1"


@pytest.mark.anyio
async def test_facade_quiz_submission_and_answer_security() -> None:
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    facade = WorkshopFacade(session_service=svc, workflow=workflow)

    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    sess = await facade.get_or_create_session("sec_sess", "sec_user", profile)

    quiz = create_sample_quiz()
    sess.stored_quizzes["quiz_test"] = quiz
    sess.current_quiz_id = "quiz_test"
    await svc.save_session(sess)

    # 1. Verify student view hides answers
    sanitized = sess.get_sanitized_quiz("quiz_test")
    assert len(sanitized) == 2
    for sq in sanitized:
        assert not hasattr(sq, "correct_answer")
        assert not hasattr(sq, "explanation")

    # 2. Submit answers (1 correct, 1 incorrect)
    sub = QuizSubmission(
        quiz_id="quiz_test",
        student_answers={"q1": "A", "q2": "B"},
    )
    result = await facade.submit_quiz("sec_sess", "sec_user", sub)
    assert result.total_questions == 2
    assert result.correct_answers == 1
    assert result.score_percentage == 50.0
    assert "llm_architecture" in result.weak_topics
    assert "genai_concepts" in result.strong_topics

    # 3. Verify progress retrieval
    prog = await facade.get_learning_progress("sec_sess", "sec_user")
    assert prog.total_quizzes_taken == 1
    assert prog.total_questions_attempted == 2
    assert prog.total_questions_correct == 1
    assert prog.overall_score_percentage == 50.0


@pytest.mark.anyio
async def test_facade_adaptive_plan_rejection_without_quiz() -> None:
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    facade = WorkshopFacade(session_service=svc, workflow=workflow)

    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    sess = await facade.get_or_create_session("no_quiz_sess", "u1", profile)

    plan = StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=1,
        daily_study_minutes=90,
        days=[
            StudyDay(
                day_number=1,
                title="Intro",
                activities=[
                    StudyActivity(
                        topic_id="genai_concepts",
                        activity_type="learning",
                        description="Intro",
                        duration_minutes=90,
                    )
                ],
                total_minutes=90,
            )
        ],
        total_planned_minutes=90,
        planning_notes="Initial",
    )
    sess.current_study_plan = plan
    await svc.save_session(sess)

    with pytest.raises(
        ValueError,
        match="Cannot claim adaptive replanning occurred without quiz evidence",
    ):
        await facade.adapt_study_plan("no_quiz_sess", "u1", completed_days=0)
