"""Unit tests for Lesson Visuals Service."""

from study_coach.services.lesson_visuals import (
    LessonDiagram,
    get_all_diagram_topics,
    get_diagram_for_topic,
)


def test_get_diagram_for_supported_topics() -> None:
    """Ensure all registered topics return valid LessonDiagram instances."""
    topics = get_all_diagram_topics()
    assert "llm_architecture" in topics
    assert "genai_concepts" in topics
    assert "responsible_ai" in topics
    assert "vertex_ai_studio" in topics

    for t in topics:
        diagram = get_diagram_for_topic(t)
        assert isinstance(diagram, LessonDiagram)
        assert diagram.topic_id == t
        assert len(diagram.title) > 0
        assert "graph TD" in diagram.mermaid_code or "graph LR" in diagram.mermaid_code
        assert len(diagram.text_alternative) > 0
        assert len(diagram.components) > 0


def test_get_diagram_unknown_topic() -> None:
    """Ensure unknown topic returns None safely."""
    diagram = get_diagram_for_topic("unknown_nonexistent_topic")
    assert diagram is None


def test_transformer_diagram_structure() -> None:
    """Verify specific structure and components of Transformer architecture diagram."""
    diagram = get_diagram_for_topic("llm_architecture")
    assert diagram is not None
    assert "Tokenization" in diagram.components
    assert "Self-Attention Mechanism" in diagram.components
    assert "Text" in diagram.input_spec
    assert "probability" in diagram.output_spec.lower()
