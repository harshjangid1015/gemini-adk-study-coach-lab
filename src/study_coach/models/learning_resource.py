"""Pydantic model for curated learning resources."""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LearningResource(BaseModel):
    """Metadata for a curated, verified learning resource."""

    resource_id: str = Field(
        ..., min_length=1, description="Unique slug for the resource"
    )
    topic_ids: list[str] = Field(
        ..., min_length=1, description="Curriculum topic IDs mapped to this resource"
    )
    title: str = Field(..., min_length=1, description="Resource title")
    provider: str = Field(
        ...,
        min_length=1,
        description="Publisher or organization providing the resource",
    )
    resource_type: Literal[
        "Official exam guide",
        "Official documentation",
        "Article",
        "Video",
        "Interactive tutorial",
        "Python example",
        "GitHub repository",
        "Sample exam questions",
    ] = Field(..., description="Category of resource")
    url: HttpUrl = Field(..., description="Direct link to the verified public resource")
    short_description: str = Field(
        ..., min_length=10, description="Concise synopsis of the content"
    )
    experience_level: Literal["beginner", "intermediate", "advanced", "all"] = Field(
        default="all", description="Target learner experience level"
    )
    estimated_minutes: int = Field(
        gt=0, description="Estimated time required in minutes"
    )
    language: str = Field(default="English", min_length=2)
    exam_domain: str = Field(
        ..., min_length=1, description="Official exam domain alignment"
    )
    requires_login: bool = Field(
        default=False, description="Whether account signup is needed"
    )
    requires_paid_access: bool = Field(
        default=False, description="Whether paid access or cloud billing is needed"
    )
    verified_at: str = Field(..., min_length=7, description="Verification date YYYY-MM")
    verification_status: Literal["verified", "unverified", "restricted"] = Field(
        default="verified", description="Resource validation status"
    )
    is_official: bool = Field(
        default=False, description="True if published directly by Google Cloud"
    )
    thumbnail_url: HttpUrl | None = Field(
        default=None,
        description="Optional verified HTTPS preview image or thumbnail URL",
    )
    tags: list[str] = Field(default_factory=list, description="Categorization keywords")

    @field_validator("topic_ids")
    @classmethod
    def validate_non_empty_topic_ids(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("topic_ids list must not be empty")
        for tid in v:
            if not tid or not tid.strip():
                raise ValueError("Topic ID cannot be empty or whitespace")
        return v
