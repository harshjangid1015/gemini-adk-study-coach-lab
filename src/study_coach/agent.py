from google.adk import Agent

from study_coach.agents.study_planner import study_planner
from study_coach.config import GEMINI_MODEL

root_agent = Agent(
    name="study_coach",
    model=GEMINI_MODEL,
    instruction=(
        "You are an AI Study Coach helping students prepare for technical certifications. "
        "Greet the student. "
        "Ask about their certification goal, days remaining, and daily study availability. "
        "When the student requests a study plan, delegate to the study_planner agent. "
        "Return the generated plan to the user. "
        "Explain that quizzes and deep topic explanations are not yet implemented. "
        "Do not claim that quizzes or deep topic explanations already work."
    ),
    sub_agents=[study_planner],
)

study_coach = root_agent
