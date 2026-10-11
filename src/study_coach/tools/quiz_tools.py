from typing import Any

from study_coach.models.quiz import (
    QuestionFeedback,
    Quiz,
    QuizResult,
    QuizSubmission,
)

# Topics with accuracy below this percentage threshold are classified as weak topics
WEAK_TOPIC_THRESHOLD_PERCENT = 70.0


def validate_quiz(quiz_data: dict[str, Any] | Quiz) -> Quiz:
    """Validates that a quiz dictionary conforms to Pydantic Quiz schema."""
    if isinstance(quiz_data, Quiz):
        return quiz_data
    return Quiz.model_validate(quiz_data)


def calculate_score(
    correct_count: int,
    total_count: int,
) -> float:
    """Calculates the percentage score rounded to one decimal place."""
    if total_count <= 0:
        return 0.0
    return round((correct_count / total_count) * 100.0, 1)


def identify_weak_topics(
    topic_scores: dict[str, dict[str, int]],
    threshold_percent: float = WEAK_TOPIC_THRESHOLD_PERCENT,
) -> tuple[list[str], list[str]]:
    """Identifies weak and strong topics based on student performance.

    topic_scores maps topic_id to {'correct': int, 'total': int}.
    Returns a tuple of (weak_topics, strong_topics).
    """
    weak_topics: list[str] = []
    strong_topics: list[str] = []

    for topic_id, stats in topic_scores.items():
        correct = stats.get("correct", 0)
        total = stats.get("total", 0)
        if total > 0:
            pct = (correct / total) * 100.0
            if pct < threshold_percent:
                weak_topics.append(topic_id)
            else:
                strong_topics.append(topic_id)

    return sorted(weak_topics), sorted(strong_topics)


def grade_quiz(
    quiz: Quiz | dict[str, Any],
    submission: QuizSubmission | dict[str, Any],
) -> QuizResult:
    """Deterministically grades a student quiz submission against the quiz answer key.

    - Missing answers count as incorrect.
    - Invalid question IDs in submission are ignored or flagged.
    - Zero network or LLM calls are used.
    """
    validated_quiz = validate_quiz(quiz)
    if isinstance(submission, dict):
        validated_submission = QuizSubmission.model_validate(submission)
    else:
        validated_submission = submission

    submitted_answers = validated_submission.student_answers

    feedback_list: list[QuestionFeedback] = []
    topic_stats: dict[str, dict[str, int]] = {}
    correct_count = 0

    for q in validated_quiz.questions:
        q_id = q.question_id
        student_choice = submitted_answers.get(q_id)
        is_correct = bool(student_choice and student_choice == q.correct_answer)

        if is_correct:
            correct_count += 1

        # Track topic stats
        if q.topic_id not in topic_stats:
            topic_stats[q.topic_id] = {"correct": 0, "total": 0}
        topic_stats[q.topic_id]["total"] += 1
        if is_correct:
            topic_stats[q.topic_id]["correct"] += 1

        feedback_list.append(
            QuestionFeedback(
                question_id=q_id,
                topic_id=q.topic_id,
                student_answer=student_choice,
                correct_answer=q.correct_answer,
                is_correct=is_correct,
                explanation=q.explanation,
            )
        )

    total_questions = len(validated_quiz.questions)
    score_percentage = calculate_score(correct_count, total_questions)
    weak_topics, strong_topics = identify_weak_topics(topic_stats)

    return QuizResult(
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        question_feedback=feedback_list,
        weak_topics=weak_topics,
        strong_topics=strong_topics,
    )


def generate_feedback_summary(result: QuizResult) -> str:
    """Generates a structured human-readable text summary of quiz performance."""
    lines = [
        f"Quiz Results: {result.correct_answers}/{result.total_questions} Correct ({result.score_percentage:.1f}%)",
    ]
    if result.score_percentage >= 80.0:
        lines.append("Performance: Outstanding mastery!")
    elif result.score_percentage >= WEAK_TOPIC_THRESHOLD_PERCENT:
        lines.append("Performance: Solid understanding; minor review recommended.")
    else:
        lines.append("Performance: Needs focused study on foundational areas.")

    if result.weak_topics:
        lines.append(f"Recommended Topics to Review: {', '.join(result.weak_topics)}")
    if result.strong_topics:
        lines.append(f"Mastered Topics: {', '.join(result.strong_topics)}")

    return "\n".join(lines)
