# Milestone 3: Topic Expert Agent

## Original Planned Goals
Implement the Topic Expert Agent to explain complex certification topics using various learning preferences.

## Full Antigravity Instructions

```text
# ANTIGRAVITY — M3: TOPIC EXPERT AGENT

You are a senior Google ADK engineer and Python architect.

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M3 of 8
BRANCH: main
TARGET RELEASE: v0.3.0

GOAL:
Implement a Gemini-powered Topic Expert Agent that
teaches certification topics using the existing
versioned curriculum and adapts explanations to
the student's experience and learning preferences.

Work inside the existing cloned repository.
Implement M3 only.

==============================================
1. INSPECT THE EXISTING IMPLEMENTATION
==============================================

Read:
- GEMINI.md
- README.md
- docs/architecture.md
- docs/antigravity/03-topic-expert-agent.md
- src/study_coach/agent.py
- src/study_coach/config.py
- src/study_coach/agents/study_planner.py
- src/study_coach/models/
- src/study_coach/tools/
- src/study_coach/data/

Confirm:
- Current branch is main.
- Existing origin remote is correct.
- Git working tree is clean.
- M1 and M2 tests pass.
- ADK configuration uses the model from the
  verified M2 live run.

Preserve all existing functionality.

==============================================
2. CREATE TOPIC EXPERT AGENT
==============================================

Create:
src/study_coach/agents/topic_expert.py

Use the installed official Google ADK API.

Agent name:
topic_expert

Responsibilities:
- Explain curriculum topics accurately.
- Adapt explanations for beginner,
  intermediate and advanced students.
- Explain important concepts and terminology.
- Provide practical Google Cloud examples.
- Identify prerequisites and related topics.
- Highlight important learning objectives.
- Explain common misconceptions.
- Offer short comprehension checks.

Do not generate scored certification quizzes.
That belongs to M4.

Do not claim Google certification questions are official.

==============================================
3. USE EXISTING CURRICULUM
==============================================

Reuse:
src/study_coach/data/google_cloud_genai_leader.yaml

Do not duplicate curriculum definitions.

Implement deterministic tools to:
- Retrieve a curriculum topic by ID.
- Search local curriculum topics by keyword.
- Retrieve learning objectives.
- Retrieve topic prerequisites or related topics
  where available.

Use existing tools where appropriate.

Do not add a vector database, external web search,
RAG pipeline, or MCP in M3.

Clearly distinguish curriculum-supported facts
from illustrative explanations.

Never invent official exam objectives.

==============================================
4. STRUCTURED OUTPUT
==============================================

Create:
src/study_coach/models/topic_explanation.py

Use Pydantic v2.

Define a TopicExplanation containing:
- topic_id
- topic_title
- experience_level
- learning_objectives
- key_concepts
- explanation
- practical_example
- common_misconceptions
- related_topics
- comprehension_questions
- source_references

Provide clear field descriptions and validation.

Validate:
- The selected topic exists.
- Experience level is supported.
- Related topic IDs exist where used.
- Required explanation fields are nonempty.
- Comprehension questions are nonempty.
- Source references are not fabricated.

If ADK structured output conflicts with
callable tools, use a documented compatible
two-step approach rather than bypassing validation.

==============================================
5. ROOT AGENT INTEGRATION
==============================================

Update:
src/study_coach/agent.py

Preserve root_agent and Study Planner.

Register Topic Expert using supported
Google ADK sub-agent delegation.

The coordinator should distinguish:

"Create my study plan"
  -> Study Planner

"Explain grounding to me"
  -> Topic Expert

"Explain Day 4 of my study plan"
  -> Topic Expert using available plan context

If the plan is not present in session state,
ask for the topic or day details rather than
pretending to remember them.

Do not implement quiz scoring or adaptive
replanning in M3.

These belong to M4 and M5.

==============================================
6. LIVE DEMO
==============================================

Test through the real ADK Runner or ADK Web.

Prompt A:
"Explain grounding and RAG to me as a
beginner. Use a Google Cloud example."

Prompt B:
"Explain the same topic at an advanced
level. Discuss architecture, limitations,
and common mistakes."

Prompt C:
"Create a 7-day study plan with 45 minutes
per day for Generative AI Leader."

Expected:
- Prompts A and B delegate to Topic Expert.
- Prompt C still delegates to Study Planner.
- Beginner and advanced explanations differ.
- All structured results validate.
- Existing M2 planning still works.

Use the configured GEMINI_MODEL.
Do not hardcode a different model in test scripts.

Never print API credentials.

==============================================
7. AUTOMATED TESTS
==============================================

Create:
tests/unit/test_topic_tools.py
tests/unit/test_topic_explanation.py
tests/integration/test_topic_expert.py

Test:
- Valid topic lookup.
- Unknown topic rejection.
- Beginner explanation schema.
- Advanced explanation schema.
- Invalid experience level.
- Empty explanation rejection.
- Invalid related topic reference.
- Root agent imports.
- Both specialist agents are registered.
- Offline delegation configuration.
- No regression to M1/M2.
- No live API calls required in CI.

Use fixtures and mocks for offline tests.

==============================================
8. QUALITY CHECKS
==============================================

Run:
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Fix all failures.

Verify the ADK developer UI launches and
the Topic Expert agent is discoverable.

Run at least one actual live Topic Expert
request if the local API key is configured.

Report offline and live results separately.

==============================================
9. DOCUMENTATION
==============================================

MANDATORY:
Save this COMPLETE M3 instruction under:

docs/antigravity/03-topic-expert-agent.md

Preserve the original planned goals.
Do not replace this instruction with a summary.

Append the actual:
- Implementation details
- Files changed
- Agent architecture
- Tests performed
- Live validation results
- Known limitations
- Commit hash and tag
- GitHub push status

Update:
- README.md
- docs/architecture.md
- docs/antigravity/README.md

Create:
examples/sample_topic_explanation.json

Ensure the example validates against Pydantic.

Keep M1 and M2 documentation intact.

==============================================
10. GITHUB CHECKPOINT
==============================================

Stay on main.
Preserve existing history and Git tags.

Verify all quality gates before committing.
Do not stage .env or any credentials.
Check for unrelated changes and remote conflicts.

Commit message:
feat(m3): implement Gemini ADK Topic Expert Agent

Create annotated tag:
v0.3.0

Push main and v0.3.0 to origin.

Never force-push.

If validation fails, stop and report the issue.

==============================================
11. FINAL REPORT
==============================================

Report:
1. Files created or modified
2. Topic Expert architecture
3. How curriculum tools are used
4. How root_agent delegates requests
5. Google ADK version and Gemini model
6. Total passing tests
7. Ruff and mypy results
8. Live Gemini test results
9. ADK execution trace summary
10. Commit hash
11. Tag and push status
12. Known limitations

STOP AFTER M3.

Do not implement M4 Quiz Generator,
M5 adaptive orchestration,
M6 Docker,
M7 observability,
or M8 release.
```

