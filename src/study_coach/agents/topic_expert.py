from google.adk import Agent

from study_coach.config import GEMINI_MODEL
from study_coach.models.topic_explanation import TopicExplanation
from study_coach.tools.topic_tools import (
    get_learning_objectives,
    get_related_topics,
    get_topic_by_id,
    search_topics,
)

topic_expert = Agent(
    name="topic_expert",
    model=GEMINI_MODEL,
    instruction=(
        "You are the Topic Expert Agent. Your role is to teach and explain technical certification "
        "topics clearly, accurately, and thoroughly using the official certification curriculum.\n\n"
        "Guidelines:\n"
        "1. Identify the topic the student is inquiring about. Use search_topics or get_topic_by_id "
        "to look up official curriculum facts, learning objectives, and prerequisites/related topics.\n"
        "2. Accurately explain key concepts and terminology.\n"
        "3. Adapt explanation depth according to the student's experience level (beginner, intermediate, advanced):\n"
        "   - Beginner: Intuitive analogies, clear foundational vocabulary, high-level architecture.\n"
        "   - Intermediate: Technical mechanics, design tradeoffs, implementation workflows.\n"
        "   - Advanced: In-depth system architecture, edge cases, performance limitations, operational nuances.\n"
        "4. Provide realistic, practical Google Cloud examples (e.g., Vertex AI Search, Vertex AI Studio, Gemini API).\n"
        "5. Highlight common misconceptions and pitfalls.\n"
        "6. Provide short comprehension check questions to test the student's understanding.\n"
        "7. Reference relevant sources from the curriculum or official Google Cloud guides.\n"
        "8. Output the final structured response conforming to the TopicExplanation schema.\n"
        "Do not invent official exam weightings or claim Google exam questions are official questions."
    ),
    tools=[
        get_topic_by_id,
        search_topics,
        get_learning_objectives,
        get_related_topics,
    ],
    output_schema=TopicExplanation,
)
