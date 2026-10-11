from study_coach.agent import study_coach
from study_coach.agents.study_planner import study_planner


def test_study_planner_imports_correctly() -> None:
    assert study_planner.name == "study_planner"
    assert study_coach.name == "study_coach"


def test_study_coach_delegates() -> None:
    assert study_planner in study_coach.sub_agents
