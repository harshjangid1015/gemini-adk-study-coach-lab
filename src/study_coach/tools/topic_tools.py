from typing import Any

from study_coach.tools.curriculum_tools import load_curriculum


def get_topic_by_id(topic_id: str) -> dict[str, Any] | None:
    """Retrieves a curriculum topic by its ID. Returns None if not found."""
    curriculum = load_curriculum()
    topics = curriculum.get("topics", [])
    if isinstance(topics, list):
        for topic in topics:
            if isinstance(topic, dict) and topic.get("id") == topic_id:
                return dict(topic)
    return None


def search_topics(keyword: str) -> list[dict[str, Any]]:
    """Searches local curriculum topics by keyword in id, title, description, or learning objectives."""
    if not keyword:
        return []
    kw = keyword.lower().strip()
    curriculum = load_curriculum()
    matches: list[dict[str, Any]] = []
    for topic in curriculum.get("topics", []):
        # Search topic fields
        searchable_text = " ".join(
            [
                topic.get("id", ""),
                topic.get("title", ""),
                topic.get("description", ""),
                topic.get("category", ""),
                " ".join(topic.get("learning_objectives", [])),
                " ".join(topic.get("prerequisites", [])),
                " ".join(topic.get("related_topics", [])),
            ]
        ).lower()
        if kw in searchable_text:
            matches.append(topic)
    return matches


def get_learning_objectives(topic_id: str) -> list[str]:
    """Retrieves the list of learning objectives for a given topic ID."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise ValueError(f"Topic not found: {topic_id}")
    return list(topic.get("learning_objectives", []))


def get_related_topics(topic_id: str) -> list[str]:
    """Retrieves prerequisites and related topic IDs for a given topic ID."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise ValueError(f"Topic not found: {topic_id}")
    rel = list(topic.get("related_topics", []))
    prereqs = list(topic.get("prerequisites", []))
    # Deduplicate while preserving order
    combined: list[str] = []
    for t in prereqs + rel:
        if t not in combined:
            combined.append(t)
    return combined
