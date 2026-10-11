import pytest
from pydantic import ValidationError

from study_coach.models.learning_session import LearningSession
from study_coach.models.quiz import Quiz, QuizQuestion
from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyActivity, StudyDay, StudyPlan


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


def test_valid_learning_session_initialization() -> None:
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = LearningSession(
        session_id="sess_001",
        user_id="user_001",
        student_profile=profile,
        certification_name="Google Cloud Generative AI Leader",
        exam_deadline_or_days_remaining=14,
    )

    assert session.session_id == "sess_001"
    assert session.user_id == "user_001"
    assert session.plan_revision == 1
    assert session.current_study_plan is None
    assert len(session.study_plan_history) == 0
    assert len(session.stored_quizzes) == 0
    assert session.learning_progress.total_quizzes_taken == 0


def test_invalid_session_deadline_or_revision() -> None:
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    with pytest.raises(ValidationError):
        LearningSession(
            session_id="sess_bad",
            user_id="user_001",
            student_profile=profile,
            certification_name="Test Cert",
            exam_deadline_or_days_remaining=0,  # Must be > 0
        )

    with pytest.raises(ValidationError):
        LearningSession(
            session_id="sess_bad2",
            user_id="user_001",
            student_profile=profile,
            certification_name="Test Cert",
            exam_deadline_or_days_remaining=14,
            plan_revision=0,  # Must be >= 1
        )


def test_sanitized_quiz_isolation() -> None:
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = LearningSession(
        session_id="sess_quiz",
        user_id="user_001",
        student_profile=profile,
        certification_name="Google Cloud Generative AI Leader",
        exam_deadline_or_days_remaining=14,
    )
    quiz = create_sample_quiz()
    session.stored_quizzes["quiz_1"] = quiz
    session.current_quiz_id = "quiz_1"

    student_questions = session.get_sanitized_quiz()
    assert len(student_questions) == 2

    # Verify answer keys and private explanations are omitted
    for sq in student_questions:
        assert not hasattr(sq, "correct_answer")
        assert not hasattr(sq, "explanation")
        assert sq.question_id in ["q1", "q2"]
        assert len(sq.options) == 4


def test_unknown_quiz_id_raises_error() -> None:
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = LearningSession(
        session_id="sess_quiz",
        user_id="user_001",
        student_profile=profile,
        certification_name="Google Cloud Generative AI Leader",
        exam_deadline_or_days_remaining=14,
    )
    with pytest.raises(ValueError, match="No quiz found with ID"):
        session.get_sanitized_quiz("non_existent_quiz")


def test_adk_state_serialization_roundtrip() -> None:
    profile = StudentProfile(experience_level="intermediate", daily_study_minutes=60)
    plan = StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=1,
        daily_study_minutes=60,
        days=[
            StudyDay(
                day_number=1,
                title="Foundations",
                activities=[
                    StudyActivity(
                        topic_id="genai_concepts",
                        activity_type="learning",
                        description="Study LLMs",
                        duration_minutes=60,
                    )
                ],
                total_minutes=60,
            )
        ],
        total_planned_minutes=60,
        planning_notes="Initial test plan",
    )
    session = LearningSession(
        session_id="sess_roundtrip",
        user_id="user_test",
        student_profile=profile,
        certification_name="Google Cloud Generative AI Leader",
        exam_deadline_or_days_remaining=1,
        current_study_plan=plan,
        study_plan_history=[plan],
        weak_topics=["llm_architecture"],
        strong_topics=["genai_concepts"],
        plan_revision=2,
    )

    adk_dict = session.to_adk_state()
    assert isinstance(adk_dict, dict)
    assert adk_dict["session_id"] == "sess_roundtrip"
    assert adk_dict["plan_revision"] == 2
    assert adk_dict["weak_topics"] == ["llm_architecture"]

    rebuilt = LearningSession.from_adk_state(adk_dict)
    assert rebuilt.session_id == session.session_id
    assert rebuilt.plan_revision == 2
    assert rebuilt.current_study_plan is not None
    assert rebuilt.current_study_plan.days_until_exam == 1
    assert rebuilt.weak_topics == ["llm_architecture"]
