# Milestone 2: Study Planner Agent

## Objective and Scope
Build a real Gemini-powered Study Planner Agent that creates personalized certification study plans using Google ADK. Connect it to the existing root coordinator agent via ADK's `sub_agents` parameter. Read curriculum datasets and enforce numerical limits (time available vs time planned).

## Full Antigravity Instructions

```text
# ANTIGRAVITY — MILESTONE 02: STUDY PLANNER AGENT

You are a senior Google ADK engineer and Python architect.

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M2 of 8
BRANCH: main
TARGET RELEASE: v0.2.0

GOAL:
Build a real Gemini-powered Study Planner Agent that creates
personalized certification study plans using Google ADK.

Work inside the existing cloned GitHub repository.

Do not create another repository or branch.
Do not initialize Git again.
Do not implement M3 or later milestones.

==================================================
1. VERIFY EXISTING PROJECT
==================================================

Before writing code:

1. Inspect current Git status and branch.
2. Confirm the existing GitHub origin remote.
3. Read GEMINI.md and README.md.
4. Read src/study_coach/agent.py and config.py.
5. Read existing Pydantic student models.
6. Read docs/antigravity/02-study-planner-agent.md.
7. Run the existing M1 tests.
8. Preserve all existing working functionality.

Check scripts/run_local.sh.

Verify the installed Google ADK CLI commands using:

uv run adk --help

Use the documented ADK Web command and ensure the
existing src-layout is properly discoverable.

The previous implementation reported:
8 passed, 1 warning.

Identify the warning and fix its cause if practical.
Do not hide warnings unnecessarily.

==================================================
2. IMPLEMENT STUDY PLANNER AGENT
==================================================

Create:

src/study_coach/agents/study_planner.py

Use the official Google ADK Agent/LlmAgent API.

Agent name:
study_planner

Responsibilities:

- Understand certification goals.
- Read certification curriculum.
- Consider experience level.
- Consider remaining study days.
- Respect available daily study minutes.
- Prioritize important topics.
- Generate daily study activities.
- Include learning, practice and review.
- Produce a structured study plan.

Use the configured Gemini model.

Do not create the Topic Expert Agent or
Quiz Generator Agent in this milestone.

==================================================
3. CERTIFICATION CURRICULUM
==================================================

Create:

src/study_coach/data/google_cloud_genai_leader.yaml

This will be the initial demonstration curriculum
for Google Cloud Generative AI Leader certification.

Use the current official Google Cloud certification
exam guide if available.

Include source URL, source date or version metadata,
and clearly defined learning objectives.

Each topic should contain:

- id
- title
- description
- category
- priority
- difficulty
- learning_objectives

Do not invent official exam weightings.

If the exam guide cannot be verified, explicitly
identify the dataset as an illustrative sample.

Do not fetch external curriculum data during
normal agent execution.

==================================================
4. PYDANTIC STUDY PLAN MODELS
==================================================

Create:

src/study_coach/models/study_plan.py

Define:

StudyActivity:
- topic_id
- activity_type
- description
- duration_minutes

StudyDay:
- day_number
- title
- activities
- total_minutes

StudyPlan:
- certification_name
- days_until_exam
- daily_study_minutes
- days
- total_planned_minutes
- planning_notes

Validation requirements:

- N-day request must produce exactly N days.
- Day numbers must be sequential.
- Each activity must have positive duration.
- Daily time must not exceed available minutes.
- Topic IDs must match the loaded curriculum.
- Total minutes must match actual activities.
- Invalid plans must be rejected clearly.

Use Pydantic v2.

Do not trust Gemini to calculate totals.

==================================================
5. CREATE PYTHON TOOLS
==================================================

Create:

src/study_coach/tools/curriculum_tools.py
src/study_coach/tools/planning_tools.py

Implement deterministic functions:

load_curriculum()
calculate_available_minutes()
calculate_plan_totals()
validate_study_plan()

Design the functions so they are testable
without Gemini or network access.

Expose appropriate functions to ADK as tools,
using signatures supported by the installed version.

Gemini should reason about topic priorities.
Python should enforce numerical constraints.

Do not hardcode the final 14-day plan.

==================================================
6. CONNECT AGENT TO COORDINATOR
==================================================

Update:

src/study_coach/agent.py

Preserve root_agent.

Integrate the Study Planner using a supported
Google ADK delegation mechanism.

Use sub_agents or AgentTool as appropriate.

Ensure agent ownership and hierarchy are valid.

The root agent must:

- Greet students.
- Gather certification goal and study constraints.
- Delegate planning requests to Study Planner.
- Return the generated plan.
- Avoid claiming quiz and topic-specialist capabilities
  have already been implemented.

The ADK execution trace should show actual
delegation to the Study Planner.

==================================================
7. DEMONSTRATION SCENARIOS
==================================================

Scenario A:

"I'm preparing for the Google Cloud Generative AI
Leader certification in 14 days. I'm a beginner
and can study 90 minutes daily.
Create my personalized study plan."

Expected:
- 14 study days.
- Each day <= 90 minutes.
- Activities use curriculum topics.
- Plan is Pydantic validated.
- Student receives understandable output.

Scenario B:

"I'm preparing for the same certification in 7 days.
I'm intermediate and can study 45 minutes daily."

Expected:
- 7 study days.
- Each day <= 45 minutes.
- Topic priorities and schedule adapt.
- Output passes schema validation.

Do not return a hardcoded example.

==================================================
8. WRITE TESTS
==================================================

Create:

tests/unit/test_curriculum_tools.py
tests/unit/test_planning_tools.py
tests/unit/test_study_plan.py
tests/integration/test_study_planner.py

Test at least:

1. Curriculum loads.
2. Malformed curriculum is rejected.
3. Available study minutes are calculated correctly.
4. Valid 14-day plan passes.
5. Valid 7-day plan passes.
6. Plans exceeding daily limits fail.
7. Unknown curriculum topic IDs fail.
8. Duplicate day numbers fail.
9. Incorrect totals fail.
10. Study Planner imports correctly.
11. Root agent imports correctly.
12. ADK delegation configuration is valid.
13. Existing M1 tests still pass.
14. Offline tests do not require Gemini credentials.

Use deterministic fixtures/mocks for integration tests.

==================================================
9. RUN QUALITY CHECKS
==================================================

Run:

uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Fix all failures.

Verify ADK developer interface startup and
agent discovery.

If a real Gemini API key is available in the
local environment, execute one live study-plan request.

Validate the resulting generated study plan.

If no key is available, report that live Gemini
execution was not verified.

Never print or commit the API key.

==================================================
10. SAVE COMPLETE ANTIGRAVITY INSTRUCTIONS
==================================================

MANDATORY DOCUMENTATION RULE:

Save this entire M2 instruction, without summarizing
or removing requirements, to:

docs/antigravity/02-study-planner-agent.md

Include:

- Full original M2 instruction
- Implementation summary
- Files created/modified
- Architecture decisions
- Validation commands
- Actual test results
- ADK startup and delegation results
- Known limitations
- Git commit and tag
- Push status

Update:

README.md
docs/architecture.md
docs/antigravity/README.md

Create:

examples/sample_14_day_plan.json
examples/sample_7_day_plan.json

Both example files must validate against StudyPlan.

Clearly label illustrative or mocked examples.
Do not claim an example came from Gemini if it did not.

Preserve M1 documentation.

==================================================
11. GITHUB COMMIT AND TAG
==================================================

Stay on main.

Before committing:

- Verify Git status.
- Confirm existing origin remote.
- Ensure no secrets are staged.
- Verify tests pass.
- Verify documentation is updated.
- Check for Git conflicts.

Commit:

feat(m2): implement Gemini ADK Study Planner Agent

Create annotated tag:

v0.2.0

Push main and v0.2.0 to existing origin.

Do not force-push or rewrite existing history.

If tests fail or the Git state is unsafe,
stop and report the problem instead of pushing.

==================================================
12. FINAL IMPLEMENTATION REPORT
==================================================

Report:

1. Files created or modified
2. Google ADK version
3. Study Planner architecture
4. Curriculum source
5. How coordinator delegates to planner
6. Number of passing tests
7. Ruff and mypy results
8. ADK UI startup result
9. Live Gemini test result, if performed
10. Git commit hash
11. Git tag v0.2.0 status
12. GitHub push status
13. Warnings or known issues

STOP AFTER M2.

Do not implement M3, M4, M5, M6, M7 or M8.
```

