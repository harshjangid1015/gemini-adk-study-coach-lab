from pathlib import Path
from typing import Any

import yaml

CURRICULUM_FILE = (
    Path(__file__).parent.parent / "data" / "google_cloud_genai_leader.yaml"
)


def load_curriculum() -> dict[str, Any]:
    """Loads the certification curriculum from the yaml file."""
    if not CURRICULUM_FILE.exists():
        raise FileNotFoundError(f"Curriculum file not found: {CURRICULUM_FILE}")
    with open(CURRICULUM_FILE, "r") as f:
        data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise TypeError("Curriculum data must be a dictionary")
        if "topics" not in data:
            raise ValueError("Curriculum missing 'topics' key")
        return data
