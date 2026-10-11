from typing import Literal

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    experience_level: Literal["beginner", "intermediate", "advanced"]
    daily_study_minutes: int = Field(ge=1, le=480)
    learning_preferences: list[str] | None = None


class StudyRequest(BaseModel):
    certification_name: str = Field(min_length=1)
    days_until_exam: int = Field(gt=0)
    student_profile: StudentProfile
