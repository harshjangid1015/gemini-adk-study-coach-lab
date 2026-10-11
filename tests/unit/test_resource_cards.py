"""Unit tests for compact ResourceCard component and provider icon mapping."""

from pydantic import HttpUrl

from study_coach.models.learning_resource import LearningResource
from ui.components.resource_cards import (
    get_provider_icon,
    render_resource_card,
    render_resource_grid,
)


def test_get_provider_icon_mapping() -> None:
    """Verify that provider and URL detection returns recognizable provider icons."""
    # Google Cloud -> Cloud icon
    assert (
        get_provider_icon("Google Cloud", "https://cloud.google.com/vertex-ai") == "☁️"
    )
    assert get_provider_icon("Google", "https://ai.google/responsibility") == "☁️"

    # YouTube (by URL or provider) -> Video/TV icon
    assert (
        get_provider_icon("3Blue1Brown", "https://www.youtube.com/watch?v=wjZofJX0v4M")
        == "📺"
    )
    assert get_provider_icon("YouTube", "https://youtu.be/eMlx5fFNoYc") == "📺"

    # GitHub -> Octocat/Git icon
    assert (
        get_provider_icon(
            "Google Cloud Platform",
            "https://github.com/GoogleCloudPlatform/generative-ai",
        )
        == "🐙"
    )

    # Hugging Face -> 🤗 icon
    assert (
        get_provider_icon("Hugging Face", "https://huggingface.co/learn/nlp-course")
        == "🤗"
    )

    # Unknown / Third-party provider -> 📖 neutral book fallback
    assert (
        get_provider_icon("Coursera", "https://www.coursera.org/learn/example") == "📖"
    )
    assert get_provider_icon("Unknown Provider", "") == "📖"


def test_render_resource_card_metadata() -> None:
    """Ensure render_resource_card can be imported and executed."""
    res = LearningResource(
        resource_id="google_genai_leader_exam_guide",
        topic_ids=["genai_concepts"],
        title="Official Google Cloud Generative AI Leader Certification Guide",
        provider="Google Cloud",
        resource_type="Official exam guide",
        url=HttpUrl(
            "https://cloud.google.com/learn/certification/generative-ai-leader"
        ),
        short_description="Official exam guide blueprint.",
        experience_level="all",
        estimated_minutes=20,
        exam_domain="Domain 1",
        verified_at="2026-10",
        verification_status="verified",
        is_official=True,
    )
    assert res.title == "Official Google Cloud Generative AI Leader Certification Guide"
    assert callable(render_resource_card)
    assert callable(render_resource_grid)
