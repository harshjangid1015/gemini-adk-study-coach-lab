from study_coach.models.quiz import Quiz
from study_coach.tools.quiz_tools import (
    calculate_score,
    generate_feedback_summary,
    grade_quiz,
    identify_weak_topics,
)


def make_sample_quiz() -> Quiz:
    return Quiz.model_validate(
        {
            "certification_name": "Google Cloud Generative AI Leader",
            "topic_ids": ["genai_concepts", "llm_architecture"],
            "experience_level": "intermediate",
            "questions": [
                {
                    "question_id": "q1",
                    "topic_id": "genai_concepts",
                    "question_text": "Question 1 text on genai concepts.",
                    "options": {"A": "Opt A", "B": "Opt B", "C": "Opt C", "D": "Opt D"},
                    "correct_answer": "A",
                    "explanation": "Valid explanation for Question 1.",
                    "difficulty": "intermediate",
                },
                {
                    "question_id": "q2",
                    "topic_id": "genai_concepts",
                    "question_text": "Question 2 text on genai concepts.",
                    "options": {"A": "Opt A", "B": "Opt B", "C": "Opt C", "D": "Opt D"},
                    "correct_answer": "B",
                    "explanation": "Valid explanation for Question 2.",
                    "difficulty": "intermediate",
                },
                {
                    "question_id": "q3",
                    "topic_id": "llm_architecture",
                    "question_text": "Question 3 text on llm architecture.",
                    "options": {"A": "Opt A", "B": "Opt B", "C": "Opt C", "D": "Opt D"},
                    "correct_answer": "C",
                    "explanation": "Valid explanation for Question 3.",
                    "difficulty": "intermediate",
                },
                {
                    "question_id": "q4",
                    "topic_id": "llm_architecture",
                    "question_text": "Question 4 text on llm architecture.",
                    "options": {"A": "Opt A", "B": "Opt B", "C": "Opt C", "D": "Opt D"},
                    "correct_answer": "D",
                    "explanation": "Valid explanation for Question 4.",
                    "difficulty": "intermediate",
                },
                {
                    "question_id": "q5",
                    "topic_id": "llm_architecture",
                    "question_text": "Question 5 text on llm architecture.",
                    "options": {"A": "Opt A", "B": "Opt B", "C": "Opt C", "D": "Opt D"},
                    "correct_answer": "A",
                    "explanation": "Valid explanation for Question 5.",
                    "difficulty": "intermediate",
                },
            ],
        }
    )


def test_calculate_score() -> None:
    assert calculate_score(5, 5) == 100.0
    assert calculate_score(3, 5) == 60.0
    assert calculate_score(0, 5) == 0.0
    assert calculate_score(0, 0) == 0.0


def test_grade_quiz_perfect_score() -> None:
    quiz = make_sample_quiz()
    submission = {
        "student_answers": {"q1": "A", "q2": "B", "q3": "C", "q4": "D", "q5": "A"}
    }
    result = grade_quiz(quiz, submission)
    assert result.total_questions == 5
    assert result.correct_answers == 5
    assert result.score_percentage == 100.0
    assert len(result.weak_topics) == 0
    assert "genai_concepts" in result.strong_topics
    assert "llm_architecture" in result.strong_topics


def test_grade_quiz_partial_score_and_weak_topics() -> None:
    quiz = make_sample_quiz()
    # Student misses both genai_concepts questions (0/2 = 0%), gets all llm_architecture right (3/3 = 100%)
    submission = {
        "student_answers": {"q1": "B", "q2": "C", "q3": "C", "q4": "D", "q5": "A"}
    }
    result = grade_quiz(quiz, submission)
    assert result.total_questions == 5
    assert result.correct_answers == 3
    assert result.score_percentage == 60.0
    assert result.weak_topics == ["genai_concepts"]
    assert result.strong_topics == ["llm_architecture"]


def test_grade_quiz_zero_score_and_missing_answers() -> None:
    quiz = make_sample_quiz()
    # Missing q2, q3, q4, q5; wrong q1
    submission = {"student_answers": {"q1": "D"}}
    result = grade_quiz(quiz, submission)
    assert result.total_questions == 5
    assert result.correct_answers == 0
    assert result.score_percentage == 0.0
    assert "genai_concepts" in result.weak_topics
    assert "llm_architecture" in result.weak_topics


def test_grade_quiz_extra_invalid_question_ids_ignored() -> None:
    quiz = make_sample_quiz()
    submission = {"student_answers": {"q1": "A", "invalid_q99": "A"}}
    result = grade_quiz(quiz, submission)
    # Only q1 is counted as correct, others missing
    assert result.correct_answers == 1
    assert result.total_questions == 5


def test_identify_weak_topics_logic() -> None:
    scores = {
        "topic_a": {"correct": 1, "total": 2},  # 50% -> weak (<70%)
        "topic_b": {"correct": 3, "total": 3},  # 100% -> strong
        "topic_c": {"correct": 7, "total": 10},  # 70% -> strong (>=70%)
    }
    weak, strong = identify_weak_topics(scores)
    assert weak == ["topic_a"]
    assert strong == ["topic_b", "topic_c"]


def test_generate_feedback_summary() -> None:
    quiz = make_sample_quiz()
    submission = {
        "student_answers": {"q1": "A", "q2": "B", "q3": "C", "q4": "D", "q5": "A"}
    }
    result = grade_quiz(quiz, submission)
    summary = generate_feedback_summary(result)
    assert "5/5 Correct (100.0%)" in summary
    assert "Outstanding mastery" in summary
    assert "Mastered Topics" in summary