---

## Implementation Details

### 1. Architecture Overview
- **Agent Name**: `topic_expert`
- **Model**: `GEMINI_MODEL` (`gemini-3.8-flash`) via Google ADK (`Agent`).
- **Tools**:
  - `get_topic_by_id`: Deterministically retrieves topic metadata from `google_cloud_genai_leader.yaml`.
  - `search_topics`: Searches curriculum topic titles, descriptions, categories, and objectives by keyword.
  - `get_learning_objectives`: Returns curriculum learning objectives.
  - `get_related_topics`: Returns prerequisites and related topics from the curriculum.
- **Output Schema**: `TopicExplanation` Pydantic v2 model enforcing required fields, non-empty text, valid experience levels, and reference integrity with the curriculum.
- **Root Delegation**: `study_coach` (`root_agent`) coordinates both `study_planner` and `topic_expert` sub-agents via ADK native transfer.

### 2. Files Created or Modified
- `src/study_coach/tools/topic_tools.py` (created): Deterministic curriculum query tools.
- `src/study_coach/models/topic_explanation.py` (created): Pydantic v2 schema for structured explanations.
- `src/study_coach/models/__init__.py` (modified): Exported new models.
- `src/study_coach/agents/topic_expert.py` (created): Topic Expert agent declaration and tool wiring.
- `src/study_coach/agent.py` (modified): Registered `topic_expert` in `root_agent` sub-agents with clear routing instructions.
- `examples/sample_topic_explanation.json` (created): Validated reference explanation artifact.
- `tests/unit/test_topic_tools.py` (created): Unit tests for topic retrieval and keyword search tools.
- `tests/unit/test_topic_explanation.py` (created): Schema validation and invariant tests for `TopicExplanation`.
- `tests/integration/test_topic_expert.py` (created): Delegation and agent configuration tests.
- `docs/architecture.md` (modified): Updated multi-agent architecture diagram to reflect Topic Expert Agent active state.
- `docs/antigravity/README.md` (modified): Updated milestone status tracking for M3.
- `docs/antigravity/03-topic-expert-agent.md` (modified): Stored full instructions and post-implementation audit.
- `README.md` (modified): Updated feature list and project progress.

