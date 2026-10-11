"""Unit tests for M6-G Interactive Formative Quick Checks, Navigation, and Sharing."""

from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

from study_coach.models.quiz import (
    Quiz,
    QuizQuestion,
    QuizSubmission,
    StudentQuizQuestion,
)
from study_coach.models.student import StudentProfile
from study_coach.models.topic_explanation import TopicExplanation
from study_coach.services.learning_session import LearningSessionService
from study_coach.services.workshop_facade import WorkshopFacade
from study_coach.workflows.adaptive_study import AdaptiveStudyWorkflow


def create_3_question_quick_check(
    topic_id: str = "llm_architecture", difficulty: str = "intermediate"
) -> Quiz:
    """Helper to create a validated 3-question formative quick check."""
    return Quiz(
        certification_name="Google Cloud Generative AI Leader",
        topic_ids=[topic_id],
        experience_level=difficulty,  # type: ignore[arg-type]
        questions=[
            QuizQuestion(
                question_id="qc1",
                topic_id=topic_id,
                question_text=f"First formative check question for {topic_id}?",
                options={
                    "A": "Option Alpha (Correct)",
                    "B": "Option Beta (Incorrect)",
                    "C": "Option Gamma (Incorrect)",
                    "D": "Option Delta (Incorrect)",
                },
                correct_answer="A",
                explanation="Detailed explanation justifying Alpha as the correct choice.",
                difficulty=difficulty,  # type: ignore[arg-type]
            ),
            QuizQuestion(
                question_id="qc2",
                topic_id=topic_id,
                question_text=f"Second formative check question for {topic_id}?",
                options={
                    "A": "Distractor A",
                    "B": "Option Beta (Correct)",
                    "C": "Distractor C",
                    "D": "Distractor D",
                },
                correct_answer="B",
                explanation="Detailed explanation justifying Beta as the correct choice.",
                difficulty=difficulty,  # type: ignore[arg-type]
            ),
            QuizQuestion(
                question_id="qc3",
                topic_id=topic_id,
                question_text=f"Third formative check question for {topic_id}?",
                options={
                    "A": "Distractor A",
                    "B": "Distractor B",
                    "C": "Option Gamma (Correct)",
                    "D": "Distractor D",
                },
                correct_answer="C",
                explanation="Detailed explanation justifying Gamma as the correct choice.",
                difficulty=difficulty,  # type: ignore[arg-type]
            ),
        ],
    )


# ==============================================================================
# SECTION A: QUICK CHECK MODEL & WORKFLOW ARCHITECTURE
# ==============================================================================


@pytest.mark.anyio
async def test_quick_check_model_and_student_sanitization() -> None:
    """Verify that quick check questions contain exactly 3 items and answer keys are stripped."""
    quiz = create_3_question_quick_check("llm_architecture", "intermediate")
    assert len(quiz.questions) == 3

    for q in quiz.questions:
        assert len(q.options) == 4
        assert set(q.options.keys()) == {"A", "B", "C", "D"}
        assert q.topic_id == "llm_architecture"
        assert q.difficulty == "intermediate"
        assert q.correct_answer in q.options
        assert len(q.explanation) >= 10

    # Test conversion to student view
    student_view = quiz.to_student_view()
    assert len(student_view) == 3
    for sq in student_view:
        assert isinstance(sq, StudentQuizQuestion)
        assert not hasattr(sq, "correct_answer")
        assert not hasattr(sq, "explanation")
        assert len(sq.options) == 4
        assert sq.topic_id == "llm_architecture"


@pytest.mark.anyio
async def test_quick_check_difficulty_levels() -> None:
    """Verify beginner, intermediate, and advanced quick checks validate properly."""
    for level in ["beginner", "intermediate", "advanced"]:
        quiz = create_3_question_quick_check("vertex_ai_studio", level)
        assert quiz.experience_level == level
        for q in quiz.questions:
            assert q.difficulty == level


# ==============================================================================
# SECTION B: DETERMINISTIC SCORING & FORMATION ISOLATION
# ==============================================================================


