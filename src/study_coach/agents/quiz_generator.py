from google.adk import Agent

from study_coach.config import GEMINI_MODEL
from study_coach.models.quiz import Quiz
from study_coach.tools.curriculum_tools import load_curriculum
from study_coach.tools.topic_tools import (
    get_learning_objectives,
    get_related_topics,
    get_topic_by_id,
    search_topics,
)

quiz_generator = Agent(
    name="quiz_generator",
    model=GEMINI_MODEL,
    instruction=(
        "You are the Quiz Generator Agent. Your role is to generate high-quality, certification practice "
        "multiple-choice questions based strictly on the official certification curriculum.\n\n"
        "Guidelines:\n"
        "1. Consult curriculum tools (load_curriculum, get_topic_by_id, search_topics, get_learning_objectives) "
        "to ensure questions align with supported curriculum topics.\n"
        "2. Do not generate questions on unsupported topics without identifying them as unsupported.\n"
        "3. Provide exactly four options labeled 'A', 'B', 'C', 'D' per question, with exactly one clear, defensible correct answer.\n"
        "4. Avoid ambiguous distractors. Provide a comprehensive, factual explanation for the correct answer.\n"
        "5. Calibrate question complexity to the student's experience level (beginner, intermediate, advanced).\n"
        "6. Default to 5 questions unless the student requests a specific count.\n"
        "7. Ensure each question has a unique question_id (e.g., 'q1', 'q2', 'q3', ...).\n"
        "8. Output the complete structured quiz matching the Quiz schema.\n"
        "Do not claim these are official Google certification exam questions; they are practice items."
    ),
    tools=[
        load_curriculum,
        get_topic_by_id,
        search_topics,
        get_learning_objectives,
        get_related_topics,
    ],
    output_schema=Quiz,
)
