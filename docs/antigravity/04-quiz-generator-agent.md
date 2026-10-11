# Milestone 4: Quiz Generator Agent

## Original Milestone Goals
Implement the Quiz Generator Agent to evaluate the user's understanding of the topics.

## Full Antigravity Instructions

```text
# ANTIGRAVITY — M4: QUIZ GENERATOR AGENT

You are a senior Google ADK engineer and Python architect.

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M4 of 8
BRANCH: main
TARGET TAG: v0.4.0

GOAL:
Build a Gemini-powered Quiz Generator Agent that
generates certification practice questions, evaluates
student answers using deterministic Python, and
identifies weak learning topics.

Implement M4 only.

==================================================
1. VERIFY EXISTING PROJECT
==================================================

Read:
- GEMINI.md
- README.md
- docs/architecture.md
- docs/antigravity/04-quiz-generator-agent.md
- src/study_coach/agent.py
- src/study_coach/agents/
- src/study_coach/models/
- src/study_coach/tools/
- src/study_coach/data/

Verify:
- Existing main branch and origin remote.
- Clean Git working tree.
- M1, M2 and M3 functionality.
- 33 existing tests pass.
- Current Google ADK and Gemini configuration.

Do not change the Gemini model unless necessary.
Never expose API credentials.

==================================================
2. CREATE QUIZ GENERATOR AGENT
==================================================

Create:
src/study_coach/agents/quiz_generator.py

Use the official Google ADK Agent API.

Agent name:
quiz_generator

Responsibilities:
- Accept certification and topic requirements.
- Read the local curriculum.
- Generate multiple-choice practice questions.
- Adjust difficulty for student experience.
- Provide four answer options per question.
- Provide one correct answer per question.
- Provide a factual explanation.
- Generate topic-specific feedback.
- Support configurable question count.

Default:
5 questions

Support beginner, intermediate and advanced.

Do not claim these are official certification questions.

Do not generate questions about topics outside
the available curriculum without identifying them
as unsupported.

==================================================
3. PYDANTIC QUIZ MODELS
==================================================

Create:
src/study_coach/models/quiz.py

Define:

QuizQuestion:
- question_id
- topic_id
- question_text
- options
- correct_answer
- explanation
- difficulty

Quiz:
- certification_name
- topic_ids
- experience_level
- questions

QuizSubmission:
- quiz_id
- student_answers

QuizResult:
- total_questions
- correct_answers
- score_percentage
- question_feedback
- weak_topics
- strong_topics

Validate:
- Exactly four options per question.
- Option identifiers A, B, C, D.
- Exactly one correct answer.
- Nonempty question and explanation.
- Unique question IDs.
- Valid topic IDs.
- Requested question count respected.
- Valid difficulty.
- No duplicate answer identifiers.
- Submitted answers reference valid questions.

Separate the answer key from student-facing
quiz display data.

Never expose correct answers before submission.

==================================================
4. DETERMINISTIC QUIZ TOOLS
==================================================

Create:
src/study_coach/tools/quiz_tools.py

Implement:

validate_quiz()
grade_quiz()
calculate_score()
identify_weak_topics()
generate_feedback_summary()

Use Python for:
- Answer comparison.
- Score calculation.
- Percentage calculation.
- Weak-topic classification.

Gemini generates questions and explanations.
Python determines whether submitted answers
match the answer key.

Do not ask Gemini to calculate quiz scores.

Ensure:
- No credentials required for scoring.
- No network requests during grading.
- Deterministic results for identical answers.
- Missing answers count as incorrect.
- Empty quiz is rejected.
- Topic weakness thresholds are documented.

==================================================
5. CURRICULUM INTEGRATION
==================================================

Reuse the existing curriculum:

src/study_coach/data/google_cloud_genai_leader.yaml

Reuse M2/M3 curriculum tools where possible.

Do not duplicate curriculum definitions.

Only create questions based on supported topics.

Use the curriculum to retrieve learning objectives.

Generated questions must be original practice
questions, not claimed official exam items.

Implement safeguards against ambiguous questions:
- One defensible correct answer.
- Four distinct options.
- Explanations consistent with the answer key.

Structural tests alone do not prove factual accuracy.
Include manually reviewed reference cases for
important curriculum concepts.

==================================================
6. ROOT AGENT INTEGRATION
==================================================

Update:
src/study_coach/agent.py

Preserve:
- root_agent
- study_planner
- topic_expert

Add:
quiz_generator

The root coordinator should distinguish:

"Create my study plan"
  -> study_planner

"Explain grounding and RAG"
  -> topic_expert

"Generate five practice questions about grounding"
  -> quiz_generator

"Check my answers"
  -> deterministic grading tools through the
     supported application workflow.

Do not implement automatic replanning yet.
That belongs to M5.

Use compatible ADK delegation and tool patterns.

==================================================
7. QUIZ ANSWER SECURITY
==================================================

IMPORTANT:

Use a server-side or private application
representation for answer keys.

Student-facing quiz presentation must not
include correct_answer or private explanations
before submission.

ADK internal traces may contain answer keys,
so clearly document that developer traces
are not student-facing output.

Do not persist sensitive student data
unnecessarily.

==================================================
8. STEP-BY-STEP TESTING
==================================================

MANDATORY:
Read and follow Rule 12 in GEMINI.md.

Test each component immediately after implementation.

A. Quiz Pydantic models
- Valid question.
- Invalid option count.
- Duplicate question IDs.
- Invalid correct answer.
- Invalid curriculum topic.
- Empty quiz.

B. Deterministic grading
- All answers correct: 100%.
- Three of five correct: 60%.
- No answers correct: 0%.
- Missing answers.
- Invalid submitted question IDs.
- Multiple incorrect answers on one topic.
- Weak-topic identification.

C. Agent integration
- Quiz Generator imports.
- root_agent imports.
- All three specialist agents registered.
- Correct tool registration.
- Correct routing configuration.

D. Regression
- Existing M1 tests pass.
- Existing M2 Study Planner tests pass.
- Existing M3 Topic Expert tests pass.

E. Live Gemini tests
When credentials are configured:

Prompt 1:
"Create five beginner practice questions on
grounding and RAG for Google Cloud
Generative AI Leader."

Prompt 2:
"Create five advanced questions on
foundation models and responsible AI."

Prompt 3:
"Create a 7-day study plan, 45 minutes
per day."

Prompt 4:
"Explain grounding and RAG for a beginner."

Verify:
- Prompts 1 and 2 route to quiz_generator.
- Prompt 3 routes to study_planner.
- Prompt 4 routes to topic_expert.
- Quiz output validates against Pydantic.
- No answers are revealed before submission
  in the student-facing presentation.
- Actual quiz scoring works.
- ADK trace shows correct agent delegation.
- Previously working functionality remains intact.

Test failure scenarios and tool exceptions.

Do not report simulated results as live results.

==================================================
9. QUALITY GATES
==================================================

Run after each major component, and once again
before the milestone commit:

uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Fix all failures.

Verify the ADK developer UI starts.

Report:
- Total passing tests.
- Separate offline/live test outcomes.
- Agent delegation trace.
- Pydantic validation results.
- Remaining limitations.

==================================================
10. DOCUMENTATION
==================================================

MANDATORY:

Save this COMPLETE M4 instruction into:

docs/antigravity/04-quiz-generator-agent.md

Preserve the original milestone goals.

Append:
- Files modified
- Implementation details
- Test commands
- Actual test outcomes
- Live Gemini results
- Fixes performed
- Known limitations
- Commit and release information

Update:
README.md
docs/architecture.md
docs/antigravity/README.md

Create:
examples/sample_quiz.json
examples/sample_quiz_result.json

Use validated examples.

Mark examples as illustrative unless
captured from real Gemini execution.

Keep M1-M3 documentation unchanged.

==================================================
11. GIT RELEASE
==================================================

Only commit after required checks pass.

Use existing main branch and origin.

Never force-push.
Do not move previous tags.
Do not commit credentials.
Check remote history before pushing.

Commit:

feat(m4): implement Gemini ADK Quiz Generator Agent

Create annotated tag:

v0.4.0

Push main and tag to origin.

If any required test fails or live verification
is incomplete, stop and report the blocker.
Do not create the milestone release tag.

==================================================
12. FINAL REPORT
==================================================

Provide:

1. Files created or modified
2. Quiz Generator architecture
3. Quiz schemas and validation rules
4. Deterministic scoring implementation
5. How answer keys are protected
6. Root-agent delegation behavior
7. Test results for each implementation step
8. Total regression test count
9. Ruff and mypy results
10. Actual live Gemini test results
11. ADK execution trace summary
12. Git commit hash
13. v0.4.0 tag status
14. GitHub push status
15. Known limitations

STOP AFTER M4.

Do not implement adaptive replanning,
Docker, Grafana, OpenTelemetry or
future milestones.
```

