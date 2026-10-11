"""Unit tests for ResourceCard component and thumbnail resolvers."""

from pydantic import HttpUrl

from study_coach.models.learning_resource import LearningResource
from ui.components.resource_cards import (
    extract_youtube_video_id,
    generate_fallback_svg_thumbnail,
    get_resource_thumbnail_url,
    get_youtube_thumbnail_url,
)


def test_extract_youtube_video_id_valid() -> None:
    """Test extracting valid 11-character video IDs from various YouTube URL formats."""
    # Standard watch URL
    assert (
        extract_youtube_video_id("https://www.youtube.com/watch?v=wjZofJX0v4M")
        == "wjZofJX0v4M"
    )
    # Watch URL with extra query params
    assert (
        extract_youtube_video_id("https://youtube.com/watch?v=eMlx5fFNoYc&t=120s")
        == "eMlx5fFNoYc"
    )
    # Shortened youtu.be URL
    assert extract_youtube_video_id("https://youtu.be/wjZofJX0v4M") == "wjZofJX0v4M"
    # Embed URL
    assert (
        extract_youtube_video_id("https://www.youtube.com/embed/eMlx5fFNoYc")
        == "eMlx5fFNoYc"
    )
    # /v/ URL
    assert (
        extract_youtube_video_id("https://www.youtube.com/v/wjZofJX0v4M")
        == "wjZofJX0v4M"
    )


def test_extract_youtube_video_id_invalid() -> None:
    """Test rejection of malformed, invalid, or non-YouTube URLs."""
    # Empty or None
    assert extract_youtube_video_id("") is None
    # Non-YouTube domain
    assert extract_youtube_video_id("https://cloud.google.com/vertex-ai") is None
    assert extract_youtube_video_id("https://vimeo.com/123456789") is None
    # Invalid video ID length (not 11 chars)
    assert extract_youtube_video_id("https://www.youtube.com/watch?v=short") is None
    assert (
        extract_youtube_video_id("https://www.youtube.com/watch?v=toolongvideoid12345")
        is None
    )
    # Invalid characters in ID
    assert (
        extract_youtube_video_id("https://www.youtube.com/watch?v=invalid!@#$%") is None
    )


def test_get_youtube_thumbnail_url() -> None:
    """Test generating official YouTube HQ thumbnail URLs."""
    url = "https://www.youtube.com/watch?v=wjZofJX0v4M"
    thumb = get_youtube_thumbnail_url(url)
    assert thumb == "https://i.ytimg.com/vi/wjZofJX0v4M/hqdefault.jpg"

    invalid_thumb = get_youtube_thumbnail_url("https://example.com/not-youtube")
    assert invalid_thumb is None


def test_get_resource_thumbnail_precedence() -> None:
    """Verify thumbnail resolution precedence: YouTube > metadata thumbnail_url > SVG fallback."""
    # 1. YouTube resource
    yt_resource = LearningResource(
        resource_id="yt_res",
        topic_ids=["llm_architecture"],
        title="Attention Visualized",
        provider="3Blue1Brown",
        resource_type="Video",
        url=HttpUrl("https://www.youtube.com/watch?v=eMlx5fFNoYc"),
        short_description="Intuitive visual math explanation of attention.",
        experience_level="all",
        estimated_minutes=25,
        exam_domain="Domain 1",
        verified_at="2026-10",
        verification_status="verified",
        is_official=False,
    )
    assert (
        get_resource_thumbnail_url(yt_resource)
        == "https://i.ytimg.com/vi/eMlx5fFNoYc/hqdefault.jpg"
    )

    # 2. Non-YouTube with custom thumbnail_url
    custom_thumb_res = LearningResource(
        resource_id="custom_res",
        topic_ids=["genai_concepts"],
        title="Vertex AI Overview",
        provider="Google Cloud",
        resource_type="Official documentation",
        url=HttpUrl("https://cloud.google.com/vertex-ai/docs"),
        thumbnail_url=HttpUrl("https://cloud.google.com/images/vertex-preview.png"),
        short_description="Official overview of Google Cloud Vertex AI.",
        experience_level="beginner",
        estimated_minutes=30,
        exam_domain="Domain 1",
        verified_at="2026-10",
        verification_status="verified",
        is_official=True,
    )
    assert (
        get_resource_thumbnail_url(custom_thumb_res)
        == "https://cloud.google.com/images/vertex-preview.png"
    )

    # 3. Non-YouTube without custom thumbnail_url -> SVG fallback
    fallback_res = LearningResource(
        resource_id="fallback_res",
        topic_ids=["responsible_ai"],
        title="Responsible AI Principles",
        provider="Google",
        resource_type="Official documentation",
        url=HttpUrl("https://ai.google/responsibility/principles/"),
        short_description="Google's 7 AI principles and safety framework.",
        experience_level="all",
        estimated_minutes=20,
        exam_domain="Domain 3",
        verified_at="2026-10",
        verification_status="verified",
        is_official=True,
    )
    thumb = get_resource_thumbnail_url(fallback_res)
    assert thumb.startswith("data:image/svg+xml;utf8,<svg")
    assert "Google" in thumb
    assert "Responsible AI Principles" in thumb


def test_generate_fallback_svg_thumbnail() -> None:
    """Ensure SVG fallback generates valid 16:9 data URI and contains proper labels."""
    res = LearningResource(
        resource_id="svg_test",
        topic_ids=["genai_concepts"],
        title="ML Crash Course",
        provider="Google Developers",
        resource_type="Interactive tutorial",
        url=HttpUrl("https://developers.google.com/machine-learning/crash-course"),
        short_description="Interactive tutorials on neural networks and embeddings.",
        experience_level="beginner",
        estimated_minutes=45,
        exam_domain="Domain 1",
        verified_at="2026-10",
        verification_status="verified",
        is_official=True,
    )
    svg_uri = generate_fallback_svg_thumbnail(res)
    assert svg_uri.startswith("data:image/svg+xml;utf8,")
    assert 'viewBox="0 0 640 360"' in svg_uri
    assert "OFFICIAL GOOGLE" in svg_uri
    assert "Google Developers" in svg_uri
