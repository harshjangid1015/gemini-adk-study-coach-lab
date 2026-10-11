"""Automated UI testing using Streamlit's official AppTest framework."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from study_coach.models.student import StudentProfile
from study_coach.models.study_plan import StudyActivity, StudyDay, StudyPlan
from study_coach.models.topic_explanation import TopicExplanation


@pytest.fixture
def sample_study_plan() -> StudyPlan:
    return StudyPlan(
        certification_name="Google Cloud Generative AI Leader",
        days_until_exam=14,
        daily_study_minutes=90,
        days=[
            StudyDay(
                day_number=i,
                title=f"Day {i} Focus",
                activities=[
                    StudyActivity(
                        topic_id="llm_architecture" if i == 4 else "genai_concepts",
                        activity_type="learning",
                        description=f"Study core concepts for day {i}",
                        duration_minutes=90,
                    )
                ],
                total_minutes=90,
            )
            for i in range(1, 15)
        ],
        total_planned_minutes=1260,
        planning_notes="14-day comprehensive roadmap.",
    )


def test_streamlit_ui_initial_render() -> None:
    """Verify that Streamlit app initializes without uncaught exceptions."""
    app_path = Path(__file__).resolve().parent.parent.parent / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()
    assert not at.exception
    # Verify title
    assert "Gemini + Google ADK Multi-Agent Study Coach" in at.title[0].value


def test_streamlit_ui_day_4_resources(sample_study_plan: StudyPlan) -> None:
    """Verify Day 4 selection displays matched learning resources and time budget notice."""
    app_path = Path(__file__).resolve().parent.parent.parent / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()

    # Create session and populate study plan
    facade = at.session_state["facade"]
    import asyncio

    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = asyncio.run(
        facade.get_or_create_session(
            at.session_state["session_id"],
            at.session_state["user_id"],
            profile,
        )
    )
    session.current_study_plan = sample_study_plan
    asyncio.run(facade.session_service.save_session(session))

    # Re-run after plan is present
    at.run()
    assert not at.exception

    # Select Day 4 in the day selectbox by label
    day_selectbox = None
    for sb in at.selectbox:
        if "detailed activities" in sb.label:
            day_selectbox = sb
            break
    assert day_selectbox is not None
    day_selectbox.select_index(3)
    at.run()
    assert not at.exception

    # Check that Day 4 details rendered
    markdown_texts = [m.value for m in at.markdown]
    has_day4 = any("Day 4" in text for text in markdown_texts)
    assert has_day4

    # Verify curated learning resources section rendered
    has_resources_header = any(
        "Curated Learning Resources for Day 4" in text for text in markdown_texts
    )
    assert has_resources_header

    # Verify compact resource cards rendered (titles and provider metadata present, NO thumbnail images)
    assert len(at.image) == 0
    has_card_title = any(
        "Official Google Cloud Generative AI Leader" in text for text in markdown_texts
    )
    assert has_card_title


def test_streamlit_ui_learn_topic_diagram_and_code() -> None:
    """Verify Learn Topic displays architecture diagram, code demo, and resources."""
    app_path = Path(__file__).resolve().parent.parent.parent / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()

    # Populate explained_topic in session state
    sample_explanation = TopicExplanation(
        topic_id="llm_architecture",
        topic_title="LLM Architecture & Transformers",
        experience_level="beginner",
        learning_objectives=["Understand self-attention", "Explain tokenization"],
        key_concepts=["Self-Attention", "Embeddings", "Positional Encoding"],
        explanation="Transformers process entire sequences concurrently using self-attention.",
        practical_example="Deploying Gemini on Vertex AI endpoints.",
        common_misconceptions=["Transformers process words one-by-one linearly."],
        comprehension_questions=["What role does self-attention play?"],
        source_references=[
            "https://cloud.google.com/learn/certification/generative-ai-leader"
        ],
    )
    at.session_state["explained_topic"] = sample_explanation
    at.run()
    assert not at.exception

    markdown_texts = [m.value for m in at.markdown]

    # Verify Mermaid diagram code block is rendered
    has_mermaid = any("```mermaid" in text for text in markdown_texts)
    assert has_mermaid

    # Verify Code blocks are present
    assert len(at.code) >= 2  # tokenization demo and attention demo expected outputs

    # Verify compact resource cards rendered without thumbnail images
    assert len(at.image) == 0
    has_resource_title = any(
        "Transformers Work" in text or "Attention" in text for text in markdown_texts
    )
    assert has_resource_title


def test_streamlit_ui_weak_topic_remediation() -> None:
    """Verify that Adaptive Plan tab displays remediation pathways for identified weak topics."""
    app_path = Path(__file__).resolve().parent.parent.parent / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()

    facade = at.session_state["facade"]
    import asyncio

    profile = StudentProfile(experience_level="beginner", daily_study_minutes=90)
    session = asyncio.run(
        facade.get_or_create_session(
            at.session_state["session_id"],
            at.session_state["user_id"],
            profile,
        )
    )
    # Inject weak topics
    session.weak_topics = ["llm_architecture"]
    asyncio.run(facade.session_service.save_session(session))

    at.run()
    assert not at.exception

    markdown_texts = [m.value for m in at.markdown]
    has_remediation = any(
        "Recommended Remediation Pathways" in text for text in markdown_texts
    )
    assert has_remediation

    has_steps = any(
        "Review the visual architecture diagram" in text for text in markdown_texts
    )
    assert has_steps

    # Verify compact cards rendered for weak topic remediation with zero thumbnail images
    assert len(at.image) == 0
    has_remediation_resources = any(
        "Transformers Work" in text or "Attention" in text or "Official Google" in text
        for text in markdown_texts
    )
    assert has_remediation_resources
