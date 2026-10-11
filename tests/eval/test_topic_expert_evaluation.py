"""Evaluations for Topic Expert explanations, level suitability, and error handling."""

import pytest
from pydantic import ValidationError

from study_coach.models.topic_explanation import TopicExplanation
from study_coach.tools.curriculum_tools import load_curriculum


def test_topic_expert_curriculum_alignment() -> None:
    """Verify that expected topics exist in curriculum and have proper metadata."""
    curriculum = load_curriculum()
    topics = {t["id"]: t for t in curriculum["topics"]}
    assert "genai_concepts" in topics
    assert "llm_architecture" in topics
    assert "responsible_ai" in topics
    assert "vertex_ai_studio" in topics


def test_topic_expert_unknown_topic_handling_scenario_9() -> None:
    """Scenario 9: Requesting an unknown topic returns None from lookup."""
    curriculum = load_curriculum()
    topic = next(
        (
            t
            for t in curriculum["topics"]
            if t["id"] == "quantum_computing_cryptography"
        ),
        None,
    )
    assert topic is None


def test_topic_explanation_schema_contract() -> None:
    """Validate TopicExplanation Pydantic model contract and constraints."""
    data = {
        "topic_id": "genai_concepts",
        "topic_title": "Generative AI Concepts",
        "experience_level": "beginner",
        "learning_objectives": [
            "Define Generative AI.",
            "Differentiate from traditional Machine Learning.",
        ],
        "key_concepts": [
            "Generative Models",
            "Discriminative Models",
            "Foundation Models",
        ],
        "explanation": "Generative AI models create new content by learning data distributions.",
        "practical_example": "Using Vertex AI Studio to prompt Gemini for summarization.",
        "common_misconceptions": ["Generative AI and predictive AI work identically."],
        "comprehension_questions": [
            "What distinguishes generative from predictive models?",
            "What is a foundation model?",
        ],
        "source_references": ["https://cloud.google.com/vertex-ai/docs"],
    }
    explanation = TopicExplanation.model_validate(data)
    assert explanation.topic_id == "genai_concepts"
    assert len(explanation.key_concepts) >= 3
    assert len(explanation.learning_objectives) >= 2
    assert len(explanation.comprehension_questions) >= 2


def test_topic_explanation_rejects_missing_required_fields() -> None:
    """Ensure incomplete explanations fail schema validation."""
    with pytest.raises(ValidationError):
        TopicExplanation.model_validate({"topic_id": "genai_concepts"})