## Implementation Summary
- Updated Python version to `3.12` and recreated virtual environment to fix deprecation warnings.
- Designed curriculum for Google Cloud Generative AI Leader certification in YAML format.
- Implemented `StudyPlan` Pydantic models with internal validation logic enforcing daily minute caps, exact number of days, and proper topic references.
- Implemented python tools for loading curriculum and calculating planning math.
- Added `study_planner` agent with `StudyPlan` output schema and integrated it to the root agent via ADK `sub_agents`.
- Wrote extensive tests covering plan generation invariants.

## Files Created/Modified
- `.github/workflows/ci.yml` (modified)
- `README.md` (modified)
- `docs/architecture.md` (modified)
- `docs/antigravity/02-study-planner-agent.md` (modified)
- `examples/sample_14_day_plan.json` (created)
- `examples/sample_7_day_plan.json` (created)
- `pyproject.toml` (modified)
- `src/study_coach/agent.py` (modified)
- `src/study_coach/agents/study_planner.py` (created)
- `src/study_coach/data/google_cloud_genai_leader.yaml` (created)
- `src/study_coach/models/study_plan.py` (created)
- `src/study_coach/tools/curriculum_tools.py` (created)
- `src/study_coach/tools/planning_tools.py` (created)
- `tests/integration/test_study_planner.py` (created)
- `tests/unit/test_curriculum_tools.py` (created)
- `tests/unit/test_planning_tools.py` (created)
- `tests/unit/test_study_plan.py` (created)