@pytest.mark.anyio
@pytest.mark.parametrize(
    "answers, expected_correct, expected_score",
    [
        ({"qc1": "A", "qc2": "B", "qc3": "C"}, 3, 100.0),
        ({"qc1": "A", "qc2": "B", "qc3": "D"}, 2, 66.7),
        ({"qc1": "A", "qc2": "D", "qc3": "D"}, 1, 33.3),
        ({"qc1": "D", "qc2": "D", "qc3": "D"}, 0, 0.0),
        ({"qc1": "A"}, 1, 33.3),  # Unanswered qc2, qc3 count as incorrect
        ({}, 0, 0.0),  # Completely unanswered
    ],
)
async def test_deterministic_scoring_percentages(
    answers: dict[str, Any], expected_correct: int, expected_score: float
) -> None:
    """Verify deterministic Python scoring: 3/3=100%, 2/3=66.7%, 1/3=33.3%, 0/3=0% and unanswered handling."""
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    profile = StudentProfile(experience_level="intermediate", daily_study_minutes=90)
    sess = await svc.get_or_create_session("qc_sess", "qc_user", profile)

    quiz = create_3_question_quick_check("llm_architecture", "intermediate")
    qc_id = "quick_check_llm_architecture_1"
    sess.stored_quizzes[qc_id] = quiz
    await svc.save_session(sess)

    submission = QuizSubmission(quiz_id=qc_id, student_answers=answers)
    result = await workflow.evaluate_quick_check("qc_sess", "qc_user", submission)

    assert result.total_questions == 3
    assert result.correct_answers == expected_correct
    assert result.score_percentage == expected_score

    # Check question feedback details
    assert len(result.question_feedback) == 3
    for fb in result.question_feedback:
        assert fb.explanation is not None
        assert fb.correct_answer in ["A", "B", "C"]
        if fb.student_answer == fb.correct_answer:
            assert fb.is_correct is True
        else:
            assert fb.is_correct is False


@pytest.mark.anyio
async def test_quick_check_formative_isolation_from_formal_quiz() -> None:
    """Verify formative quick check does NOT mutate formal quiz results, weak topics, or progress."""
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)
    facade = WorkshopFacade(session_service=svc, workflow=workflow)

    profile = StudentProfile(experience_level="intermediate", daily_study_minutes=90)
    sess = await facade.get_or_create_session("iso_sess", "iso_user", profile)
    sess.weak_topics = ["genai_concepts"]
    await svc.save_session(sess)

    # Inject quick check into private storage
    quiz = create_3_question_quick_check("llm_architecture", "intermediate")
    qc_id = "quick_check_llm_architecture_1"
    sess.stored_quizzes[qc_id] = quiz
    await svc.save_session(sess)

    # Student scores 0% on quick check
    submission = QuizSubmission(quiz_id=qc_id, student_answers={"qc1": "D"})
    result = await facade.evaluate_quick_check("iso_sess", "iso_user", submission)
    assert result.correct_answers == 0
    assert result.score_percentage == 0.0

    # Verify session state remains intact
    refreshed_sess = await svc.get_session("iso_sess", "iso_user")
    assert refreshed_sess is not None
    # Formal quiz results list should be completely empty
    assert len(refreshed_sess.quiz_results) == 0
    # Weak topics list should NOT have added llm_architecture
    assert refreshed_sess.weak_topics == ["genai_concepts"]
    # Formal quiz progress counters must remain 0
    assert refreshed_sess.learning_progress.total_quizzes_taken == 0
    assert refreshed_sess.learning_progress.total_questions_attempted == 0
    assert refreshed_sess.current_quiz_id is None


# ==============================================================================
# SECTION C: STREAMLIT APPTEST UI VERIFICATION
# ==============================================================================


def test_ui_quick_check_and_share_rendering() -> None:
    """Verify Learn Topic Practice & Share subtab renders quick check controls and share section."""
    app_path = Path(__file__).resolve().parent.parent.parent / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()

    # Populate explained_topic in session state
    sample_explanation = TopicExplanation(
        topic_id="llm_architecture",
        topic_title="LLM Architecture & Transformers",
        experience_level="intermediate",
        learning_objectives=["Understand self-attention"],
        key_concepts=["Self-Attention", "Embeddings"],
        explanation="Transformers process entire sequences concurrently.",
        practical_example="Deploying Gemini on Vertex AI.",
        common_misconceptions=["Transformers process words one-by-one linearly."],
        comprehension_questions=["Explain self-attention."],
        source_references=[
            "https://cloud.google.com/learn/certification/generative-ai-leader"
        ],
    )
    at.session_state["explained_topic"] = sample_explanation
    at.run()
    assert not at.exception

    markdown_texts = [m.value for m in at.markdown]

    # Verify Quick Check section exists
    has_qc = any("Quick Knowledge Check" in text for text in markdown_texts)
    assert has_qc

    # Verify Share My Learning section exists
    has_share = any("Share My Learning" in text for text in markdown_texts)
    assert has_share

    # Verify LinkedIn share copy and prefill notice
    text_areas = [ta.value for ta in at.text_area]
    assert any(val and "I'm learning about" in val for val in text_areas)
    assert any(val and "Google Cloud Generative AI Leader" in val for val in text_areas)
    assert any(val and "#GeminiADK" in val for val in text_areas)

    # Verify sharing instructions state modern LinkedIn manual copy/paste
    info_texts = [i.value for i in at.info]
    assert any("Modern LinkedIn sharing URLs" in text for text in info_texts)


