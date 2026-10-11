from study_coach.agent import root_agent, study_coach
from study_coach.agents.quiz_generator import quiz_generator
from study_coach.agents.study_planner import study_planner
from study_coach.agents.topic_expert import topic_expert
from study_coach.models.quiz import Quiz


def test_root_agent_exports_and_all_specialists() -> None:
    assert root_agent is study_coach
    assert root_agent.name == "study_coach"
    assert study_planner in root_agent.sub_agents
    assert topic_expert in root_agent.sub_agents
    assert quiz_generator in root_agent.sub_agents
    assert len(root_agent.sub_agents) == 3


def test_quiz_generator_configuration() -> None:
    assert quiz_generator.name == "quiz_generator"
    assert quiz_generator.output_schema is Quiz
    tool_names = [getattr(t, "__name__", str(t)) for t in quiz_generator.tools]
    assert "load_curriculum" in tool_names
    assert "get_topic_by_id" in tool_names
    assert "search_topics" in tool_names
    assert "get_learning_objectives" in tool_names
    assert "get_related_topics" in tool_names


def test_coordinator_instructions_quiz_routing() -> None:
    instruction = str(root_agent.instruction)
    assert "study_planner" in instruction
    assert "topic_expert" in instruction
    assert "quiz_generator" in instruction
    assert "Practice Quizzes" in instruction
    assert "Grading" in instruction