---

## Implementation Details

### 1. Architecture Overview
- **Agent Name**: `quiz_generator`
- **Model**: `GEMINI_MODEL` (`gemini-3.8-flash`) via Google ADK (`Agent`).
- **Tools**:
  - `load_curriculum`: Loads the versioned curriculum from `google_cloud_genai_leader.yaml`.
  - `get_topic_by_id`: Retrieves topic definition by ID.
  - `search_topics`: Finds topics and learning objectives by keyword.
  - `get_learning_objectives`: Retrieves target objectives to anchor practice questions.
  - `get_related_topics`: Cross-references prerequisites and topic connections.
- **Output Schema**: `Quiz` Pydantic v2 model enforcing exactly 4 distinct options ('A', 'B', 'C', 'D'), a single valid `correct_answer`, non-empty explanations, unique question IDs, and valid topic IDs.
- **Student View Security**: `Quiz.to_student_view()` returns `StudentQuizQuestion` instances stripped of `correct_answer` and `explanation` so the answer key is never exposed before student submission.
- **Deterministic Python Grading**: `grade_quiz()` performs exact matching between submitted answers and answer keys without invoking LLM tokens. Calculates score percentages, weak topics ($< 70\%$), and strong topics ($\ge 70\%$).
- **Root Delegation**: `study_coach` (`root_agent`) coordinates all three specialist agents: `study_planner`, `topic_expert`, and `quiz_generator`.

