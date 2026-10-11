"""Declarative and validated visual diagrams for curriculum topics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LessonDiagram:
    """Validated diagram metadata and visual representations."""

    topic_id: str
    title: str
    description: str
    mermaid_code: str
    text_alternative: str
    input_spec: str
    output_spec: str
    components: dict[str, str]


DIAGRAM_CATALOG: dict[str, LessonDiagram] = {
    "llm_architecture": LessonDiagram(
        topic_id="llm_architecture",
        title="Transformer Inference & Autoregressive Decoding Flow",
        description="The architectural sequence from raw text input to next-token probability distribution.",
        mermaid_code="""graph TD
    Input["Input Text Prompt ('The quick brown...')"] --> Tokenizer["Tokenization (Subword BPE / SentencePiece)"]
    Tokenizer --> TokenIDs["Token IDs [1524, 892, 341]"]
    TokenIDs --> Embedding["Token Embeddings + Positional Encoding"]
    Embedding --> Blocks["Transformer Blocks (Self-Attention & Feed-Forward Layers)"]
    Blocks --> Norm["Layer Normalization"]
    Norm --> Projection["Linear Output Projection (Vocabulary Dimension)"]
    Projection --> Softmax["Softmax (Next-Token Probabilities)"]
    Softmax --> Sampling["Token Sampling (Temperature, Top-P, Top-K)"]
    Sampling --> Output["Predicted Next Token ('fox')"]""",
        text_alternative=(
            "1. Input Prompt -> 2. Subword Tokenization -> 3. Token Embeddings + Positional Information -> "
            "4. Multi-Head Self-Attention & Feed-Forward Blocks -> 5. Output Projection -> "
            "6. Softmax Next Token Probabilities -> 7. Next Token Generation."
        ),
        input_spec="Text Prompt string",
        output_spec="Next token string or probability distribution",
        components={
            "Tokenization": "Splits text strings into discrete numerical tokens (BPE/SentencePiece).",
            "Token Embeddings": "Maps tokens into high-dimensional semantic vector spaces.",
            "Positional Information": "Adds sequential ordering signals to tokens since Transformers process tokens concurrently.",
            "Self-Attention Mechanism": "Calculates contextual relationships and dependencies across all tokens simultaneously.",
            "Feed-Forward Blocks": "Applies non-linear transformations and feature extraction per token.",
            "Output Projection & Softmax": "Projects hidden dimensions to vocabulary size and normalizes into probabilities.",
        },
    ),
    "genai_concepts": LessonDiagram(
        topic_id="genai_concepts",
        title="Retrieval-Augmented Generation (RAG) & Grounding Pipeline",
        description="How generative models use enterprise factual grounding to minimize hallucinations.",
        mermaid_code="""graph LR
    UserQuery["User Query"] --> Search["Vertex AI Search / Enterprise Vector DB"]
    Search --> DocRetrieval["Retrieve Relevant Passages (Grounding Context)"]
    UserQuery --> ContextMerge["Augmented Prompt Assembly"]
    DocRetrieval --> ContextMerge
    ContextMerge --> LLM["Gemini Foundation Model"]
    LLM --> GroundedResponse["Grounded Fact-Checked Response + Citations"]""",
        text_alternative=(
            "1. User Query -> 2. Vector DB / Search Retrieval -> 3. Retrieve Relevant Facts -> "
            "4. Assemble Augmented Prompt (Query + Context) -> 5. Gemini Generation -> "
            "6. Factual Grounded Response with Source Citations."
        ),
        input_spec="User prompt question requiring enterprise domain knowledge",
        output_spec="Factual response grounded in verified enterprise documents with citations",
        components={
            "Vertex AI Search": "Enterprise indexing and semantic vector retrieval system.",
            "Grounding Passages": "Top factual chunks retrieved to ground the generative response.",
            "Prompt Augmentation": "Combines original query with factual context and system guidelines.",
            "Gemini Model": "Generates natural language response strictly adhering to provided facts.",
        },
    ),
    "responsible_ai": LessonDiagram(
        topic_id="responsible_ai",
        title="Google Responsible AI Safety & Moderation Lifecycle",
        description="Multi-layered safety evaluations, content filtering, and bias auditing.",
        mermaid_code="""graph TD
    Prompt["User Input"] --> InputFilter["Safety & Policy Classifier (Hate, Harassment, PII)"]
    InputFilter -->|Allowed| FoundationModel["Gemini Model Reasoning"]
    InputFilter -->|Violation| BlockedInput["Safe Rejection / Canned Error"]
    FoundationModel --> OutputFilter["Harm Evaluation & Attribution Check"]
    OutputFilter -->|Safe & Grounded| Student["Audited Safe Output"]
    OutputFilter -->|Unsafe| BlockedOutput["Content Blocked by Safety Threshold"]""",
        text_alternative=(
            "1. User Input -> 2. Safety & Policy Classifier -> 3. Model Reasoning -> "
            "4. Output Harm & Attribution Evaluation -> 5. Audited Safe Response or Blocked."
        ),
        input_spec="Raw student/user prompt",
        output_spec="Filtered, policy-compliant safe response or blocked message",
        components={
            "Input Filter": "Pre-generation safety checks (hate speech, sexual content, harassment, dangerous content).",
            "Foundation Model": "Safety-aligned model following constitutional system instructions.",
            "Output Filter": "Post-generation verification for hallucinations, attribution, and safety thresholds.",
        },
    ),
    "vertex_ai_studio": LessonDiagram(
        topic_id="vertex_ai_studio",
        title="Vertex AI Studio Generative Prototyping Workflow",
        description="Iterative lifecycle from prompt design to parameter tuning and API deployment.",
        mermaid_code="""graph TD
    Concept["Business Use Case"] --> Studio["Vertex AI Studio UI"]
    Studio --> PromptDesign["Design Zero-Shot / Few-Shot System Instructions"]
    PromptDesign --> Tuning["Tune Temperature (0.0-2.0), Top-P (0.95), Top-K (40)"]
    Tuning --> Evaluation["Inspect Model Responses & Latency"]
    Evaluation --> Export["Export to Python Code / Cloud Run Deployment"]""",
        text_alternative=(
            "1. Use Case Concept -> 2. Vertex AI Studio -> 3. Prompt Design -> "
            "4. Parameter Tuning (Temperature/Top-P) -> 5. Response Evaluation -> 6. Code Export."
        ),
        input_spec="Business use case and sample prompts",
        output_spec="Tuned model configuration, prompt templates, and production export code",
        components={
            "Vertex AI Studio": "Web console for rapid experimentation with Gemini models.",
            "System Instructions": "Guiding role, persona, and output formatting rules.",
            "Parameter Tuning": "Controlling determinism (Temperature), diversity (Top-P), and candidate pool (Top-K).",
            "Code Export": "One-click export to Python SDK or REST API.",
        },
    ),
}


def get_diagram_for_topic(topic_id: str) -> LessonDiagram | None:
    """Returns the validated lesson visual for a given topic ID, or None if not defined."""
    return DIAGRAM_CATALOG.get(topic_id)


def list_available_diagrams() -> list[LessonDiagram]:
    """Returns all available lesson diagrams."""
    return list(DIAGRAM_CATALOG.values())


def get_all_diagram_topics() -> list[str]:
    """Returns list of all topic IDs that have registered visual diagrams."""
    return list(DIAGRAM_CATALOG.keys())
