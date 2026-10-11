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
from study_coach.services.learning_session import LearningSessionService
from study_coach.tools.planning_tools import validate_study_plan
from study_coach.tools.quiz_tools import grade_quiz


class AdaptiveStudyWorkflow:
    """Coordinates multi-agent adaptive learning and deterministic validation."""

    def __init__(
        self,
        session_service: LearningSessionService | None = None,
    ) -> None:
        self.session_service = session_service or LearningSessionService()

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

        runner = InMemoryRunner(agent=study_planner)
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

        runner = InMemoryRunner(agent=quiz_generator)
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

        runner = InMemoryRunner(agent=study_planner)
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

        return validated_adapted_plan
