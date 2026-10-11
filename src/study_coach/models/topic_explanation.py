from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from study_coach.tools.curriculum_tools import load_curriculum


class TopicExplanation(BaseModel):
    """Structured explanation of a technical certification topic."""

    topic_id: str = Field(
        ...,
        description="The unique identifier of the curriculum topic (e.g. 'genai_concepts', 'llm_architecture').",
    )
    topic_title: str = Field(
        ...,
        min_length=1,
        description="The title of the topic being explained.",
    )
    experience_level: Literal["beginner", "intermediate", "advanced"] = Field(
        ...,
        description="Target student experience level adapting the explanation depth.",
    )
    learning_objectives: list[str] = Field(
        ...,
        min_length=1,
        description="Core learning objectives addressed by this explanation.",
    )
    key_concepts: list[str] = Field(
        ...,
        min_length=1,
        description="Key terms, concepts, and foundational vocabulary.",
    )
    explanation: str = Field(
        ...,
        min_length=10,
        description="In-depth conceptual explanation adapted to the target experience level.",
    )
    practical_example: str = Field(
        ...,
        min_length=10,
        description="Real-world practical Google Cloud architecture, service, or business scenario example.",
    )
    common_misconceptions: list[str] = Field(
        ...,
        min_length=1,
        description="Common pitfalls, mistakes, or misconceptions regarding this topic.",
    )
    related_topics: list[str] = Field(
        default_factory=list,
        description="Valid topic IDs related to this topic or serving as prerequisites.",
    )
    comprehension_questions: list[str] = Field(
        ...,
        min_length=1,
        description="Short comprehension check questions for self-assessment.",
    )
    source_references: list[str] = Field(
        ...,
        min_length=1,
        description="Curriculum documentation sources or Google Cloud documentation references.",
    )

    @field_validator(
        "learning_objectives",
        "key_concepts",
        "common_misconceptions",
        "comprehension_questions",
        "source_references",
    )
    @classmethod
    def validate_non_empty_items(cls, items: list[str]) -> list[str]:
        if not items:
            raise ValueError("List must contain at least one item")
        for item in items:
            if not item or not item.strip():
                raise ValueError("List items cannot be empty strings")
        return items

    @field_validator("explanation", "practical_example")
    @classmethod
    def validate_text_content(cls, val: str) -> str:
        if not val or not val.strip():
            raise ValueError("Explanation fields must not be empty or blank")
        return val.strip()

    @model_validator(mode="after")
    def validate_topic_references(self) -> "TopicExplanation":
        try:
            curriculum = load_curriculum()
        except (FileNotFoundError, TypeError, ValueError):
            return self

        valid_topic_ids = {t["id"] for t in curriculum.get("topics", [])}

        if self.topic_id not in valid_topic_ids:
            raise ValueError(
                f"Unknown topic_id '{self.topic_id}'. Must be one of {sorted(valid_topic_ids)}"
            )

        for rel in self.related_topics:
            if rel not in valid_topic_ids:
                raise ValueError(
                    f"Invalid related_topic '{rel}'. Must be one of {sorted(valid_topic_ids)}"
                )

        return self
