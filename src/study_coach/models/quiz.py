from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from study_coach.tools.curriculum_tools import load_curriculum


class QuizQuestion(BaseModel):
    """A multiple-choice certification practice question."""

    question_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the question (e.g., 'q1', 'q_genai_01').",
    )
    topic_id: str = Field(
        ...,
        min_length=1,
        description="Curriculum topic ID this question assesses.",
    )
    question_text: str = Field(
        ...,
        min_length=10,
        description="The scenario or question prompt text.",
    )
    options: dict[Literal["A", "B", "C", "D"], str] = Field(
        ...,
        description="Dictionary mapping exactly keys 'A', 'B', 'C', 'D' to option text.",
    )
    correct_answer: Literal["A", "B", "C", "D"] = Field(
        ...,
        description="The single correct answer key ('A', 'B', 'C', or 'D').",
    )
    explanation: str = Field(
        ...,
        min_length=10,
        description="Detailed factual explanation justifying the correct answer and addressing distractors.",
    )
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        ...,
        description="Target difficulty level of the question.",
    )

    @field_validator("options")
    @classmethod
    def validate_options(
        cls, v: dict[Literal["A", "B", "C", "D"], str]
    ) -> dict[Literal["A", "B", "C", "D"], str]:
        expected_keys = {"A", "B", "C", "D"}
        if set(v.keys()) != expected_keys:
            raise ValueError(
                f"Question options must contain exactly keys A, B, C, D; got {sorted(v.keys())}"
            )
        for opt_key, opt_text in v.items():
            if not opt_text or not opt_text.strip():
                raise ValueError(f"Option {opt_key} text cannot be empty or blank")
        # Ensure options are distinct
        cleaned_values = [text.strip().lower() for text in v.values()]
        if len(set(cleaned_values)) != len(cleaned_values):
            raise ValueError(
                "All four options must be distinct; duplicate options found"
            )
        return v

    @model_validator(mode="after")
    def validate_topic_and_answer(self) -> "QuizQuestion":
        if self.correct_answer not in self.options:
            raise ValueError(
                f"correct_answer '{self.correct_answer}' is not among available options: {list(self.options.keys())}"
            )

        try:
            curriculum = load_curriculum()
            valid_topic_ids = {t["id"] for t in curriculum.get("topics", [])}
            if self.topic_id not in valid_topic_ids:
                raise ValueError(
                    f"Unknown topic_id '{self.topic_id}'. Must be one of {sorted(valid_topic_ids)}"
                )
        except (FileNotFoundError, TypeError, ValueError) as err:
            if "Unknown topic_id" in str(err):
                raise

        return self


class StudentQuizQuestion(BaseModel):
    """Student-facing presentation of a question without answer key or private explanation."""

    question_id: str
    topic_id: str
    question_text: str
    options: dict[Literal["A", "B", "C", "D"], str]
    difficulty: Literal["beginner", "intermediate", "advanced"]


class Quiz(BaseModel):
    """Complete generated quiz containing questions and answer key."""

    certification_name: str = Field(
        ...,
        min_length=1,
        description="Target technical certification.",
    )
    topic_ids: list[str] = Field(
        ...,
        min_length=1,
        description="List of curriculum topic IDs covered by this quiz.",
    )
    experience_level: Literal["beginner", "intermediate", "advanced"] = Field(
        ...,
        description="Target experience level of the student.",
    )
    questions: list[QuizQuestion] = Field(
        ...,
        min_length=1,
        description="List of multiple choice quiz questions.",
    )

    @model_validator(mode="after")
    def validate_quiz_structure(self) -> "Quiz":
        if not self.questions:
            raise ValueError("Quiz must contain at least one question")

        q_ids = [q.question_id for q in self.questions]
        if len(set(q_ids)) != len(q_ids):
            raise ValueError("Quiz question IDs must be unique; duplicate ID found")

        try:
            curriculum = load_curriculum()
            valid_topic_ids = {t["id"] for t in curriculum.get("topics", [])}
            for tid in self.topic_ids:
                if tid not in valid_topic_ids:
                    raise ValueError(
                        f"Unknown topic_id '{tid}' in quiz topic_ids. Must be one of {sorted(valid_topic_ids)}"
                    )
        except (FileNotFoundError, TypeError, ValueError) as err:
            if "Unknown topic_id" in str(err):
                raise

        return self

    def to_student_view(self) -> list[StudentQuizQuestion]:
        """Returns student-facing questions stripped of correct answers and private explanations."""
        return [
            StudentQuizQuestion(
                question_id=q.question_id,
                topic_id=q.topic_id,
                question_text=q.question_text,
                options=q.options,
                difficulty=q.difficulty,
            )
            for q in self.questions
        ]


class QuizSubmission(BaseModel):
    """Student submitted answers for evaluation."""

    quiz_id: str = Field(
        default="default_quiz",
        description="Identifier of the quiz being evaluated.",
    )
    student_answers: dict[str, Literal["A", "B", "C", "D"]] = Field(
        ...,
        description="Dictionary mapping question_id to student chosen option ('A', 'B', 'C', 'D').",
    )


class QuestionFeedback(BaseModel):
    """Detailed feedback for a single question evaluation."""

    question_id: str
    topic_id: str
    student_answer: str | None
    correct_answer: str
    is_correct: bool
    explanation: str


class QuizResult(BaseModel):
    """Deterministic grading evaluation summary for a submitted quiz."""

    total_questions: int = Field(ge=0)
    correct_answers: int = Field(ge=0)
    score_percentage: float = Field(ge=0.0, le=100.0)
    question_feedback: list[QuestionFeedback]
    weak_topics: list[str] = Field(
        default_factory=list,
        description="Topics where student scored below mastery threshold (e.g., < 70%).",
    )
    strong_topics: list[str] = Field(
        default_factory=list,
        description="Topics where student scored at or above mastery threshold.",
    )
