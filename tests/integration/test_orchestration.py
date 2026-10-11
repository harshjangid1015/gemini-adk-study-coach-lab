import pytest

from study_coach.agent import root_agent, study_coach
from study_coach.agents.quiz_generator import quiz_generator
from study_coach.agents.study_planner import study_planner
from study_coach.agents.topic_expert import topic_expert
from study_coach.models.quiz import Quiz, QuizSubmission
from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyActivity, StudyDay, StudyPlan
from study_coach.services.learning_session import LearningSessionService
from study_coach.workflows.adaptive_study import AdaptiveStudyWorkflow


def test_coordinator_has_all_three_specialists() -> None:
    assert root_agent is study_coach
    assert root_agent.name == "study_coach"
    assert study_planner in root_agent.sub_agents
    assert topic_expert in root_agent.sub_agents
    assert quiz_generator in root_agent.sub_agents
    assert len(root_agent.sub_agents) == 3


def test_coordinator_instructions_cover_all_routes() -> None:
    instructions = str(root_agent.instruction)
    assert "study_planner" in instructions
    assert "topic_expert" in instructions
    assert "quiz_generator" in instructions
    assert "Adaptive Replanning" in instructions
    assert "Grading & Evaluation" in instructions


@pytest.mark.anyio
async def test_end_to_end_orchestration_cycle_offline() -> None:
    """Tests the full multi-agent adaptive study cycle using simulated outputs and deterministic validation."""
    svc = LearningSessionService()
    workflow = AdaptiveStudyWorkflow(session_service=svc)

    user_id = "test_student_m5"
    session_id = "sess_m5_e2e"
    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)

    # 1. Initialize session and initial plan
    session = await svc.get_or_create_session(
        session_id=session_id,
        user_id=user_id,
        student_profile=profile,
        certification_name="Google Cloud Generative AI Leader",
        days_remaining=14,
    )
    assert session.plan_revision == 1

    initial_plan = StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=14,
        daily_study_minutes=90,
        days=[
            StudyDay(
                day_number=i,
                title=f"Day {i}",
                activities=[
                    StudyActivity(
                        topic_id="genai_concepts" if i <= 7 else "llm_architecture",
                        activity_type="learning",
                        description=f"Study concepts for Day {i}",
                        duration_minutes=90,
                    )
                ],
                total_minutes=90,
            )
            for i in range(1, 15)
        ],
        total_planned_minutes=14 * 90,
        planning_notes="Initial 14-day balanced curriculum schedule.",
    )
    session.current_study_plan = initial_plan
    session.study_plan_history.append(initial_plan)
    await svc.save_session(session)

    # Verify plan stored
    active_plan = await workflow.get_current_plan(session_id, user_id)
    assert active_plan is not None
    assert active_plan.days_until_exam == 14

    from study_coach.models.quiz import QuizQuestion

    quiz = Quiz(
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
    session.stored_quizzes["quiz_1"] = quiz
    session.current_quiz_id = "quiz_1"
    await svc.save_session(session)

    # 3. Present sanitized quiz to student
    sanitized = session.get_sanitized_quiz("quiz_1")
    assert len(sanitized) == 2
    for sq in sanitized:
        assert not hasattr(sq, "correct_answer")
        assert not hasattr(sq, "explanation")

    # 4. Student submits answers (q1 correct, q2 incorrect)
    # genai_concepts: 1/1 = 100% (strong)
    # llm_architecture: 0/1 = 0% (weak)
    submission = QuizSubmission(
        quiz_id="quiz_1",
        student_answers={"q1": "A", "q2": "B"},
    )
    grade_res = await workflow.submit_quiz_answers(session_id, user_id, submission)
    assert grade_res.total_questions == 2
    assert grade_res.correct_answers == 1
    assert grade_res.score_percentage == 50.0
    assert "llm_architecture" in grade_res.weak_topics
    assert "genai_concepts" in grade_res.strong_topics

    # 5. Check session state has recorded weak and strong topics
    session_after_quiz = await svc.get_session(session_id, user_id)
    assert session_after_quiz is not None
    assert session_after_quiz.weak_topics == ["llm_architecture"]
    assert session_after_quiz.strong_topics == ["genai_concepts"]

    # 6. Simulate adapted study plan (e.g., student completed 3 days, 11 days remaining)
    completed_days = 3
    remaining_days = 14 - completed_days
    adapted_plan = StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=remaining_days,
        daily_study_minutes=90,
        days=[
            StudyDay(
                day_number=i,
                title=f"Adapted Day {i}",
                activities=[
                    StudyActivity(
                        topic_id="llm_architecture",  # Prioritizing weak topic
                        activity_type="review" if i <= 4 else "practice",
                        description=f"Focused deep dive on weak topic for Day {i}",
                        duration_minutes=90,
                    )
                ],
                total_minutes=90,
            )
            for i in range(1, remaining_days + 1)
        ],
        total_planned_minutes=remaining_days * 90,
        planning_notes=(
            f"Adapted schedule for remaining {remaining_days} days. "
            "Prioritized weak topic llm_architecture based on quiz scoring (50.0%)."
        ),
    )

    # Update session with adapted plan
    session_after_quiz.current_study_plan = adapted_plan
    session_after_quiz.study_plan_history.append(adapted_plan)
    session_after_quiz.plan_revision = 2
    await svc.save_session(session_after_quiz)

    # 7. Validate adapted plan and historical preservation
    final_session = await svc.get_session(session_id, user_id)
    assert final_session is not None
    assert final_session.plan_revision == 2
    assert len(final_session.study_plan_history) == 2
    assert final_session.study_plan_history[0].days_until_exam == 14
    assert final_session.study_plan_history[1].days_until_exam == 11
    assert final_session.current_study_plan is not None
    assert final_session.current_study_plan.days_until_exam == 11

    # Time budget checks
    for day in final_session.current_study_plan.days:
        assert day.total_minutes <= 90
