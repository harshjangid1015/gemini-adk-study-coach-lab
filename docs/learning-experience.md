# Learning Experience Enhancement

## Overview

The Learning Experience Enhancement evolves the Gemini + Google ADK Study Coach from a text-heavy interface into an interactive, visual, evidence-linked multi-modal platform. It aligns with the official **Google Cloud Generative AI Leader** certification exam guide, providing verified learning resources, visual architecture diagrams, runnable Python examples, and deterministic diagnostic remediation pathways.

---

## 1. Official Exam Alignment

The curriculum is mapped directly to the official certification guide:
- **Certification:** [Google Cloud Generative AI Leader](https://cloud.google.com/learn/certification/generative-ai-leader)
- **Exam Domains Covered:**
  - *Domain 1:* Generative AI Fundamentals & Model Architectures (Tokens, Embeddings, Attention, Transformers)
  - *Domain 2:* Google Cloud GenAI Products & Workflows (Gemini, Vertex AI Studio, Model Garden, Agent Development Kit)
  - *Domain 3:* Grounding & Enterprise Retrieval (RAG, Vertex AI Search, Vector Search)
  - *Domain 4:* Responsible AI & Governance (Safety thresholds, moderation lifecycle, ethical evaluation)

---

## 2. Curated Learning Resource Library

A versioned, strictly verified catalog of external learning resources is maintained in [`src/study_coach/data/learning_resources.yaml`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/data/learning_resources.yaml) and validated via the `LearningResource` Pydantic model ([`src/study_coach/models/learning_resource.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/models/learning_resource.py)).

### Resource Metadata Schema
- `resource_id`: Unique identifier (e.g., `google_genai_leader_exam_guide`)
- `topic_ids`: Associated curriculum topics
- `title`: Verified resource title
- `provider`: Content provider (e.g., `Google Cloud`, `Hugging Face`, `3Blue1Brown`)
- `resource_type`: Type classification (`Official exam guide`, `Official documentation`, `Video`, `Python example`, `Interactive tutorial`)
- `url`: Direct, verified HTTPS link
- `short_description`: Concise synopsis
- `experience_level`: `beginner`, `intermediate`, `advanced`, or `all`
- `estimated_minutes`: Reading or viewing duration
- `exam_domain`: Relevant exam domain
- `requires_login` / `requires_paid_access`: Access prerequisites
- `is_official`: Boolean indicating whether published directly by Google
- `verification_status`: `verified` or `unverified`

### Verified Resources Catalog
| Resource ID | Title | Provider | Type | Duration | Official |
|---|---|---|---|---|---|
| `google_genai_leader_exam_guide` | Generative AI Leader Certification Exam Guide | Google Cloud | Official exam guide | 20 min | Yes |
| `vertex_ai_genai_docs` | Vertex AI Generative AI Documentation & Overview | Google Cloud | Official documentation | 25 min | Yes |
| `google_ml_crash_course_llm` | Google Machine Learning Crash Course - Large Language Models | Google Developers | Interactive tutorial | 30 min | Yes |
| `google_responsible_ai_practices` | Google Responsible AI Practices and Principles | Google | Official documentation | 20 min | Yes |
| `vertex_ai_studio_quickstart` | Vertex AI Studio Prompt Design & Prototyping Quickstart | Google Cloud | Official documentation | 15 min | Yes |
| `google_cloud_rag_grounding_repo` | Vertex AI Search & Grounding Reference Architecture | Google Cloud Platform | GitHub repository | 30 min | Yes |
| `huggingface_llm_course_intro` | Hugging Face LLM Course - Chapter 1: Introduction | Hugging Face | Article | 25 min | No |
| `3b1b_transformer_video` | Visualizing Transformers & Attention Mechanisms | 3Blue1Brown | Video | 27 min | No |
| `3b1b_attention_video` | Attention in Transformers, Visually Explained | 3Blue1Brown | Video | 26 min | No |

### Licensing & Link Verification Policy
- All links are tested for public availability and 200 HTTP response.
- Third-party content (e.g., 3Blue1Brown, Hugging Face) is linked directly to authoritative public endpoints without scraping, mirroring, or violating copyright.
- Official Google resources are distinguished from third-party community resources with explicit visual badges.

---

## 3. Visual Architecture Diagrams

Declarative Mermaid diagrams with comprehensive text fallbacks are generated via [`src/study_coach/services/lesson_visuals.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/services/lesson_visuals.py).

### Supported Topics & Diagrams
1. **`llm_architecture` (Transformer Inference & Autoregressive Decoding Flow):**
   - Inputs: Text Prompt string
   - Components: Tokenizer, Token Embeddings, Positional Encoding, Transformer Blocks (Multi-Head Attention & Feed-Forward), Output Projection, Softmax, Sampling.
   - Output: Next token probabilities.
2. **`genai_concepts` (Retrieval-Augmented Generation & Grounding Pipeline):**
   - Inputs: User Query
   - Components: Vertex AI Search, Document Retrieval, Augmented Prompt Assembly, Foundation Model.
   - Output: Fact-checked grounded response with source citations.
3. **`responsible_ai` (Google Responsible AI Safety & Moderation Lifecycle):**
   - Inputs: User prompt
   - Components: Pre-generation Safety Classifier, Aligned Gemini Reasoning, Post-generation Harm Evaluation & Attribution Check.
   - Output: Audited safe output or safety threshold block.
4. **`vertex_ai_studio` (Vertex AI Studio Generative Prototyping Workflow):**
   - Inputs: Business use case and prompt concepts
   - Components: Prompt Design (Zero-Shot/Few-Shot), Parameter Tuning (Temperature, Top-P, Top-K), Evaluation, Python Export.
   - Output: Tuned prompt templates and production export code.

---

## 4. Curated Practical Python Examples

To reinforce conceptual learning without incurring cloud costs or requiring student credentials, curated examples are provided in [`src/study_coach/data/code_examples/`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/data/code_examples/):
- **`tokenization_demo.py`:** Word and subword regex tokenization, deterministic token ID hashing simulation. Zero external dependencies.
- **`attention_demo.py`:** Scaled dot-product vector attention and Softmax distribution calculation. Zero external dependencies.
- **`rag_simulation.py`:** Lexical search passage retrieval, context concatenation, and grounded prompt assembly.
- **`prompt_comparison`:** Zero-shot vs. few-shot system instructions formulation.

All examples are tested in isolated subprocesses and unit tests to ensure safety, deterministic execution, and lack of credential leakage.

---

## 5. UI Architecture & Features

The Streamlit interface ([`ui/app.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/ui/app.py)) provides:
1. **Study Plan Tab:**
   - Day-by-day activity schedules.
   - Matched curated learning resources with estimated duration badges.
   - Explicit study budget reminder (resources do not silently increase daily minute limits).
2. **Learn Topic Tab:**
   - 6 progressive-disclosure sub-tabs: Summary & Objectives, Architecture Diagram, Step-by-Step Lesson, Hands-On Python, Verified Resources, Practice & Share.
   - Native Mermaid architecture diagram rendering with component breakdowns and accessible text alternative.
   - Python code block with expected outputs.
   - Practice preselection jump link.
   - LinkedIn Share text generator with safe manual share link (zero score or answer-key exposure).
3. **Practice Quiz Tab:**
   - Context-aware preselection when launched from Learn Topic.
   - Deterministic scoring, diagnostic feedback, and sanitized questions.
4. **Adaptive Plan Tab:**
   - Identifies weak topics (< 70%).
   - Displays multi-step remediation pathway (diagram review, Python demo, official docs) before replanning.
   - Full version history of study plans preserved across revisions.
