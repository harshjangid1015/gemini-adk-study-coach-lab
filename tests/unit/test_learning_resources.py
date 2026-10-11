"""Unit tests for the Curated Learning Resource Catalog and Tools."""

import pytest
from pydantic import ValidationError

from study_coach.models.learning_resource import LearningResource
from study_coach.tools.resource_tools import (
    filter_resources_by_experience,
    filter_resources_by_type,
    get_official_exam_resources,
    get_resources_for_day,
    get_resources_for_topic,
    load_learning_resources,
)


def test_load_learning_resources_valid() -> None:
    """Ensure catalog loads from default YAML and parses into valid Pydantic models."""
    resources = load_learning_resources()
    assert len(resources) >= 8

    # Ensure unique resource IDs
    ids = [r.resource_id for r in resources]
    assert len(ids) == len(set(ids)), "Resource IDs must be unique"

    # Ensure all resources have valid URLs and providers
    for r in resources:
        url_str = str(r.url)
        assert url_str.startswith(("http://", "https://"))
        assert len(r.title) > 0

        assert len(r.provider) > 0
        assert r.verification_status == "verified"


def test_get_resources_for_topic() -> None:
    """Test retrieving resources by topic ID."""
    arch_resources = get_resources_for_topic("llm_architecture")
    assert len(arch_resources) >= 2
    resource_ids = [r.resource_id for r in arch_resources]
    assert "google_genai_leader_exam_guide" in resource_ids
    assert "3b1b_transformer_video" in resource_ids


def test_get_resources_for_day() -> None:
    """Test retrieving resources for multiple topics in a study day."""
    day_resources = get_resources_for_day(["llm_architecture", "vertex_ai_studio"])
    assert len(day_resources) >= 3
    # Check deduplication
    ids = [r.resource_id for r in day_resources]
    assert len(ids) == len(set(ids))


def test_filter_resources_by_type() -> None:
    """Test filtering catalog by resource type."""
    videos = filter_resources_by_type("video")
    assert len(videos) >= 2
    for v in videos:
        assert v.resource_type.lower() == "video"


def test_filter_resources_by_experience() -> None:
    """Test filtering catalog by experience level."""
    beginner = filter_resources_by_experience("beginner")
    assert len(beginner) >= 5
    for b in beginner:
        assert b.experience_level in ("beginner", "all")


def test_get_official_exam_resources() -> None:
    """Test retrieving only official Google resources."""
    official = get_official_exam_resources()
    assert len(official) >= 4
    for o in official:
        assert o.is_official is True
        assert "Google" in o.provider


def test_learning_resource_validation_failure() -> None:
    """Ensure Pydantic rejects invalid resources missing mandatory fields."""
    with pytest.raises(ValidationError):
        LearningResource(
            resource_id="invalid",
            # missing title, url, provider, etc.
        )  # type: ignore[call-arg]
