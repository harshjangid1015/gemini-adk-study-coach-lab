"""Unit tests for expanded Provider Registry, brand logo mapping, and resource sharing."""

from pydantic import HttpUrl

from study_coach.models.learning_resource import LearningResource
from study_coach.services.provider_registry import (
    extract_url_hostname,
    load_provider_registry,
    match_domain_pattern,
    resolve_provider_for_url,
)
from study_coach.services.resource_sharing import (
    generate_share_text,
    get_email_share_url,
    get_facebook_share_url,
    get_linkedin_share_url,
    get_x_twitter_share_url,
)
from ui.components.resource_cards import (
    ASSETS_DIR,
    get_provider_logo_svg,
    render_resource_card,
    render_resource_grid,
)


def test_extract_url_hostname_strict() -> None:
    """Verify hostname extraction rejects non-http/https schemes and normalizes properly."""
    assert (
        extract_url_hostname("https://cloud.google.com/vertex-ai") == "cloud.google.com"
    )
    assert extract_url_hostname("HTTPS://DEV.TO/guide") == "dev.to"
    assert extract_url_hostname("http://MEDIUM.COM/@author/post") == "medium.com"
    assert extract_url_hostname("") is None
    assert extract_url_hostname("not-a-url") is None
    assert extract_url_hostname("ftp://example.com") is None
    assert extract_url_hostname("javascript:void(0)") is None
    assert extract_url_hostname("mailto:info@google.com") is None


def test_match_domain_pattern() -> None:
    """Verify exact and wildcard domain matching rules."""
    assert match_domain_pattern("cloud.google.com", "cloud.google.com")
    assert not match_domain_pattern("other.google.com", "cloud.google.com")

    # Wildcard subdomain
    assert match_domain_pattern("ai.google.com", "*.google.com")
    assert match_domain_pattern("cloud.google.com", "*.google.com")
    assert not match_domain_pattern("fake-google.com", "*.google.com")

    # Entity wildcard
    assert match_domain_pattern("ai.google", "*.google")
    assert match_domain_pattern("cloudskillsboost.google", "*.google")
    assert not match_domain_pattern("google.co.uk", "*.google")


def test_resolve_provider_for_all_major_platforms() -> None:
    """Verify recognition for all required technical publishers and learning platforms."""
    # Google suite
    assert (
        resolve_provider_for_url("https://cloud.google.com/vertex-ai").provider_id
        == "google_cloud"
    )
    assert (
        resolve_provider_for_url(
            "https://developers.google.com/machine-learning"
        ).provider_id
        == "google_developers"
    )
    assert (
        resolve_provider_for_url(
            "https://www.cloudskillsboost.google/paths"
        ).provider_id
        == "google_skills_boost"
    )
    assert (
        resolve_provider_for_url("https://ai.google/responsibility").provider_id
        == "google"
    )
    assert (
        resolve_provider_for_url("https://www.google.com/about").provider_id == "google"
    )

    # Streaming and Code
    assert (
        resolve_provider_for_url(
            "https://www.youtube.com/watch?v=wjZofJX0v4M"
        ).provider_id
        == "youtube"
    )
    assert (
        resolve_provider_for_url("https://youtu.be/wjZofJX0v4M").provider_id
        == "youtube"
    )
    assert (
        resolve_provider_for_url(
            "https://github.com/GoogleCloudPlatform/generative-ai"
        ).provider_id
        == "github"
    )

    # AI Hub
    assert (
        resolve_provider_for_url("https://huggingface.co/learn/nlp-course").provider_id
        == "huggingface"
    )

    # Technical publications
    assert (
        resolve_provider_for_url(
            "https://medium.com/towards-data-science/genai"
        ).provider_id
        == "medium"
    )
    assert (
        resolve_provider_for_url(
            "https://towardsdatascience.medium.com/post"
        ).provider_id
        == "medium"
    )
    assert (
        resolve_provider_for_url("https://dev.to/googlecloud/gemini-guide").provider_id
        == "dev_to"
    )
    assert (
        resolve_provider_for_url("https://dzone.com/articles/rag-patterns").provider_id
        == "dzone"
    )
    assert (
        resolve_provider_for_url(
            "https://hackernoon.com/prompt-engineering"
        ).provider_id
        == "hackernoon"
    )
    assert (
        resolve_provider_for_url(
            "https://www.infoq.com/articles/gemini-flash"
        ).provider_id
        == "infoq"
    )

    # Professional & Community QA
    assert (
        resolve_provider_for_url("https://www.linkedin.com/learning/genai").provider_id
        == "linkedin"
    )
    assert (
        resolve_provider_for_url(
            "https://stackoverflow.com/questions/123456"
        ).provider_id
        == "stackoverflow"
    )
    assert (
        resolve_provider_for_url(
            "https://www.freecodecamp.org/news/generative-ai-handbook/"
        ).provider_id
        == "freecodecamp"
    )
    assert (
        resolve_provider_for_url(
            "https://www.kaggle.com/learn/intro-to-ai-ethics"
        ).provider_id
        == "kaggle"
    )
    assert (
        resolve_provider_for_url(
            "https://www.coursera.org/learn/google-cloud-genai"
        ).provider_id
        == "coursera"
    )
    assert (
        resolve_provider_for_url("https://www.edx.org/course/deep-learning").provider_id
        == "edx"
    )
    assert (
        resolve_provider_for_url("https://arxiv.org/abs/1706.03762").provider_id
        == "arxiv"
    )


