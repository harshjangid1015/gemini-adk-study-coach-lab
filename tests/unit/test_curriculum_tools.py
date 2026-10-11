from study_coach.tools.curriculum_tools import load_curriculum


def test_load_curriculum() -> None:
    data = load_curriculum()
    assert "topics" in data
    assert len(data["topics"]) > 0
    assert data["topics"][0]["id"] == "genai_concepts"
