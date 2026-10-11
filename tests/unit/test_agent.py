from study_coach.agent import study_coach


def test_agent_import() -> None:
    assert study_coach is not None
    assert study_coach.name == "study_coach"