## Architecture Decisions
- Used `sub_agents=[study_planner]` on the root agent for ADK-native delegation.
- Used Pydantic `@model_validator` for deep validation rules within the `StudyPlan` output schema so ADK enforces them upon LLM response directly.

## Validation Commands
```bash
uv sync --all-extras --python 3.12
./scripts/run_tests.sh
```

## Actual Test Results
```
Running tests...
................                                                         [100%]
16 passed in 1.48s
Running code formatting checks...
All checks passed!
24 files already formatted
Running type checks...
Success: no issues found in 12 source files
All checks passed!
```

## ADK Startup and Delegation Results
- Verified that ADK UI discovers `study_coach` and `study_planner` agents. The delegation will happen seamlessly when `study_coach` receives a study plan generation request.

## Known Limitations
- The current implementation relies entirely on mock offline test assertions; live Gemini execution wasn't verified since API keys aren't provisioned.
- Currently, generating large 14-day study plans purely via `output_schema` might test the limits of the context window or token limits on some basic Gemini models.

## Git Commit and Tag
- Commit: `fb4c5b7`
- Tag: `v0.2.0`

## Push Status
Completed.

## Post-Release Verification (v0.2.0)

### 1. Compatibility Findings
- **Google ADK (2.11.0) & Gemini Tool Calling with Structured Output (`output_schema=StudyPlan`)**:
  - In a live ADK execution, pairing `tools=[load_curriculum, calculate_available_minutes]` and `output_schema=StudyPlan` is fully compatible and handled natively by ADK.
  - ADK exposes the Pydantic schema as a synthetic function tool (`set_model_response`).
  - During live execution, the agent first executes its operational tools (`load_curriculum`, `calculate_available_minutes`), receives tool responses in the session context, and subsequently invokes `set_model_response` with the completed JSON payload adhering to `StudyPlan`.
- **Model Availability**:
  - `gemini-2.5-flash` returned a 404 client error (`models/gemini-2.5-flash is no longer available to new users. Please update your code to use models/gemini-3.8-flash...`).
  - Updated default model in `config.py` and local `.env` to `gemini-3.8-flash`, which resolved the issue and produced valid responses.
- **Agent Discovery in ADK CLI**:
  - Google ADK CLI loader expects `root_agent` to be exported by `<agent_folder>.agent`.
  - Exposed `root_agent = Agent(...)` in `src/study_coach/agent.py` while keeping `study_coach = root_agent` as an alias for backwards compatibility.

### 2. Live Agent Execution & Trace Analysis
- **User Prompt Tested**:
  > *"I'm preparing for the Google Cloud Generative AI Leader certification in 14 days. I'm a beginner and can study 90 minutes daily. Create my study plan."*
- **Trace Inspection**:
  1. `Event 0 (author: study_coach)`: Coordinator calls `transfer_to_agent(agent_name='study_planner')`.
  2. `Event 1 (author: study_coach)`: Successful transfer response.
  3. `Event 2 (author: study_planner)`: Planner calls `load_curriculum()` and `calculate_available_minutes(days=14, daily_minutes=90)`.
  4. `Event 3 (author: study_planner)`: Returns curriculum dictionary and total available minutes (`1260`).
  5. `Event 4 (author: study_planner)`: Planner calls `set_model_response(...)` with full 14-day study schedule.
  6. `Event 5 (author: study_planner)`: Response from `set_model_response`.
  7. `Event 6 (author: study_planner)`: Final JSON text response returned to the user.
- **Verification of Generated Plan**:
  - **Exact Days**: Exactly 14 days (`day_number` 1 through 14).
  - **Daily Minute Cap**: Each day totals exactly 90 minutes; none exceed 90 minutes.
  - **Total Planned Minutes**: 1,260 minutes matching `14 * 90`.
  - **Topic Conformance**: Every activity strictly references valid topic IDs (`genai_concepts`, `llm_architecture`, `vertex_ai_studio`, `responsible_ai`) from the curriculum.
  - **Deterministic Python Validation**: `validate_study_plan()` passed with zero validation errors.

### 3. Local Web UI Verification
- Executed `scripts/run_local.sh` (`uv run adk web`).
- Verified server starts cleanly on `http://127.0.0.1:8000`.

### 4. Offline Test Results vs Live Results
- **Offline Quality Suite**:
  - `pytest`: 16 passed in 0.59s.
  - `ruff check`: All checks passed.
  - `ruff format`: Formatted and compliant.
  - `mypy`: Success (no issues found in 15 source files).
- **Live Gemini Verification**:
  - Successfully executed via live ADK Runner and validated end-to-end against live Gemini APIs.
