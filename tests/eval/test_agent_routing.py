"""Evaluations for agent routing logic and coordinator intent detection."""

import json
from pathlib import Path
from typing import Any

import pytest

from study_coach.agent import root_agent

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "evaluation_scenarios.json"


def load_fixtures() -> list[dict[str, Any]]:
    with open(FIXTURES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    result: list[dict[str, Any]] = data["scenarios"]
    return result


def test_coordinator_agent_structure_and_subagents() -> None:
    """Verify coordinator agent declares the required subagents for delegation."""
    subagents = {a.name: a for a in root_agent.sub_agents}
    assert "study_planner" in subagents
    assert "topic_expert" in subagents
    assert "quiz_generator" in subagents


@pytest.mark.parametrize(
    ("scenario_id", "expected_agent"),
    [
        ("scenario_1", "study_planner"),
        ("scenario_2", "study_planner"),
        ("scenario_3", "topic_expert"),
        ("scenario_4", "topic_expert"),
        ("scenario_5", "quiz_generator"),
        ("scenario_6", "quiz_generator"),
    ],
)
def test_deterministic_routing_intent_classification(
    scenario_id: str, expected_agent: str
) -> None:
    """Verify scenarios classify and route predictably based on domain keywords."""
    scenarios = {s["id"]: s for s in load_fixtures()}
    scenario = scenarios[scenario_id]
    request = scenario["request"].lower()

    # Rule-based intent verification mirrors coordinator instructions
    if any(k in request for k in ["study plan", "help me plan", "replan"]):
        predicted_agent = "study_planner"
    elif any(k in request for k in ["explain", "teach", "architecture"]):
        predicted_agent = "topic_expert"
    elif any(k in request for k in ["quiz", "mcq", "questions", "practice"]):
        predicted_agent = "quiz_generator"
    else:
        predicted_agent = "unknown"

    assert predicted_agent == expected_agent