def test_ui_quick_check_interactive_submission_and_feedback() -> None:
    """Verify answering 3 quick check questions renders deterministic scoring banner and feedback."""
    app_path = Path(__file__).resolve().parent.parent.parent / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()

    # Populate session and explanation
    facade = at.session_state["facade"]
    import asyncio

    profile = StudentProfile(experience_level="intermediate", daily_study_minutes=90)
    session = asyncio.run(
        facade.get_or_create_session(
            at.session_state["session_id"],
            at.session_state["user_id"],
            profile,
        )
    )

    # Inject mock quick check
    sample_qc = create_3_question_quick_check("llm_architecture", "intermediate")
    qc_id = "quick_check_llm_architecture_test"
    session.stored_quizzes[qc_id] = sample_qc
    asyncio.run(facade.session_service.save_session(session))

    sample_explanation = TopicExplanation(
        topic_id="llm_architecture",
        topic_title="LLM Architecture & Transformers",
        experience_level="intermediate",
        learning_objectives=["Understand self-attention"],
        key_concepts=["Self-Attention"],
        explanation="Transformers process sequences concurrently.",
        practical_example="Gemini on Vertex AI.",
        common_misconceptions=["Linear sequential processing."],
        comprehension_questions=["What is attention?"],
        source_references=["https://cloud.google.com"],
    )
    at.session_state["explained_topic"] = sample_explanation
    at.session_state["quick_check_quiz_id"] = qc_id
    at.session_state["quick_check_questions"] = sample_qc.to_student_view()
    at.session_state["quick_check_selections"] = {"qc1": "A", "qc2": "B", "qc3": "D"}
    at.run()
    assert not at.exception

    # Find the submit button
    submit_btn = None
    for b in at.button:
        if "Submit / Check Answers" in b.label:
            submit_btn = b
            break
    assert submit_btn is not None
    submit_btn.click()
    at.run()
    assert not at.exception

    # Verify score banner: 2/3 = 66.7%
    success_or_warning = [s.value for s in at.warning] + [s.value for s in at.success]
    has_score_banner = any("Quick Check Score: 66.7%" in s for s in success_or_warning)
    assert has_score_banner

    # Verify explanations rendered for correct and incorrect answers
    has_correct_feedback = any("Correct!" in s for s in success_or_warning)
    assert has_correct_feedback
    has_incorrect_feedback = any("Incorrect" in e.value for e in at.error)
    assert has_incorrect_feedback

    # Verify Retry button is present
    has_retry_btn = any("Retry Quick Check" in b.label for b in at.button)
    assert has_retry_btn


def test_ui_navigation_preselects_topic_and_switches_tab() -> None:
    """Verify clicking Start Practice Quiz directly preselects topic and sets active tab to Practice Quiz."""
    app_path = Path(__file__).resolve().parent.parent.parent / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()

    # Prepopulate explanation
    sample_explanation = TopicExplanation(
        topic_id="llm_architecture",
        topic_title="LLM Architecture & Transformers",
        experience_level="intermediate",
        learning_objectives=["Self-attention"],
        key_concepts=["Attention"],
        explanation="Transformer models.",
        practical_example="Gemini Vertex AI.",
        common_misconceptions=["RNN superiority."],
        comprehension_questions=["Attention?"],
        source_references=["https://cloud.google.com"],
    )
    at.session_state["explained_topic"] = sample_explanation
    at.run()
    assert not at.exception

    # Find Start Practice Quiz button
    nav_btn = None
    for b in at.button:
        if "Start Practice Quiz" in b.label:
            nav_btn = b
            break
    assert nav_btn is not None
    nav_btn.click()
    at.run()
    assert not at.exception

    # Verify session state updated tab and topic
    assert at.session_state["main_nav_tab"] == "📝 Practice Quiz"
    assert at.session_state["preselected_quiz_topic"] == "llm_architecture"
    assert "llm_architecture" in at.session_state["quiz_topic_select"]
