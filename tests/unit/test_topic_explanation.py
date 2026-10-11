import pytest
from pydantic import ValidationError

from study_coach.models.topic_explanation import TopicExplanation


def test_valid_beginner_explanation() -> None:
    data = {
        "topic_id": "genai_concepts",
        "topic_title": "Generative AI Concepts",
        "experience_level": "beginner",
        "learning_objectives": ["Define Generative AI", "Differentiate from ML"],
        "key_concepts": ["Generative AI", "Deep Learning", "Prompting"],
        "explanation": "Generative AI is a subset of deep learning focused on generating new content.",
        "practical_example": "Using Vertex AI Studio to generate marketing copy drafts for a campaign.",
        "common_misconceptions": ["GenAI understands facts like a conscious human."],
        "related_topics": ["llm_architecture"],
        "comprehension_questions": [
            "What is the primary difference between ML and GenAI?"
        ],
        "source_references": [
            "Google Cloud Generative AI Leader Certification Exam Guide"
        ],
    }
    explanation = TopicExplanation.model_validate(data)
    assert explanation.topic_id == "genai_concepts"
    assert explanation.experience_level == "beginner"
    assert len(explanation.comprehension_questions) == 1


def test_valid_advanced_explanation() -> None:
    data = {
        "topic_id": "llm_architecture",
        "topic_title": "Large Language Models (LLMs)",
        "experience_level": "advanced",
        "learning_objectives": ["Understand the transformer architecture"],
        "key_concepts": ["Self-Attention", "Rotary Position Embeddings", "KV Cache"],
        "explanation": (
            "Transformers rely on multi-head attention mechanisms to parallelize "
            "token representation calculations across sequence dimensions."
        ),
        "practical_example": "Deploying fine-tuned models on Vertex AI Endpoints with vLLM acceleration.",
        "common_misconceptions": ["Attention requires recurrent sequential unrolling."],
        "related_topics": ["genai_concepts", "vertex_ai_studio"],
        "comprehension_questions": [
            "How does KV caching optimize autoregressive token generation?"
        ],
        "source_references": [
            "Google Cloud Architecture Center: Generative AI on Vertex AI"
        ],
    }
    explanation = TopicExplanation.model_validate(data)
    assert explanation.experience_level == "advanced"
    assert len(explanation.related_topics) == 2


def test_invalid_experience_level() -> None:
    data = {
        "topic_id": "genai_concepts",
        "topic_title": "Generative AI Concepts",
        "experience_level": "expert",  # Invalid, only beginner, intermediate, advanced allowed
        "learning_objectives": ["Obj 1"],
        "key_concepts": ["Concept 1"],
        "explanation": "A valid explanation that is long enough.",
        "practical_example": "A valid practical example on GCP.",
        "common_misconceptions": ["Misconception 1"],
        "comprehension_questions": ["Question 1?"],
        "source_references": ["Google Cloud Guide"],
    }
    with pytest.raises(ValidationError):
        TopicExplanation.model_validate(data)


def test_empty_explanation_rejected() -> None:
    data = {
        "topic_id": "genai_concepts",
        "topic_title": "Generative AI Concepts",
        "experience_level": "beginner",
        "learning_objectives": ["Obj 1"],
        "key_concepts": ["Concept 1"],
        "explanation": "   ",  # Blank
        "practical_example": "A valid practical example on GCP.",
        "common_misconceptions": ["Misconception 1"],
        "comprehension_questions": ["Question 1?"],
        "source_references": ["Google Cloud Guide"],
    }
    with pytest.raises(ValidationError):
        TopicExplanation.model_validate(data)


def test_unknown_topic_id_rejected() -> None:
    data = {
        "topic_id": "unknown_future_topic_42",
        "topic_title": "Unknown Topic",
        "experience_level": "beginner",
        "learning_objectives": ["Obj 1"],
        "key_concepts": ["Concept 1"],
        "explanation": "A sufficiently long explanation string for testing.",
        "practical_example": "A valid practical example on GCP.",
        "common_misconceptions": ["Misconception 1"],
        "comprehension_questions": ["Question 1?"],
        "source_references": ["Google Cloud Guide"],
    }
    with pytest.raises(ValidationError, match="Unknown topic_id"):
        TopicExplanation.model_validate(data)


def test_invalid_related_topic_rejected() -> None:
    data = {
        "topic_id": "genai_concepts",
        "topic_title": "Generative AI Concepts",
        "experience_level": "beginner",
        "learning_objectives": ["Obj 1"],
        "key_concepts": ["Concept 1"],
        "explanation": "A valid explanation with enough length.",
        "practical_example": "A valid practical example on GCP.",
        "common_misconceptions": ["Misconception 1"],
        "related_topics": ["fake_nonexistent_topic"],
        "comprehension_questions": ["Question 1?"],
        "source_references": ["Google Cloud Guide"],
    }
    with pytest.raises(ValidationError, match="Invalid related_topic"):
        TopicExplanation.model_validate(data)


def test_empty_list_fields_rejected() -> None:
    data = {
        "topic_id": "genai_concepts",
        "topic_title": "Generative AI Concepts",
        "experience_level": "beginner",
        "learning_objectives": [],  # Empty list
        "key_concepts": ["Concept 1"],
        "explanation": "A valid explanation that meets minimum length.",
        "practical_example": "A valid practical example on GCP.",
        "common_misconceptions": ["Misconception 1"],
        "comprehension_questions": ["Question 1?"],
        "source_references": ["Google Cloud Guide"],
    }
    with pytest.raises(ValidationError):
        TopicExplanation.model_validate(data)
