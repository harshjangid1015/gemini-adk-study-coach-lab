import pytest

from study_coach.models.quiz import Quiz, QuizQuestion, QuizSubmission
from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyActivity, StudyDay, StudyPlan
from study_coach.services.learning_session import LearningSessionService
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
            QuizQuestion(
                question_id="q3",
                topic_id="llm_architecture",
                question_text="What is the key role of self-attention in transformers?",
                options={
                    "A": "Allows model to weigh relationships between all tokens in context",
                    "B": "Compiles Python bytecode to machine code",
                    "C": "Indexes relational SQL databases",
                    "D": "Regulates power supply to GPU fans",
                },
                correct_answer="A",
                explanation="Self-attention computes dynamic weights representing contextual token relationships.",
                difficulty="beginner",
            ),
        ],
    )


@pytest.mark.anyio
async def test_submit_quiz_before_quiz_created_fails() -> None:
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    await svc.get_or_create_session(
        session_id="s1", user_id="u1", student_profile=profile
    )

    sub = QuizSubmission(
        quiz_id="quiz_1",
        student_answers={"q1": "A"},
    )
    with pytest.raises(
        ValueError, match="Cannot evaluate submission before creating a quiz"
    ):
        await workflow.submit_quiz_answers("s1", "u1", sub)


@pytest.mark.anyio
async def test_replan_without_quiz_results_fails() -> None:
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = await svc.get_or_create_session(
        session_id="s1", user_id="u1", student_profile=profile
    )

    plan = StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=1,
        daily_study_minutes=90,
        days=[
            StudyDay(
                day_number=1,
                title="Day 1",
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
    session.current_study_plan = plan
    await svc.save_session(session)

    with pytest.raises(
        ValueError,
        match="Cannot claim adaptive replanning occurred without quiz evidence",
    ):
        await workflow.generate_adapted_plan("s1", "u1", completed_days=0)


@pytest.mark.anyio
async def test_quiz_grading_and_weak_topic_update_in_session() -> None:
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = await svc.get_or_create_session(
        session_id="s_quiz", user_id="u1", student_profile=profile
    )

    quiz = create_sample_quiz()
    session.stored_quizzes["quiz_1"] = quiz
    session.current_quiz_id = "quiz_1"
    await svc.save_session(session)

    # Student answers q1 correctly (A), q2 incorrectly (B), q3 incorrectly (B)
    # genai_concepts: 1/1 = 100% (strong)
    # llm_architecture: 0/2 = 0% (weak)
    sub = QuizSubmission(
        quiz_id="quiz_1",
        student_answers={"q1": "A", "q2": "B", "q3": "B"},
    )
    result = await workflow.submit_quiz_answers("s_quiz", "u1", sub)

    assert result.total_questions == 3
    assert result.correct_answers == 1
    assert result.score_percentage == 33.3
    assert "llm_architecture" in result.weak_topics
    assert "genai_concepts" in result.strong_topics

    # Check updated session state
    updated_session = await svc.get_session("s_quiz", "u1")
    assert updated_session is not None
    assert updated_session.weak_topics == ["llm_architecture"]
    assert updated_session.strong_topics == ["genai_concepts"]
    assert updated_session.learning_progress.total_quizzes_taken == 1
    assert updated_session.learning_progress.total_questions_attempted == 3
    assert updated_session.learning_progress.total_questions_correct == 1
    assert updated_session.learning_progress.overall_score_percentage == 33.3


@pytest.mark.anyio
async def test_retrieve_learning_progress() -> None:
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = await svc.get_or_create_session(
        session_id="s_prog", user_id="u1", student_profile=profile
    )

    quiz = create_sample_quiz()
    session.stored_quizzes["quiz_1"] = quiz
    session.current_quiz_id = "quiz_1"
    await svc.save_session(session)

    # 100% score
    sub = QuizSubmission(
        quiz_id="quiz_1",
        student_answers={"q1": "A", "q2": "A", "q3": "A"},
    )
    await workflow.submit_quiz_answers("s_prog", "u1", sub)

    progress = await workflow.retrieve_learning_progress("s_prog", "u1")
    assert progress.total_quizzes_taken == 1
    assert progress.total_questions_attempted == 3
    assert progress.total_questions_correct == 3
    assert progress.overall_score_percentage == 100.0
    assert "genai_concepts" in progress.topics_covered
    assert "llm_architecture" in progress.topics_covered
