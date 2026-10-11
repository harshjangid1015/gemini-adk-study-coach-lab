from study_coach.agent import root_agent, study_coach
from study_coach.agents.study_planner import study_planner
from study_coach.agents.topic_expert import topic_expert
from study_coach.models.topic_explanation import TopicExplanation


def test_root_agent_exports_and_subagents() -> None:
    assert root_agent is study_coach
    assert root_agent.name == "study_coach"
    assert study_planner in root_agent.sub_agents
    assert topic_expert in root_agent.sub_agents
    assert len(root_agent.sub_agents) >= 2


def test_topic_expert_configuration() -> None:
    assert topic_expert.name == "topic_expert"
    assert topic_expert.output_schema is TopicExplanation
    tool_names = [getattr(t, "__name__", str(t)) for t in topic_expert.tools]
    assert "get_topic_by_id" in tool_names
    assert "search_topics" in tool_names
    assert "get_learning_objectives" in tool_names
    assert "get_related_topics" in tool_names


def test_coordinator_instructions_routing() -> None:
    instruction = str(root_agent.instruction)
    assert "study_planner" in instruction
    assert "topic_expert" in instruction
    assert "Explain" in instruction