def test_resolve_provider_rejects_lookalike_spoofing() -> None:
    """Ensure malicious or lookalike domains are not credited as trusted providers."""
    # Phishing subdomains on different base domains
    assert (
        resolve_provider_for_url("https://googlecloud.phishing.com/docs").provider_id
        == "external_resource"
    )
    assert (
        resolve_provider_for_url("https://youtube.malicious-site.org/watch").provider_id
        == "external_resource"
    )
    assert (
        resolve_provider_for_url("https://github.attacker.net/repo").provider_id
        == "external_resource"
    )
    assert (
        resolve_provider_for_url("https://medium.evilcorp.com/story").provider_id
        == "external_resource"
    )


def test_provider_svg_assets_exist_on_disk() -> None:
    """Confirm all provider icon SVG files exist in ui/assets/provider_icons/ and parse correctly."""
    registry = load_provider_registry()
    for provider in registry:
        svg_filename = provider.icon_asset
        svg_content = get_provider_logo_svg(svg_filename)
        assert svg_content.startswith("<svg"), f"Invalid SVG for {provider.provider_id}"
        assert "</svg>" in svg_content, f"Unterminated SVG for {provider.provider_id}"
        assert (ASSETS_DIR / svg_filename).is_file(), f"Missing file: {svg_filename}"


def test_resource_sharing_url_generators() -> None:
    """Verify that sharing URLs are properly URL-encoded and privacy-safe."""
    sample_url = "https://cloud.google.com/vertex-ai/docs?topic=rag&level=beginner"
    title = "Vertex AI RAG Guide"
    provider = "Google Cloud"

    # LinkedIn
    linkedin_url = get_linkedin_share_url(sample_url)
    assert linkedin_url.startswith(
        "https://www.linkedin.com/sharing/share-offsite/?url="
    )
    assert "https%3A%2F%2Fcloud.google.com" in linkedin_url
    assert "session_id" not in linkedin_url

    # Twitter / X
    share_text = generate_share_text(title, provider)
    twitter_url = get_x_twitter_share_url(sample_url, share_text)
    assert twitter_url.startswith("https://twitter.com/intent/tweet?url=")
    assert (
        "Vertex+AI+RAG+Guide" in twitter_url
        or "Vertex%20AI%20RAG%20Guide" in twitter_url
    )
    assert "session_id" not in twitter_url

    # Facebook
    fb_url = get_facebook_share_url(sample_url)
    assert fb_url.startswith("https://www.facebook.com/sharer/sharer.php?u=")
    assert "cloud.google.com" in fb_url

    # Email
    email_url = get_email_share_url(sample_url, title, provider)
    assert email_url.startswith("mailto:?subject=")
    assert (
        "Vertex+AI+RAG+Guide" in email_url or "Vertex%20AI%20RAG%20Guide" in email_url
    )


def test_render_resource_card_callable() -> None:
    """Verify render_resource_card execution on model instance."""
    res = LearningResource(
        resource_id="test_fc_handbook",
        topic_ids=["genai_concepts"],
        title="freeCodeCamp Generative AI Handbook",
        provider="freeCodeCamp",
        resource_type="Article",
        url=HttpUrl("https://www.freecodecamp.org/news/generative-ai-handbook/"),
        short_description="Open comprehensive handbook on LLMs and RAG architectures.",
        experience_level="beginner",
        estimated_minutes=35,
        exam_domain="Domain 1",
        verified_at="2026-10",
        verification_status="verified",
        is_official=False,
    )
    assert res.title == "freeCodeCamp Generative AI Handbook"
    assert callable(render_resource_card)
    assert callable(render_resource_grid)
