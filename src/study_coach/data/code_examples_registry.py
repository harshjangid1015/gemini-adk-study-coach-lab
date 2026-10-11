"""Catalog and registry of curated runnable code examples."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CodeExample:
    """Metadata and code content for a topic's practical exercise."""

    example_id: str
    topic_id: str
    title: str
    description: str
    category: (
        str  # "Conceptual Simulation" or "Runnable Python" or "Gemini API Example"
    )
    code: str
    expected_output: str
    requires_credentials: bool
    requires_cloud_services: bool

    @property
    def example_type(self) -> str:
        return self.category


EXAMPLES_DIR = Path(__file__).resolve().parent / "code_examples"


def load_code_example(example_id: str) -> CodeExample | None:
    """Returns a CodeExample by its identifier."""
    return EXAMPLES_REGISTRY.get(example_id)


def get_examples_for_topic(topic_id: str) -> list[CodeExample]:
    """Returns all code examples matching a given curriculum topic."""
    return [ex for ex in EXAMPLES_REGISTRY.values() if ex.topic_id == topic_id]


get_code_examples_for_topic = get_examples_for_topic


def get_all_code_example_topics() -> list[str]:
    """Returns all unique topic IDs that have registered code examples."""
    return sorted({ex.topic_id for ex in EXAMPLES_REGISTRY.values()})


# Registry definitions
EXAMPLES_REGISTRY: dict[str, CodeExample] = {
    "tokenization_demo": CodeExample(
        example_id="tokenization_demo",
        topic_id="llm_architecture",
        title="Subword & Punctuation Tokenization Simulation",
        description="Splits an input prompt into discrete tokens and assigns simulated numerical token IDs.",
        category="Runnable Python",
        code=(EXAMPLES_DIR / "tokenization_demo.py").read_text(encoding="utf-8")
        if (EXAMPLES_DIR / "tokenization_demo.py").exists()
        else "",
        expected_output="Tokens: ['Hello', 'Vertex', 'AI', '!', 'Transformers', 'predict', 'the', 'next', 'word', '.']",
        requires_credentials=False,
        requires_cloud_services=False,
    ),
    "attention_demo": CodeExample(
        example_id="attention_demo",
        topic_id="llm_architecture",
        title="Self-Attention Scaled Dot-Product Vector Math",
        description="Calculates Softmax attention distribution between a query token and contextual key tokens.",
        category="Conceptual Simulation",
        code=(EXAMPLES_DIR / "attention_demo.py").read_text(encoding="utf-8")
        if (EXAMPLES_DIR / "attention_demo.py").exists()
        else "",
        expected_output="Attention Weights [river, money]: [0.387, 0.613]",
        requires_credentials=False,
        requires_cloud_services=False,
    ),
    "rag_simulation": CodeExample(
        example_id="rag_simulation",
        topic_id="genai_concepts",
        title="Factual Retrieval-Augmented Generation (RAG) Assembly",
        description="Searches a knowledge base for keywords and builds an augmented prompt with source attribution.",
        category="Conceptual Simulation",
        code=(EXAMPLES_DIR / "rag_simulation.py").read_text(encoding="utf-8")
        if (EXAMPLES_DIR / "rag_simulation.py").exists()
        else "",
        expected_output="Retrieved Sources: ['doc2']\nPrompt: Context Information: ...",
        requires_credentials=False,
        requires_cloud_services=False,
    ),
    "prompt_comparison": CodeExample(
        example_id="prompt_comparison",
        topic_id="vertex_ai_studio",
        title="Zero-Shot vs Few-Shot Prompt Formulation",
        description="Demonstrates constructing system instructions with few-shot demonstration input-output pairs.",
        category="Runnable Python",
        code="""def format_few_shot_prompt(task_input: str) -> str:
    examples = [
        {"input": "Classify: The quarterly revenue increased 14%", "output": "POSITIVE_BUSINESS"},
        {"input": "Classify: Server latency increased 200ms", "output": "INCIDENT_ALERT"},
    ]
    prompt_lines = ["You are an enterprise classification assistant.", ""]
    for ex in examples:
        prompt_lines.append(f"Input: {ex['input']}\\nOutput: {ex['output']}")
    prompt_lines.append(f"Input: {task_input}\\nOutput:")
    return "\\n".join(prompt_lines)

if __name__ == "__main__":
    prompt = format_few_shot_prompt("Classify: Database backup succeeded on schedule")
    print(prompt)
""",
        expected_output="You are an enterprise classification assistant.\nInput: ...\nOutput:",
        requires_credentials=False,
        requires_cloud_services=False,
    ),
}
