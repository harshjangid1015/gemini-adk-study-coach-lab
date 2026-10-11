from typing import Literal

from pydantic import BaseModel, Field, model_validator


class StudyActivity(BaseModel):
    topic_id: str
    activity_type: Literal["learning", "practice", "review"]
    description: str
    duration_minutes: int = Field(gt=0)


class StudyDay(BaseModel):
    day_number: int = Field(gt=0)
    title: str
    activities: list[StudyActivity]
    total_minutes: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total_minutes(self) -> "StudyDay":
        calc_total = sum(act.duration_minutes for act in self.activities)
        if calc_total != self.total_minutes:
            raise ValueError(
                f"total_minutes ({self.total_minutes}) does not match sum of activities ({calc_total})"
            )
        return self


class StudyPlan(BaseModel):
    certification_name: str = Field(min_length=1)
    days_until_exam: int = Field(gt=0)
    daily_study_minutes: int = Field(ge=1, le=480)
    days: list[StudyDay]
    total_planned_minutes: int = Field(ge=0)
    planning_notes: str

    @model_validator(mode="after")
    def validate_plan(self) -> "StudyPlan":
        if len(self.days) != self.days_until_exam:
            raise ValueError(
                f"Plan has {len(self.days)} days but exam is in {self.days_until_exam} days."
            )

        calc_total = 0
        expected_day_num = 1
        for day in self.days:
            if day.day_number != expected_day_num:
                raise ValueError(
                    f"Day numbers must be sequential. Expected {expected_day_num}, got {day.day_number}."
                )
            if day.total_minutes > self.daily_study_minutes:
                raise ValueError(
                    f"Day {day.day_number} exceeds daily limit of {self.daily_study_minutes} minutes."
                )
            calc_total += day.total_minutes
            expected_day_num += 1

        if calc_total != self.total_planned_minutes:
            raise ValueError(
                f"total_planned_minutes ({self.total_planned_minutes}) does not match sum of days ({calc_total})"
            )

        return self