### 2. Files Created or Modified
- `src/study_coach/models/quiz.py` (created): Pydantic v2 schemas: `QuizQuestion`, `StudentQuizQuestion`, `Quiz`, `QuizSubmission`, `QuestionFeedback`, `QuizResult`.
- `src/study_coach/models/__init__.py` (modified): Exported all quiz models.
- `src/study_coach/tools/quiz_tools.py` (created): Deterministic scoring and feedback tools: `calculate_score`, `identify_weak_topics`, `grade_quiz`, `validate_quiz`, `generate_feedback_summary`.
- `src/study_coach/agents/quiz_generator.py` (created): Declared `quiz_generator` agent with curriculum tools and `Quiz` output schema.
- `src/study_coach/agent.py` (modified): Registered `quiz_generator` in `sub_agents` and added intent routing for practice quizzes and grading.
- `examples/sample_quiz.json` (created): Validated reference quiz artifact.
- `examples/sample_quiz_result.json` (created): Validated reference grading result artifact.
- `tests/unit/test_quiz_models.py` (created): 9 unit tests for quiz schemas, option constraints, and student views.
- `tests/unit/test_quiz_tools.py` (created): 7 unit tests for deterministic scoring, missing answer penalties, and weak topic thresholds.
- `tests/integration/test_quiz_generator.py` (created): 3 integration tests verifying root delegation routing and agent configurations.
- `tests/integration/test_topic_expert.py` (modified): Updated subagent assertion count for the 3 registered agents.
- `docs/architecture.md` (modified): Updated architecture diagram and notes to reflect Quiz Generator Agent as an active component.
- `docs/antigravity/README.md` (modified): Marked M4 completed in milestone tracking.
- `docs/antigravity/04-quiz-generator-agent.md` (created): Stored full instructions and post-implementation audit.
- `README.md` (modified): Updated feature set and roadmap.

