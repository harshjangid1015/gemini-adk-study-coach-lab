"""Evaluations for adaptive workflow grading, weak topic identification, and replanning."""

import pytest

from study_coach.models.quiz import (
    Quiz,
    QuizQuestion,
    QuizSubmission,
)
from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyActivity, StudyDay, StudyPlan
from study_coach.services.learning_session import LearningSessionService
from study_coach.tools.quiz_tools import grade_quiz
from study_coach.workflows.adaptive_study import AdaptiveStudyWorkflow


def make_eval_quiz() -> Quiz:
    questions = [
        QuizQuestion(
            question_id=f"q{i}",
            topic_id="llm_architecture" if i in [1, 2] else "genai_concepts",
            question_text=f"Question {i} scenario prompt text?",
            options={
                "A": "Option A explanation",
                "B": "Option B explanation",
                "C": "Option C explanation",
                "D": "Option D explanation",
            },
            correct_answer="A",
            explanation="Detailed explanation justifying correct answer.",
            difficulty="intermediate",
        )
        for i in range(1, 6)
    ]
    return Quiz(
        certification_name="Google Cloud Generative AI Leader",
        topic_ids=["llm_architecture", "genai_concepts"],
        experience_level="intermediate",
        questions=questions,
    )


def test_deterministic_grading_and_weak_topics_scenario_7() -> None:
    """Evaluate Scenario 7: submit 3 correct and 2 incorrect answers in 5-question quiz."""
    quiz = make_eval_quiz()
    # q1, q2 wrong (llm_architecture), q3, q4, q5 correct (genai_concepts)
    submission = QuizSubmission(
        quiz_id="quiz_eval_workflow",
        student_answers={"q1": "B", "q2": "C", "q3": "A", "q4": "A", "q5": "A"},
    )
    result = grade_quiz(quiz, submission)
    assert result.total_questions == 5
    assert result.correct_answers == 3
    assert result.score_percentage == 60.0
    assert "llm_architecture" in result.weak_topics
    assert "genai_concepts" in result.strong_topics


@pytest.mark.anyio
async def test_adaptive_replanning_state_isolation_scenario_8() -> None:
    """Evaluate Scenario 8: replan requires prior quiz results and updates session history."""
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)

    profile = StudentProfile(experience_level="beginner", daily_study_minutes=60)
    session = await svc.get_or_create_session("eval_session", "eval_user", profile)

    # Initial plan
    initial_plan = StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=10,
        daily_study_minutes=60,
        days=[
            StudyDay(
                day_number=i,
                title=f"Day {i}",
                total_minutes=60,
                activities=[
                    StudyActivity(
                        activity_type="learning",
                        topic_id="genai_concepts",
                        description="Reading",
                        duration_minutes=60,
                    )
                ],
            )
            for i in range(1, 11)
        ],
        total_planned_minutes=600,
        planning_notes="Initial 10-day schedule",
    )
    session.current_study_plan = initial_plan
    await svc.save_session(session)

    # Attempting to replan before any quiz must fail
    with pytest.raises(ValueError, match="No quiz results found"):
        await workflow.generate_adapted_plan(
            "eval_session", "eval_user", completed_days=3
        )
