"""Deterministic tools for querying and filtering the curated learning resource catalog."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from study_coach.models.learning_resource import LearningResource

CATALOG_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "learning_resources.yaml"
)


@lru_cache(maxsize=1)
def load_learning_resources() -> list[LearningResource]:
    """Loads and validates all resources from the YAML catalog using Pydantic."""
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Learning resource catalog not found at {CATALOG_PATH}"
        )

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)

    raw_list: list[dict[str, Any]] = data.get("resources", [])
    seen_ids: set[str] = set()
    resources: list[LearningResource] = []

    for item in raw_list:
        res = LearningResource.model_validate(item)
        if res.resource_id in seen_ids:
            raise ValueError(
                f"Duplicate resource_id detected in catalog: '{res.resource_id}'"
            )
        seen_ids.add(res.resource_id)
        resources.append(res)

    return resources


def get_resources_for_topic(
    topic_id: str,
    experience_level: str | None = None,
) -> list[LearningResource]:
    """Retrieves all resources that cover a specified curriculum topic ID."""
    all_resources = load_learning_resources()
    results: list[LearningResource] = []

    for res in all_resources:
        if topic_id in res.topic_ids:
            if experience_level and res.experience_level not in (
                experience_level,
                "all",
            ):
                continue
            results.append(res)

    return results


def get_resources_for_day(
    topic_ids: list[str],
    max_minutes: int | None = None,
    experience_level: str | None = None,
) -> list[LearningResource]:
    """Matches resources to a study day's topic list, optionally constrained by study budget."""
    all_resources = load_learning_resources()
    matched: list[LearningResource] = []
    seen: set[str] = set()

    for tid in topic_ids:
        for res in all_resources:
            if tid in res.topic_ids and res.resource_id not in seen:
                if experience_level and res.experience_level not in (
                    experience_level,
                    "all",
                ):
                    continue
                seen.add(res.resource_id)
                matched.append(res)

    if max_minutes is not None:
        # Return resources that fit within or closest to the allocated activity time
        return [r for r in matched if r.estimated_minutes <= max_minutes]

    return matched


def filter_resources_by_type(
    resource_type: str,
    topic_id: str | None = None,
) -> list[LearningResource]:
    """Filters resources by their content type (Video, Article, Official documentation, etc.)."""
    all_resources = load_learning_resources()
    return [
        r
        for r in all_resources
        if r.resource_type.lower() == resource_type.lower()
        and (topic_id is None or topic_id in r.topic_ids)
    ]


def filter_resources_by_experience(
    experience_level: str,
) -> list[LearningResource]:
    """Filters resources by experience level (beginner, intermediate, advanced, or all)."""
    all_resources = load_learning_resources()
    return [r for r in all_resources if r.experience_level in (experience_level, "all")]


def get_official_exam_resources() -> list[LearningResource]:
    """Returns strictly official Google Cloud resources."""
    all_resources = load_learning_resources()
    return [r for r in all_resources if r.is_official]
