from google.adk import Agent

from study_coach.config import GEMINI_MODEL
from study_coach.models.study_plan import StudyPlan
from study_coach.tools.curriculum_tools import load_curriculum
from study_coach.tools.planning_tools import calculate_available_minutes

study_planner = Agent(
    name="study_planner",
    model=GEMINI_MODEL,
    instruction=(
        "You are the Study Planner Agent. Your job is to create structured study plans for students "
        "preparing for technical certifications.\n"
        "To do this:\n"
        "1. Understand the certification goals.\n"
        "2. Read the certification curriculum.\n"
        "3. Consider their experience level and days remaining.\n"
        "4. Respect their daily study minutes limit.\n"
        "5. Produce a structured study plan.\n"
        "Make sure day numbers are sequential and each activity uses a valid topic id from the curriculum."
    ),
    tools=[load_curriculum, calculate_available_minutes],
    output_schema=StudyPlan,
)
