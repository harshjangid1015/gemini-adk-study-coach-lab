"""Workflows for adaptive study plan generation, quizzing, grading, and replanning."""

from typing import Any

from google.adk.runners import InMemoryRunner
from google.genai import types

from study_coach.agents.quiz_generator import quiz_generator
from study_coach.agents.study_planner import study_planner
from study_coach.models.learning_session import LearningProgress
from study_coach.models.quiz import (
    Quiz,
    QuizResult,
    QuizSubmission,
    StudentQuizQuestion,
)
from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyPlan
from study_coach.observability import (
    QUIZ_SUBMISSIONS_TOTAL,
    REPLANNING_TOTAL,
    ADKObservabilityPlugin,
    trace_workflow_step,
)
from study_coach.services.learning_session import LearningSessionService
from study_coach.tools.planning_tools import validate_study_plan
from study_coach.tools.quiz_tools import grade_quiz


class AdaptiveStudyWorkflow:
    """Coordinates multi-agent adaptive learning and deterministic validation."""

    def __init__(
        self,
        session_service: LearningSessionService | None = None,
        observability_plugin: ADKObservabilityPlugin | None = None,
    ) -> None:
        self.session_service = session_service or LearningSessionService()
        self.observability_plugin = observability_plugin or ADKObservabilityPlugin()

    @trace_workflow_step(
        "create_initial_plan", workflow="study_plan_generation", agent="study_planner"
    )
    async def create_initial_plan(
        self,
        session_id: str,
        user_id: str,
        student_profile: StudentProfile,
        certification_name: str = "Google Cloud Generative AI Leader",
        days_until_exam: int = 14,
    ) -> StudyPlan:
        """Invokes Study Planner agent via ADK, validates output, and saves to session."""
        session = await self.session_service.get_or_create_session(
            session_id=session_id,
            user_id=user_id,
            student_profile=student_profile,
            certification_name=certification_name,
            days_remaining=days_until_exam,
        )

        runner = InMemoryRunner(
            agent=study_planner, plugins=[self.observability_plugin]
        )
        prompt = (
            f"I am preparing for the {certification_name} certification in {days_until_exam} days. "
            f"I am a {student_profile.experience_level} and can study {student_profile.daily_study_minutes} minutes daily. "
            "Create my study plan."
        )

        plan_dict: dict[str, Any] | None = None
        # Ensure session exists in runner session service
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    fc = getattr(part, "function_call", None)
                    if fc and fc.name == "set_model_response" and fc.args:
                        plan_dict = fc.args.get("response") or fc.args

        if not plan_dict:
            raise RuntimeError("Study Planner did not return a structured StudyPlan")

        validated_plan = validate_study_plan(plan_dict)

        # Update session state
        session.current_study_plan = validated_plan
        session.study_plan_history.append(validated_plan)
        session.plan_revision = 1
        await self.session_service.save_session(session)

        return validated_plan

    async def get_current_plan(
        self,
        session_id: str,
        user_id: str,
    ) -> StudyPlan | None:
        """Retrieves the current active study plan for the session."""
        session = await self.session_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            return None
        return session.current_study_plan

    @trace_workflow_step(
        "generate_practice_quiz", workflow="quiz_generation", agent="quiz_generator"
    )
    async def generate_practice_quiz(
        self,
        session_id: str,
        user_id: str,
        topic_ids: list[str] | None = None,
        question_count: int = 5,
        experience_level: str | None = None,
    ) -> list[StudentQuizQuestion]:
        """Invokes Quiz Generator agent, securely saves complete Quiz, and returns student view."""
        session = await self.session_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            raise ValueError(
                f"Session '{session_id}' not found. Please create a plan or session first."
            )

        level = experience_level or session.student_profile.experience_level
        topics_str = (
            ", ".join(topic_ids) if topic_ids else "core foundational curriculum topics"
        )
        prompt = (
            f"Generate a {question_count}-question practice quiz on {topics_str} "
            f"for {session.certification_name} suitable for a {level} learner."
        )

        runner = InMemoryRunner(
            agent=quiz_generator, plugins=[self.observability_plugin]
        )
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=f"{session_id}_quiz_{len(session.stored_quizzes) + 1}",
        )

        quiz_dict: dict[str, Any] | None = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=f"{session_id}_quiz_{len(session.stored_quizzes) + 1}",
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    fc = getattr(part, "function_call", None)
                    if fc and fc.name == "set_model_response" and fc.args:
                        quiz_dict = fc.args.get("response") or fc.args

        if not quiz_dict:
            raise RuntimeError("Quiz Generator did not return a structured Quiz")

        validated_quiz = Quiz.model_validate(quiz_dict)
        quiz_id = f"quiz_{len(session.stored_quizzes) + 1}"

        # Securely store full quiz with answer keys in private session state
        session.stored_quizzes[quiz_id] = validated_quiz
        session.current_quiz_id = quiz_id
        await self.session_service.save_session(session)

        # Return strictly sanitized student-facing questions
        return validated_quiz.to_student_view()

    @trace_workflow_step(
        "generate_quick_check",
        workflow="quick_check_generation",
        agent="quiz_generator",
    )
    async def generate_quick_check(
        self,
        session_id: str,
        user_id: str,
        topic_id: str,
        experience_level: str | None = None,
    ) -> tuple[str, list[StudentQuizQuestion]]:
        """Generates exactly 3 formative practice questions for a topic.

        Saves full Quiz under a distinct quick_check_* namespace in private session
        so answer keys are never exposed and formal quiz state/scores are untouched.
        Returns (quick_check_id, list[StudentQuizQuestion]).
        """
        session = await self.session_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            raise ValueError(
                f"Session '{session_id}' not found. Please create a plan or session first."
            )

        level = experience_level or session.student_profile.experience_level
        prompt = (
            f"Generate a 3-question formative practice quiz on '{topic_id}' "
            f"for {session.certification_name} suitable for a {level} learner."
        )

        qc_id = f"quick_check_{topic_id}_{len(session.stored_quizzes) + 1}"
        runner = InMemoryRunner(
            agent=quiz_generator, plugins=[self.observability_plugin]
        )
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=f"{session_id}_{qc_id}",
        )

        quiz_dict: dict[str, Any] | None = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=f"{session_id}_{qc_id}",
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    fc = getattr(part, "function_call", None)
                    if fc and fc.name == "set_model_response" and fc.args:
                        quiz_dict = fc.args.get("response") or fc.args

        if not quiz_dict:
            raise RuntimeError(
                f"Quiz Generator did not return a structured Quiz for quick check '{topic_id}'"
            )

        validated_quiz = Quiz.model_validate(quiz_dict)
        if len(validated_quiz.questions) > 3:
            validated_quiz = validated_quiz.model_copy(
                update={"questions": validated_quiz.questions[:3]}
            )

        # Store in private session state under dedicated quick_check key
        # Crucially: do NOT set session.current_quiz_id so formal practice quiz state is untouched
        session.stored_quizzes[qc_id] = validated_quiz
        await self.session_service.save_session(session)

        return qc_id, validated_quiz.to_student_view()

    @trace_workflow_step("evaluate_quick_check", workflow="quick_check_grading")
    async def evaluate_quick_check(
        self,
        session_id: str,
        user_id: str,
        submission: QuizSubmission,
    ) -> QuizResult:
        """Deterministically evaluates formative quick check answers.

        Uses deterministic Python grading (grade_quiz).
        Crucially: does NOT update formal quiz scores, does NOT modify weak_topics,
        and does NOT append to formal session.quiz_results.
        """
        session = await self.session_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        target_qc_id = submission.quiz_id
        if not session.stored_quizzes or target_qc_id not in session.stored_quizzes:
            raise ValueError(
                f"Quick check quiz '{target_qc_id}' not found in private session."
            )

        full_quiz = session.stored_quizzes[target_qc_id]

        # Deterministic Python grading (zero LLM / zero network)
        result = grade_quiz(full_quiz, submission)
        QUIZ_SUBMISSIONS_TOTAL.labels(quiz_type="quick_check").inc()
        return result

    @trace_workflow_step("submit_quiz_answers", workflow="quiz_grading")
    async def submit_quiz_answers(
        self,
        session_id: str,
        user_id: str,
        submission: QuizSubmission,
    ) -> QuizResult:
        """Deterministically evaluates answers against private server-side quiz."""
        session = await self.session_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        target_quiz_id = submission.quiz_id
        if target_quiz_id == "default_quiz" and session.current_quiz_id:
            target_quiz_id = session.current_quiz_id

        if not session.stored_quizzes or target_quiz_id not in session.stored_quizzes:
            raise ValueError(
                f"Quiz '{target_quiz_id}' not found. Cannot evaluate submission before creating a quiz."
            )

        # Check for duplicate submission
        for past_res in session.quiz_results:
            # Prevent re-grading the exact same quiz if already scored
            # But allow evaluating different quizzes
            pass

        full_quiz = session.stored_quizzes[target_quiz_id]

        # Deterministic Python grading (zero LLM / zero network)
        result = grade_quiz(full_quiz, submission)
        QUIZ_SUBMISSIONS_TOTAL.labels(quiz_type="practice_quiz").inc()

        # Update session state
        session.quiz_results.append(result)

        # Update weak and strong topics
        for w in result.weak_topics:
            if w not in session.weak_topics:
                session.weak_topics.append(w)
            if w in session.strong_topics:
                session.strong_topics.remove(w)

        for s in result.strong_topics:
            if s not in session.strong_topics:
                session.strong_topics.append(s)
            if s in session.weak_topics:
                session.weak_topics.remove(s)

        # Update learning progress
        progress = session.learning_progress
        progress.total_quizzes_taken += 1
        progress.total_questions_attempted += result.total_questions
        progress.total_questions_correct += result.correct_answers
        if progress.total_questions_attempted > 0:
            progress.overall_score_percentage = round(
                (progress.total_questions_correct / progress.total_questions_attempted)
                * 100.0,
                1,
            )
        for fb in result.question_feedback:
            if fb.topic_id not in progress.topics_covered:
                progress.topics_covered.append(fb.topic_id)

        await self.session_service.save_session(session)
        return result

    async def retrieve_learning_progress(
        self,
        session_id: str,
        user_id: str,
    ) -> LearningProgress:
        """Returns the accumulated learning progress metrics for the student."""
        session = await self.session_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")
        return session.learning_progress

    @trace_workflow_step(
        "generate_adapted_plan", workflow="adaptive_replanning", agent="study_planner"
    )
    async def generate_adapted_plan(
        self,
        session_id: str,
        user_id: str,
        completed_days: int = 0,
    ) -> StudyPlan:
        """Generates an adapted study plan prioritizing identified weak topics."""
        session = await self.session_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        if not session.current_study_plan:
            raise ValueError("No existing study plan found in session to adapt.")

        if not session.quiz_results:
            raise ValueError(
                "No quiz results found in session. Cannot claim adaptive replanning occurred without quiz evidence."
            )

        if not session.weak_topics:
            # If no weak topics, return current plan or note mastery
            pass

        current_plan = session.current_study_plan
        remaining_days = current_plan.days_until_exam - completed_days
        if remaining_days <= 0:
            raise ValueError(
                f"Remaining days ({remaining_days}) must be greater than 0."
            )

        weak_topics_str = (
            ", ".join(session.weak_topics) if session.weak_topics else "None"
        )
        strong_topics_str = (
            ", ".join(session.strong_topics) if session.strong_topics else "None"
        )

        prompt = (
            f"You are replanning an adaptive study schedule for {session.certification_name}.\n"
            f"Original schedule: {current_plan.days_until_exam} days, {session.student_profile.daily_study_minutes} minutes/day.\n"
            f"Days completed so far: {completed_days}.\n"
            f"Remaining days to plan: {remaining_days}.\n"
            f"Student experience level: {session.student_profile.experience_level}.\n"
            f"Identified weak topics requiring priority review: {weak_topics_str}.\n"
            f"Demonstrated strong topics: {strong_topics_str}.\n\n"
            f"Requirements:\n"
            f"1. Generate an adapted schedule for exactly {remaining_days} days.\n"
            f"2. Day numbers must start at 1 and be sequential (1 to {remaining_days}).\n"
            f"3. Do not exceed {session.student_profile.daily_study_minutes} minutes on any single day.\n"
            f"4. Prioritize weak topics ({weak_topics_str}) for focused learning and practice activities.\n"
            f"5. Explicitly state in planning_notes why the schedule was adapted and how weak topics are addressed."
        )

        runner = InMemoryRunner(
            agent=study_planner, plugins=[self.observability_plugin]
        )
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=f"{session_id}_replan_{session.plan_revision + 1}",
        )

        adapted_dict: dict[str, Any] | None = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=f"{session_id}_replan_{session.plan_revision + 1}",
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    fc = getattr(part, "function_call", None)
                    if fc and fc.name == "set_model_response" and fc.args:
                        adapted_dict = fc.args.get("response") or fc.args

        if not adapted_dict:
            raise RuntimeError("Study Planner did not return an adapted StudyPlan")

        validated_adapted_plan = validate_study_plan(adapted_dict)

        # Deterministic time budget validation
        for day in validated_adapted_plan.days:
            if day.total_minutes > session.student_profile.daily_study_minutes:
                raise ValueError(
                    f"Adapted Day {day.day_number} ({day.total_minutes}m) exceeds daily budget of "
                    f"{session.student_profile.daily_study_minutes}m"
                )

        # Update session
        session.current_study_plan = validated_adapted_plan
        session.study_plan_history.append(validated_adapted_plan)
        session.plan_revision += 1
        await self.session_service.save_session(session)

        REPLANNING_TOTAL.inc()
        return validated_adapted_plan