### 3. Validation Commands
```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q
```

### 4. Actual Offline Test Results
```text
Running tests...
.................................                                        [100%]
33 passed in 0.70s
Running code formatting checks...
All checks passed!
33 files already formatted
Running type checks...
Success: no issues found in 21 source files
All checks passed!
```

### 5. Live Gemini Verification Results

#### Prompt A: Beginner Topic Explanation
- **Query**: *"Explain grounding and RAG to me as a beginner. Use a Google Cloud example."*
- **Delegation**: `study_coach` transferred immediately to `topic_expert`.
- **Tools Called**: `search_topics`, `get_related_topics`, `get_topic_by_id`, `get_learning_objectives`, `set_model_response`.
- **Result**: Validated `TopicExplanation` instance:
  - Topic: Generative AI Concepts: Grounding & Retrieval-Augmented Generation (RAG) (`genai_concepts`)
  - Experience Level: `beginner`
  - Formatted using clear analogies (closed-book vs open-book exams) and enterprise HR retrieval assistant on Vertex AI Search.

#### Prompt B: Advanced Topic Explanation
- **Query**: *"Explain the same topic at an advanced level. Discuss architecture, limitations, and common mistakes."*
- **Delegation**: `study_coach` transferred to `topic_expert`.
- **Tools Called**: `search_topics`, `get_topic_by_id`, `get_related_topics`, `get_learning_objectives`, `set_model_response`.
- **Result**: Validated `TopicExplanation` instance:
  - Topic: Large Language Models (LLMs) (`llm_architecture`)
  - Experience Level: `advanced`
  - Technical deep dive into vector embeddings, cosine distance, chunking strategies, retrieval latency, and hybrid grounding architectures on Vertex AI.

#### Prompt C: Regression Study Plan
- **Query**: *"Create a 7-day study plan with 45 minutes per day for Generative AI Leader."*
- **Delegation**: `study_coach` transferred to `study_planner`.
- **Result**: Validated `StudyPlan` instance with exactly 7 sequential days, each $\le 45$ minutes, total planned minutes matching $315$.

### 6. Known Limitations
- The curriculum currently contains four primary foundational topics (`genai_concepts`, `llm_architecture`, `responsible_ai`, `vertex_ai_studio`); deep granular subtopic lookups map to these broader curriculum sections.
- Full conversational memory retention across deep multi-turn chat sessions without plan state re-prompting is planned for M5 (adaptive orchestration).
- Scored quizzes and interactive testing are intentionally deferred to M4.

### 7. Git Commit and Tag
- Commit: `to be recorded`
- Tag: `v0.3.0`
- GitHub Push Status: Pending checkpoint.
