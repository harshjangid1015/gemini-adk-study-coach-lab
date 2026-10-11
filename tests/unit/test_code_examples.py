"""Unit tests for Code Examples Registry and Python Demos."""

import subprocess
import sys
from pathlib import Path

from study_coach.data.code_examples.attention_demo import attention_demo
from study_coach.data.code_examples.rag_simulation import rag_simulation_demo
from study_coach.data.code_examples.tokenization_demo import tokenization_demo
from study_coach.data.code_examples_registry import (
    get_all_code_example_topics,
    get_code_examples_for_topic,
)


def test_registry_has_supported_topics() -> None:
    """Ensure registry indexes topics with code examples."""
    topics = get_all_code_example_topics()
    assert "llm_architecture" in topics
    assert "genai_concepts" in topics

    arch_examples = get_code_examples_for_topic("llm_architecture")
    assert len(arch_examples) == 2
    example_ids = [e.example_id for e in arch_examples]
    assert "tokenization_demo" in example_ids
    assert "attention_demo" in example_ids

    genai_examples = get_code_examples_for_topic("genai_concepts")
    assert len(genai_examples) == 1
    assert genai_examples[0].example_id == "rag_simulation"


def test_tokenization_demo_direct_execution() -> None:
    """Run tokenization demo directly in-process."""
    tokens = tokenization_demo("Hello, Generative AI!")
    assert tokens == ["hello", ",", "generative", "ai", "!"]


def test_attention_demo_direct_execution() -> None:
    """Run self-attention demo directly in-process."""
    weights = attention_demo()
    assert len(weights) == 3
    # Softmax rows sum to approx 1.0 (with 3-decimal rounding)
    for row in weights:
        assert abs(sum(row) - 1.0) < 0.01


def test_rag_simulation_direct_execution() -> None:
    """Run RAG retrieval demo directly in-process."""
    result = rag_simulation_demo()
    assert "Retrieved Knowledge" in result
    assert "Grounding in facts" in result


def test_code_examples_isolated_subprocess() -> None:
    """Verify that all example script files run cleanly as standalone scripts in isolated Python subprocesses."""
    code_dir = (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "study_coach"
        / "data"
        / "code_examples"
    )
    scripts = ["tokenization_demo.py", "attention_demo.py", "rag_simulation.py"]

    for script in scripts:
        script_path = code_dir / script
        assert script_path.exists(), f"Script {script} must exist"
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        assert proc.returncode == 0
        assert len(proc.stdout) > 0
