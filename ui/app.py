"""Streamlit Workshop Web Application for Gemini ADK Study Coach."""

import asyncio
import os
import uuid
from typing import Any, Literal, cast

import streamlit as st
from dotenv import load_dotenv

from study_coach.models.quiz import QuizSubmission
from study_coach.models.student import StudentProfile
from study_coach.services.workshop_facade import WorkshopFacade

# Load environment configuration
load_dotenv()

st.set_page_config(
    page_title="Gemini ADK Study Coach Lab",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run_async(coro: Any) -> Any:
    """Helper to run async facade methods inside synchronous Streamlit execution."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        # Inside an active loop, run in a new sub-thread or runner
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    return loop.run_until_complete(coro)


# Initialize persistent Facade in Streamlit session state
if "facade" not in st.session_state:
    st.session_state.facade = WorkshopFacade()

if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"

if "user_id" not in st.session_state:
    st.session_state.user_id = f"student_{uuid.uuid4().hex[:6]}"

facade: WorkshopFacade = st.session_state.facade
session_id: str = st.session_state.session_id
user_id: str = st.session_state.user_id

# Header
st.title("🎓 Gemini + Google ADK Multi-Agent Study Coach")
st.caption(
    "Adaptive certification preparation powered by Gemini, Google Agent Development Kit (ADK), "
    "and deterministic Python grading."
)

# Sidebar: Student Configuration
with st.sidebar:
    st.header("⚙️ Student Setup")
    certification_name = st.selectbox(
        "Target Certification",
        ["Google Cloud Generative AI Leader"],
        index=0,
    )
    raw_exp = st.selectbox(
        "Experience Level",
        ["beginner", "intermediate", "advanced"],
        index=0,
    )
    experience_level: Literal["beginner", "intermediate", "advanced"] = cast(
        Literal["beginner", "intermediate", "advanced"], raw_exp
    )
    days_until_exam = st.number_input(
        "Study Days Remaining",
        min_value=1,
        max_value=90,
        value=14,
        step=1,
    )
    daily_study_minutes = st.number_input(
        "Daily Study Budget (Minutes)",
        min_value=15,
        max_value=240,
        value=90,
        step=15,
    )

    if st.button("🚀 Start / Reset Session", use_container_width=True):
        profile = StudentProfile(
            experience_level=experience_level,
            daily_study_minutes=int(daily_study_minutes),
        )
        run_async(
            facade.get_or_create_session(
                session_id=session_id,
                user_id=user_id,
                student_profile=profile,
                certification_name=certification_name,
                days_remaining=int(days_until_exam),
            )
        )
        st.session_state.active_quiz = None
        st.session_state.active_quiz_result = None
        st.session_state.explained_topic = None
        st.success(f"Session started! (ID: {session_id})")

    st.divider()
    st.markdown("**Session Info:**")
    st.text(f"Session ID: {session_id}")
    st.text(f"User ID: {user_id}")

    # Check API key status safely without printing secret
    has_api_key = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if has_api_key:
        st.success("API Key: Configured")
    else:
        st.warning("API Key: Not Found in .env")

# Navigation Tabs
tab_plan, tab_learn, tab_quiz, tab_adaptive = st.tabs(
    ["📅 Study Plan", "📖 Learn Topic", "📝 Practice Quiz", "🔄 Adaptive Plan"]
)

# Fetch current session state
current_session = run_async(facade.get_session(session_id, user_id))

# ==============================================================================
# TAB 1: STUDY PLAN
# ==============================================================================
with tab_plan:
    st.header("📅 Personalized Certification Study Plan")
    st.write(
        "The Study Planner agent crafts a day-by-day roadmap aligned with curriculum objectives "
        "and validates that daily limits are strictly respected."
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Generate Initial Plan", type="primary", use_container_width=True):
            profile = StudentProfile(
                experience_level=experience_level,
                daily_study_minutes=int(daily_study_minutes),
            )
            with st.spinner("Invoking Study Planner agent via Google ADK..."):
                try:
                    plan = run_async(
                        facade.create_study_plan(
                            session_id=session_id,
                            user_id=user_id,
                            student_profile=profile,
                            certification_name=certification_name,
                            days_until_exam=int(days_until_exam),
                        )
                    )
                    st.success("Study plan successfully generated!")
                    current_session = run_async(facade.get_session(session_id, user_id))
                except (RuntimeError, ValueError) as err:
                    st.error(f"Error generating study plan: {err}")

    if current_session and current_session.current_study_plan:
        plan = current_session.current_study_plan
        st.subheader(
            f"Active Schedule: {plan.days_until_exam} Days ({plan.total_planned_minutes} Total Planned Minutes)"
        )
        st.info(f"**Planning Notes:** {plan.planning_notes}")

        # Day selector
        day_options = [f"Day {d.day_number}: {d.title}" for d in plan.days]
        selected_day_idx = st.selectbox(
            "Select a day to view its detailed activities:",
            range(len(plan.days)),
            format_func=lambda i: day_options[i],
        )

        selected_day = plan.days[selected_day_idx]
        st.markdown(f"### Details for {day_options[selected_day_idx]}")
        st.write(
            f"**Total Day Time:** {selected_day.total_minutes} / {plan.daily_study_minutes} minutes"
        )

        for act in selected_day.activities:
            with st.container(border=True):
                st.markdown(
                    f"**Topic:** `{act.topic_id}` | **Type:** `{act.activity_type}`"
                )
                st.write(act.description)
                st.caption(f"⏱️ Duration: {act.duration_minutes} minutes")
    else:
        st.info(
            "No active study plan found. Click 'Generate Initial Plan' above to start."
        )

# ==============================================================================
# TAB 2: LEARN TOPIC
# ==============================================================================
with tab_learn:
    st.header("📖 Topic Deep Dive")
    st.write(
        "Ask the Topic Expert agent to teach a curriculum topic adapted to your level, "
        "featuring analogies, architectural examples, and comprehension checks."
    )

    topics = facade.get_supported_curriculum_topics()
    topic_map = {f"{t['title']} ({t['id']})": t["id"] for t in topics}

    selected_topic_label = st.selectbox(
        "Select Curriculum Topic", list(topic_map.keys())
    )
    chosen_topic_id = topic_map[selected_topic_label]

    if st.button("Teach This Topic", type="primary"):
        with st.spinner(
            "Topic Expert agent is generating explanation grounded in curriculum..."
        ):
            try:
                explanation = run_async(
                    facade.explain_topic(
                        topic_id=chosen_topic_id,
                        experience_level=experience_level,
                    )
                )
                st.session_state.explained_topic = explanation
                st.success("Topic explanation loaded!")
            except (RuntimeError, ValueError) as err:
                st.error(f"Error fetching topic explanation: {err}")

    if st.session_state.get("explained_topic"):
        exp = st.session_state.explained_topic
        st.markdown(f"## {exp.topic_title} (`{exp.topic_id}`)")
        st.caption(f"Adapted Level: **{exp.experience_level.capitalize()}**")

        st.markdown("### 🎯 Learning Objectives")
        for obj in exp.learning_objectives:
            st.markdown(f"- {obj}")

        st.markdown("### 💡 Key Concepts & Vocabulary")
        st.write(", ".join(f"`{c}`" for c in exp.key_concepts))

        st.markdown("### 📘 In-Depth Explanation")
        st.write(exp.explanation)

        st.markdown("### ☁️ Practical Google Cloud Architecture Example")
        st.info(exp.practical_example)

        st.markdown("### ⚠️ Common Misconceptions & Pitfalls")
        for m in exp.common_misconceptions:
            st.warning(m)

        st.markdown("### ❓ Self-Assessment Comprehension Questions")
        for q in exp.comprehension_questions:
            st.markdown(f"- {q}")

# ==============================================================================
# TAB 3: PRACTICE QUIZ
# ==============================================================================
with tab_quiz:
    st.header("📝 Certification Practice Quiz")
    st.write(
        "Test your knowledge with original practice questions. "
        "Answer keys are strictly protected on the backend until you submit."
    )

    q_col1, q_col2 = st.columns([1, 1])
    with q_col1:
        quiz_topic_label = st.selectbox(
            "Select Quiz Topic",
            list(topic_map.keys()),
            key="quiz_topic_select",
        )
        quiz_topic_id = topic_map[quiz_topic_label]
    with q_col2:
        question_count = st.number_input(
            "Number of Questions",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
        )

    if st.button("Generate Practice Quiz", type="primary"):
        if not current_session:
            st.error("Please start a session in the sidebar first.")
        else:
            with st.spinner(
                "Quiz Generator agent is creating multiple choice questions..."
            ):
                try:
                    student_questions = run_async(
                        facade.generate_quiz(
                            session_id=session_id,
                            user_id=user_id,
                            topic_ids=[quiz_topic_id],
                            question_count=int(question_count),
                            experience_level=experience_level,
                        )
                    )
                    st.session_state.active_quiz = student_questions
                    st.session_state.active_quiz_result = None
                    st.session_state.student_choices = {}
                    st.success(
                        f"Generated {len(student_questions)} practice questions!"
                    )
                except (RuntimeError, ValueError) as err:
                    st.error(f"Error generating quiz: {err}")

    if st.session_state.get("active_quiz"):
        questions = st.session_state.active_quiz
        st.markdown(f"### Questions ({len(questions)} items)")

        with st.form("quiz_submission_form"):
            user_answers: dict[str, Literal["A", "B", "C", "D"]] = {}
            radio_opts: list[Literal["A", "B", "C", "D"]] = ["A", "B", "C", "D"]
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**Question {idx} ({q.question_id}):** {q.question_text}")

                def _format_option(opt_key: str, q_item: Any = q) -> str:
                    return f"{opt_key}: {q_item.options.get(opt_key, '')}"

                chosen_opt = st.radio(
                    f"Select your answer for Question {idx}:",
                    options=["A", "B", "C", "D"],
                    format_func=_format_option,
                    key=f"ans_{q.question_id}",
                )
                user_answers[q.question_id] = cast(
                    Literal["A", "B", "C", "D"], chosen_opt or "A"
                )
                st.divider()

            submit_quiz_button = st.form_submit_button(
                "Submit Answers for Deterministic Grading", type="primary"
            )

        if submit_quiz_button:
            with st.spinner("Grading answers deterministically via Python..."):
                try:
                    submission = QuizSubmission(
                        quiz_id=current_session.current_quiz_id or "default_quiz",
                        student_answers=user_answers,
                    )
                    grading_result = run_async(
                        facade.submit_quiz(
                            session_id=session_id,
                            user_id=user_id,
                            submission=submission,
                        )
                    )
                    st.session_state.active_quiz_result = grading_result
                    current_session = run_async(facade.get_session(session_id, user_id))
                    st.success("Quiz graded successfully!")
                except (RuntimeError, ValueError) as err:
                    st.error(f"Error submitting quiz: {err}")

    if st.session_state.get("active_quiz_result"):
        res = st.session_state.active_quiz_result
        st.markdown("## 📊 Evaluation & Diagnostic Feedback")
        score_metric, correct_metric = st.columns(2)
        with score_metric:
            st.metric("Score Percentage", f"{res.score_percentage:.1f}%")
        with correct_metric:
            st.metric(
                "Correct Answers", f"{res.correct_answers} / {res.total_questions}"
            )

        if res.weak_topics:
            st.error(
                f"⚠️ **Identified Weak Topics (< 70%):** {', '.join(res.weak_topics)}"
            )
        if res.strong_topics:
            st.success(
                f"✅ **Demonstrated Strong Topics (≥ 70%):** {', '.join(res.strong_topics)}"
            )

        st.markdown("### Detailed Item Feedback")
        for fb in res.question_feedback:
            status_icon = "✅" if fb.is_correct else "❌"
            with st.expander(
                f"{status_icon} Question {fb.question_id} ({fb.topic_id})"
            ):
                st.write(f"**Your Answer:** {fb.student_answer}")
                st.write(f"**Correct Answer:** {fb.correct_answer}")
                st.info(f"**Factual Explanation:** {fb.explanation}")

# ==============================================================================
# TAB 4: ADAPTIVE PLAN
# ==============================================================================
with tab_adaptive:
    st.header("🔄 Dynamic Adaptive Replanning")
    st.write(
        "When quiz results expose weak topics, the multi-agent orchestration layer "
        "re-engages the Study Planner to dynamically adapt the remaining schedule."
    )

    if current_session:
        st.markdown(f"**Current Plan Revision:** Rev {current_session.plan_revision}")
        if current_session.weak_topics:
            st.warning(
                f"Identified Weak Topics: {', '.join(current_session.weak_topics)}"
            )
        else:
            st.info(
                "No weak topics identified yet. Complete a practice quiz to generate performance evidence."
            )

        completed_days_input = st.number_input(
            "Days completed so far:",
            min_value=0,
            max_value=max(0, current_session.exam_deadline_or_days_remaining - 1),
            value=min(3, max(0, current_session.exam_deadline_or_days_remaining - 1)),
            step=1,
        )

        if st.button("Generate Adapted Plan", type="primary"):
            with st.spinner(
                "Re-engaging Study Planner agent with weak topic diagnostic feedback..."
            ):
                try:
                    adapted_plan = run_async(
                        facade.adapt_study_plan(
                            session_id=session_id,
                            user_id=user_id,
                            completed_days=int(completed_days_input),
                        )
                    )
                    st.success(
                        f"Adapted plan generated! (Revision {current_session.plan_revision + 1})"
                    )
                    current_session = run_async(facade.get_session(session_id, user_id))
                except (RuntimeError, ValueError) as err:
                    st.error(f"Error adapting study plan: {err}")

        if (
            current_session.study_plan_history
            and len(current_session.study_plan_history) > 1
        ):
            st.markdown("### 📜 Plan Evolution History")
            for rev_idx, h_plan in enumerate(current_session.study_plan_history, 1):
                with st.expander(
                    f"Plan Revision {rev_idx}: {h_plan.days_until_exam} Days ({h_plan.total_planned_minutes}m)"
                ):
                    st.write(f"**Planning Notes:** {h_plan.planning_notes}")
                    for d in h_plan.days:
                        st.text(
                            f"Day {d.day_number}: {d.title} ({d.total_minutes} min)"
                        )
    else:
        st.info("Start a session in the sidebar to test adaptive replanning.")