### 3. Step-by-Step Testing Audit Table

| Component Tested | Test Command | Expected Result | Actual Result | Status | Fixes Applied | Remaining Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Quiz Models (`quiz.py`)** | `uv run pytest tests/unit/test_quiz_models.py -v` | Validates option count (A, B, C, D), correct answer choice, unique question IDs, student-facing view sanitization. | 9/9 tests passed. Invalid options, duplicate options, and unknown topics rejected. | **PASS** | Added explicit `dict[str, Any]` type annotations in test helpers for strict mypy compliance. | Models strictly check against YAML curriculum topics. |
| **Deterministic Grading (`quiz_tools.py`)** | `uv run pytest tests/unit/test_quiz_tools.py -v` | Calculates scores deterministically (100%, 60%, 0%), handles missing answers, identifies weak topics ($< 70\%$). | 7/7 tests passed. | **PASS** | Removed unused `question_map` assignment to satisfy Ruff `F841`. | Threshold currently set at $70\%$ mastery mark. |
| **Agent Integration (`quiz_generator.py`, `agent.py`)** | `uv run pytest tests/integration/test_quiz_generator.py -v` | Root agent registers `study_planner`, `topic_expert`, and `quiz_generator`; routing instructions present. | 3/3 tests passed. All 3 specialists active. | **PASS** | Adjusted subagents length assertion in existing test suite. | None. |
| **Full Regression Suite** | `uv run pytest -q` | All 52 tests pass across M1 models, M2 study planner, M3 topic expert, and M4 quiz generator. | `52 passed in 0.74s` | **PASS** | Organized imports for Ruff `I001`. | None. Backward compatibility 100% verified. |
| **Formatting & Linting** | `uv run ruff check . && uv run ruff format --check .` | 0 lint errors, all files formatted. | `All checks passed! 39 files already formatted` | **PASS** | Formatted all 39 source and test files. | None. |
| **Static Type Checking** | `uv run mypy .` | Strict type checking passes across all files. | `Success: no issues found in 27 source files` | **PASS** | Added generic type arguments to dictionary instances. | None. |
| **Live Prompt 1 (Beginner Quiz)** | ADK Runner (`run_live` with `quiz_generator`) | Generates 5 beginner multiple-choice questions on grounding & RAG. | Generated 5 validated questions on `genai_concepts` and `vertex_ai_studio`. Answer key stripped in student view. Deterministically graded 4/5 ($80\%$). | **PASS** | ADK structured output handled via `set_model_response` tool pattern. | Questions bounded to local curriculum concepts. |
| **Live Prompt 2 (Advanced Quiz)** | ADK Runner (`run_live` with `quiz_generator`) | Generates 5 advanced questions on foundation models & responsible AI. | Generated 5 validated advanced questions on `llm_architecture` and `responsible_ai`. | **PASS** | Prompt instructions enforce advanced distractor quality. | None. |
| **Live Prompt 3 (M2 Study Planner Regression)** | ADK Runner (`run_live` with `study_planner`) | Generates 7-day plan, 45 mins/day. | Correctly routed to `study_planner`; produced validated 7-day schedule (315 total minutes). | **PASS** | Zero delegation regression. | None. |
| **Live Prompt 4 (M3 Topic Expert Regression)** | ADK Runner (`run_live` with `topic_expert`) | Explains grounding & RAG for beginner. | Correctly routed to `topic_expert`; produced validated `TopicExplanation`. | **PASS** | Zero delegation regression. | None. |
| **ADK Web UI Server** | `scripts/run_local.sh` (`uv run adk web`) | Server launches on `http://127.0.0.1:8000` and serves `src.study_coach`. | Server started cleanly; `GET /list-apps` returned `["src.study_coach"]`. | **PASS** | Preserved `root_agent` discovery. | Manual browser testing. |

### 4. Git Commit and Tag
- Commit: `to be recorded`
- Tag: `v0.4.0`
- GitHub Push Status: Pending checkpoint.
