import pytest

from study_coach.tools.topic_tools import (
    get_learning_objectives,
    get_related_topics,
    get_topic_by_id,
    search_topics,
)


def test_get_topic_by_id_success() -> None:
    topic = get_topic_by_id("genai_concepts")
    assert topic is not None
    assert topic["id"] == "genai_concepts"
    assert "title" in topic
    assert topic["title"] == "Generative AI Concepts"
    assert len(topic["learning_objectives"]) >= 1


def test_get_topic_by_id_unknown() -> None:
    topic = get_topic_by_id("non_existent_topic")
    assert topic is None


def test_search_topics_by_keyword() -> None:
    # Search by title/description keyword
    results = search_topics("transformer")
    assert len(results) >= 1
    assert any(t["id"] == "llm_architecture" for t in results)

    # Search by category keyword
    results_gov = search_topics("governance")
    assert len(results_gov) >= 1
    assert any(t["id"] == "responsible_ai" for t in results_gov)


def test_search_topics_empty_or_no_match() -> None:
    assert search_topics("") == []
    assert search_topics("completely_random_query_that_never_matches") == []


def test_get_learning_objectives_valid() -> None:
    objectives = get_learning_objectives("genai_concepts")
    assert isinstance(objectives, list)
    assert len(objectives) > 0
    assert any("Generative AI" in obj for obj in objectives)


def test_get_learning_objectives_invalid() -> None:
    with pytest.raises(ValueError, match="Topic not found"):
        get_learning_objectives("unknown_topic_xyz")


def test_get_related_topics() -> None:
    # genai_concepts may have related topics or empty list
    related = get_related_topics("genai_concepts")
    assert isinstance(related, list)

    with pytest.raises(ValueError, match="Topic not found"):
        get_related_topics("unknown_topic_xyz")
