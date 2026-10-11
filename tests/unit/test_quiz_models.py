from typing import Any

import pytest
from pydantic import ValidationError

from study_coach.models.quiz import (
    Quiz,
    QuizQuestion,
    QuizSubmission,
)


def sample_valid_question() -> dict[str, Any]:
    return {
        "question_id": "q1",
        "topic_id": "genai_concepts",
        "question_text": "How does Generative AI differ fundamentally from traditional predictive Machine Learning?",
        "options": {
            "A": "Generative AI creates new original content, while predictive ML predicts labels or values.",
            "B": "Generative AI can only process structured tabular datasets.",
            "C": "Generative AI does not require model training or data.",
            "D": "Traditional predictive ML produces human-like essays directly.",
        },
        "correct_answer": "A",
        "explanation": "Generative AI specializes in creating novel data artifacts, whereas traditional ML primarily maps inputs to discrete classes or continuous scores.",
        "difficulty": "beginner",
    }


def test_valid_quiz_question() -> None:
    q_data = sample_valid_question()
    q = QuizQuestion.model_validate(q_data)
    assert q.question_id == "q1"
    assert q.correct_answer == "A"
    assert len(q.options) == 4


def test_invalid_option_count() -> None:
    q_data = sample_valid_question()
    # Missing option D
    q_data["options"] = {
        "A": "Opt A",
        "B": "Opt B",
        "C": "Opt C",
    }
    with pytest.raises(ValidationError, match="must contain exactly keys A, B, C, D"):
        QuizQuestion.model_validate(q_data)


def test_invalid_correct_answer() -> None:
    q_data = sample_valid_question()
    q_data["correct_answer"] = "E"  # Not among A, B, C, D
    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(q_data)


def test_duplicate_options_rejected() -> None:
    q_data = sample_valid_question()
    q_data["options"]["B"] = q_data["options"]["A"]  # duplicate
    with pytest.raises(ValidationError, match="All four options must be distinct"):
        QuizQuestion.model_validate(q_data)


def test_invalid_curriculum_topic_rejected() -> None:
    q_data = sample_valid_question()
    q_data["topic_id"] = "non_existent_curriculum_topic_123"
    with pytest.raises(ValidationError, match="Unknown topic_id"):
        QuizQuestion.model_validate(q_data)


def test_valid_quiz_and_student_view() -> None:
    q1 = sample_valid_question()
    q2 = sample_valid_question()
    q2["question_id"] = "q2"
    q2["topic_id"] = "llm_architecture"

    quiz_data = {
        "certification_name": "Google Cloud Generative AI Leader",
        "topic_ids": ["genai_concepts", "llm_architecture"],
        "experience_level": "beginner",
        "questions": [q1, q2],
    }
    quiz = Quiz.model_validate(quiz_data)
    assert len(quiz.questions) == 2

    # Student view must omit correct_answer and explanation
    student_view = quiz.to_student_view()
    assert len(student_view) == 2
    assert not hasattr(student_view[0], "correct_answer")
    assert not hasattr(student_view[0], "explanation")
    assert student_view[0].question_id == "q1"
    assert len(student_view[0].options) == 4


def test_empty_quiz_rejected() -> None:
    quiz_data = {
        "certification_name": "Google Cloud Generative AI Leader",
        "topic_ids": ["genai_concepts"],
        "experience_level": "beginner",
        "questions": [],
    }
    with pytest.raises(ValidationError):
        Quiz.model_validate(quiz_data)


def test_duplicate_question_ids_rejected() -> None:
    q1 = sample_valid_question()
    q2 = sample_valid_question()
    # Both have question_id 'q1'
    quiz_data = {
        "certification_name": "Google Cloud Generative AI Leader",
        "topic_ids": ["genai_concepts"],
        "experience_level": "beginner",
        "questions": [q1, q2],
    }
    with pytest.raises(ValidationError, match="Quiz question IDs must be unique"):
        Quiz.model_validate(quiz_data)


def test_quiz_submission_model() -> None:
    sub = QuizSubmission(
        quiz_id="quiz_01",
        student_answers={"q1": "A", "q2": "B"},
    )
    assert sub.student_answers["q1"] == "A"
