"""Unit tests for ResourceCard provider logo mapping and hostname parsing."""

from pydantic import HttpUrl

from study_coach.models.learning_resource import LearningResource
from ui.components.resource_cards import (
    ASSETS_DIR,
    extract_url_hostname,
    get_provider_icon_name,
    get_provider_logo_svg,
    render_resource_card,
    render_resource_grid,
)


def test_extract_url_hostname_valid_and_normalization() -> None:
    """Verify that hostnames are correctly extracted and lowercased."""
    assert (
        extract_url_hostname("https://cloud.google.com/vertex-ai") == "cloud.google.com"
    )
    assert (
        extract_url_hostname("HTTPS://DEVELOPERS.GOOGLE.COM/ml")
        == "developers.google.com"
    )
    assert (
        extract_url_hostname("http://www.youtube.com/watch?v=123") == "www.youtube.com"
    )
    assert extract_url_hostname("https://youtu.be/abc12345678") == "youtu.be"
    assert extract_url_hostname("https://github.com/repo/sub") == "github.com"
    assert extract_url_hostname("https://HuggingFace.co/models") == "huggingface.co"
    assert (
        extract_url_hostname("https://www.linkedin.com/in/student")
        == "www.linkedin.com"
    )


def test_extract_url_hostname_invalid_and_malformed() -> None:
    """Reject empty, malformed, or unsupported scheme URLs."""
    assert extract_url_hostname("") is None
    assert extract_url_hostname("not-a-url") is None
    assert extract_url_hostname("ftp://files.example.com") is None
    assert extract_url_hostname("javascript:alert(1)") is None
    assert extract_url_hostname("mailto:user@example.com") is None


def test_get_provider_icon_name_mapping() -> None:
    """Verify strict hostname-based mapping to provider logo assets."""
    # Google Cloud
    assert (
        get_provider_icon_name(
            "https://cloud.google.com/learn/certification/generative-ai-leader"
        )
        == "google-cloud"
    )
    assert (
        get_provider_icon_name("https://console.cloud.google.com/vertex-ai")
        == "google-cloud"
    )

    # Google Developers
    assert (
        get_provider_icon_name("https://developers.google.com/machine-learning")
        == "google-developers"
    )

    # General / Verified Google subdomains
    assert (
        get_provider_icon_name("https://ai.google/responsibility/principles/")
        == "google"
    )
    assert get_provider_icon_name("https://www.google.com/search") == "google"
    assert (
        get_provider_icon_name("https://deepmind.google/technologies/gemini/")
        == "google"
    )

    # YouTube video and shortened URLs
    assert (
        get_provider_icon_name("https://www.youtube.com/watch?v=wjZofJX0v4M")
        == "youtube"
    )
    assert (
        get_provider_icon_name("https://youtube.com/watch?v=eMlx5fFNoYc") == "youtube"
    )
    assert get_provider_icon_name("https://m.youtube.com/watch?v=123") == "youtube"
    assert get_provider_icon_name("https://youtu.be/wjZofJX0v4M") == "youtube"

    # GitHub
    assert (
        get_provider_icon_name("https://github.com/GoogleCloudPlatform/generative-ai")
        == "github"
    )

    # Hugging Face
    assert (
        get_provider_icon_name("https://huggingface.co/learn/nlp-course/chapter1/1")
        == "huggingface"
    )

    # LinkedIn
    assert (
        get_provider_icon_name(
            "https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fexample.com"
        )
        == "linkedin"
    )
    assert get_provider_icon_name("https://linkedin.com/feed") == "linkedin"

    # Other external domains -> neutral fallback
    assert (
        get_provider_icon_name("https://coursera.org/learn/ml") == "external-resource"
    )
    assert get_provider_icon_name("https://example.com/guide") == "external-resource"
    assert get_provider_icon_name("https://medium.com/article") == "external-resource"

    # No arbitrary domain impersonation: googlecloud.fake.com or my-youtube.org
    assert (
        get_provider_icon_name("https://googlecloud.phishing.com/test")
        == "external-resource"
    )
    assert get_provider_icon_name("https://my-youtube.org/video") == "external-resource"


def test_provider_icon_svg_assets_exist() -> None:
    """Verify that all required SVG icon assets exist on disk and contain valid SVG."""
    required_icons = [
        "google-cloud",
        "google-developers",
        "google",
        "youtube",
        "github",
        "huggingface",
        "linkedin",
        "external-resource",
    ]
    for icon in required_icons:
        svg = get_provider_logo_svg(icon)
        assert svg.startswith("<svg")
        assert "</svg>" in svg
        assert (ASSETS_DIR / f"{icon}.svg").is_file()


def test_render_resource_card_callable() -> None:
    """Verify render_resource_card and render_resource_grid execution."""
    res = LearningResource(
        resource_id="google_genai_leader_exam_guide",
        topic_ids=["genai_concepts"],
        title="Official Google Cloud Generative AI Leader Certification Guide",
        provider="Google Cloud",
        resource_type="Official exam guide",
        url=HttpUrl(
            "https://cloud.google.com/learn/certification/generative-ai-leader"
        ),
        short_description="Official exam blueprint.",
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
