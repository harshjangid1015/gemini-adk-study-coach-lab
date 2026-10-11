"""Evaluations for Quiz Generator question quality, option formatting, and answer security."""

import pytest
from pydantic import ValidationError

from study_coach.models.quiz import Quiz, QuizQuestion


def test_formative_quiz_contract_scenario_5() -> None:
    """Evaluate Scenario 5: exactly 3 questions for formative Quick Check."""
    questions = [
        QuizQuestion(
            question_id=f"q_{i}",
            topic_id="genai_concepts",
            question_text=f"Question {i} scenario about foundational GenAI components?",
            options={
                "A": "Option A explanation",
                "B": "Option B explanation",
                "C": "Option C explanation",
                "D": "Option D explanation",
            },
            correct_answer="A",
            explanation="Detailed explanation justifying correct answer.",
            difficulty="beginner",
        )
        for i in range(1, 4)
    ]
    quiz = Quiz(
        certification_name="Google Cloud Generative AI Leader",
        topic_ids=["genai_concepts"],
        experience_level="beginner",
        questions=questions,
    )
    assert len(quiz.questions) == 3
    # Check student view excludes answers and explanations
    student_view = quiz.to_student_view()
    assert len(student_view) == 3
    for sq in student_view:
        assert not hasattr(sq, "correct_answer")
        assert not hasattr(sq, "explanation")
        assert len(sq.options) == 4


def test_practice_quiz_contract_scenario_6() -> None:
    """Evaluate Scenario 6: 5 questions for formal practice quiz."""
    questions = [
        QuizQuestion(
            question_id=f"q_{i}",
            topic_id="llm_architecture",
            question_text=f"Practice question scenario {i} for intermediate student?",
            options={
                "A": "Option A explanation",
                "B": "Option B explanation",
                "C": "Option C explanation",
                "D": "Option D explanation",
            },
            correct_answer="B",
            explanation="Detailed explanation justifying correct answer.",
            difficulty="intermediate",
        )
        for i in range(1, 6)
    ]
    quiz = Quiz(
        certification_name="Google Cloud Generative AI Leader",
        topic_ids=["llm_architecture"],
        experience_level="intermediate",
        questions=questions,
    )
    assert len(quiz.questions) == 5
    for q in quiz.questions:
        assert len(q.options) == 4
        keys = list(q.options.keys())
        assert keys == ["A", "B", "C", "D"]
        assert q.correct_answer in keys


def test_quiz_rejects_missing_or_invalid_options() -> None:
    """Evaluation check: invalid options dict must fail validation."""
    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(
            {
                "question_id": "bad_q",
                "topic_id": "genai_concepts",
                "question_text": "Invalid question prompt?",
                "options": {"A": "Option A", "B": "Option B"},
                "correct_answer": "A",
                "explanation": "Needs 4 options",
                "difficulty": "beginner",
            }
        )
