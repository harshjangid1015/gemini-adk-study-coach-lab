# Milestone 1: Project Foundation

## Objective and Scope
Build a working foundation for an AI Study Coach using Gemini and Google ADK. Create the core project structure, environment configuration, validation scripts, GitHub Actions CI, base Pydantic models for the student profile, and a minimal working Google ADK root agent that greets the user and asks for their certification goals.

## Full Antigravity Instructions

```text
You are a senior Python engineer and Google Agent Development Kit (ADK) specialist.

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M1 — Project Foundation
BRANCH: main

We are building a beginner-friendly multi-agent AI Study Coach using Gemini and Google ADK.

This is milestone 1 of 8. Implement ONLY M1.

IMPORTANT:
- The GitHub repository already exists.
- It has already been cloned locally.
- Work inside the current Antigravity workspace.
- Do NOT create or clone another GitHub repository.
- Do NOT initialize Git again.
- Preserve the existing remote and README.
- Inspect existing files before changing anything.

==================================================
1. PROJECT OBJECTIVE
==================================================

Build a working foundation for an AI Study Coach.

A student will eventually be able to ask:

"I'm preparing for the Google Cloud Generative AI Leader certification in 14 days. I'm a beginner and can study 90 minutes daily. Create my study plan, explain important topics, and test my knowledge."

The final application will use:

1. Study Coach Coordinator
2. Study Planner Agent
3. Topic Expert Agent
4. Quiz Generator Agent

For M1, implement ONLY a minimal working ADK root agent.

Do not implement the three specialist agents yet.

==================================================
2. TECHNOLOGY STACK
==================================================

Use:

- Python 3.11+
- Google ADK (google-adk)
- Gemini API
- Pydantic v2
- PyYAML
- uv
- pytest
- Ruff
- mypy

Use official documented Google ADK APIs.

Choose a currently supported stable Gemini model and explain the selection.

Do not introduce:

- LangChain
- CrewAI
- FastAPI
- Streamlit
- SQLite
- MCP
- BigQuery
- Kubernetes
- Grafana

These are unnecessary in M1.

==================================================
3. REPOSITORY STRUCTURE
==================================================

Create this structure without overwriting existing valid files:

gemini-adk-study-coach-lab/
├── docs/
│   ├── antigravity/
│   │   ├── 01-project-foundation.md
│   │   ├── 02-study-planner-agent.md
│   │   ├── 03-topic-expert-agent.md
│   │   ├── 04-quiz-generator-agent.md
│   │   ├── 05-multi-agent-orchestration.md
│   │   ├── 06-workshop-ui-docker.md
│   │   ├── 07-observability-evaluation.md
│   │   └── 08-workshop-ready-release.md
│   └── architecture.md
│
├── src/
│   └── study_coach/
│       ├── __init__.py
│       ├── agent.py
│       ├── config.py
│       ├── agents/
│       ├── tools/
│       ├── models/
│       │   ├── __init__.py
│       │   └── student.py
│       ├── workflows/
│       └── data/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── eval/
│
├── examples/
│   └── student_request.json
│
├── scripts/
│   ├── run_local.sh
│   └── run_tests.sh
│
├── .github/workflows/
│   └── ci.yml
│
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── GEMINI.md
├── LICENSE
└── README.md

Create package initialization files as necessary.

Ensure the src-layout is compatible with Google ADK agent discovery.

Do not assume ADK automatically discovers arbitrary src layouts.

Implement and verify a real launch command, adjusting packaging or launch paths if needed.

==================================================
4. IMPLEMENT FIRST GOOGLE ADK AGENT
==================================================

File:
src/study_coach/agent.py

Create an ADK root_agent.

Name: study_coach

Description:
An AI Study Coach helping students prepare for technical certifications.

Behavior:

- Greet the student.
- Ask about their certification goal.
- Ask how many days remain until the exam.
- Ask about daily study availability.
- Explain the future capabilities of the application.

Do not claim study planning, quizzes, or multi-agent delegation already work.

Use Gemini through official Google ADK.

All credentials must come from environment variables.

==================================================
5. STUDENT DATA MODELS
==================================================

File:
src/study_coach/models/student.py

Create Pydantic models.

StudentProfile:
- experience_level: beginner/intermediate/advanced
- daily_study_minutes: integer
- learning_preferences: optional list

StudyRequest:
- certification_name: string
- days_until_exam: integer
- student_profile: StudentProfile

Validation:

- Days must be greater than zero.
- Study minutes must be between 1 and 480.
- Certification name must not be empty.
- Experience level must be valid.

Create an example JSON request in:
examples/student_request.json

Example:
Certification: Google Cloud Generative AI Leader
Days: 14
Level: beginner
Minutes per day: 90

==================================================
6. ENVIRONMENT CONFIGURATION
==================================================

Create .env.example with supported ADK environment variable names.

Include:

GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=verified_supported_model_id

Use a real supported model identifier as the default, not a placeholder.

Ensure:
- .env is Git-ignored.
- API keys are never committed.
- Tests do not require an API key.
- No paid Gemini calls occur in CI.

Explain how to get a Gemini API key from Google AI Studio.

==================================================
7. ANTIGRAVITY PROJECT INSTRUCTIONS
==================================================

Create GEMINI.md.

Include these permanent project rules:

1. Implement one milestone at a time.
2. Preserve previously working functionality.
3. Prefer official Google ADK APIs.
4. Use type hints and Pydantic.
5. Use Python for deterministic calculations.
6. Keep components modular and testable.
7. Never hardcode credentials.
8. Run all quality checks after each milestone.
9. Update README when behavior changes.
10. Do not prematurely implement future milestones.

Create eight milestone instruction documents.

The documents should describe the milestone goals,
deliverables, and acceptance criteria.

Only M1 should contain completed implementation details.
M2-M8 remain planned.

==================================================
8. TESTS AND QUALITY
==================================================

Write tests for:

- Valid StudentProfile
- Invalid experience level
- Invalid daily study minutes
- Invalid exam deadline
- Empty certification name
- Valid StudyRequest JSON
- Successful import of the ADK root_agent

Configure Ruff, mypy, and pytest.

Run:

uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Fix any failures.

Do not claim the tests passed without running them.

==================================================
9. LOCAL EXECUTION
==================================================

Implement scripts/run_local.sh.

It must launch the Google ADK developer UI using a verified working command.

Implement scripts/run_tests.sh.

Verify:

- ADK root_agent can be imported.
- ADK agent discovery works.
- The development server starts successfully.
- The README documents the correct URL and commands.

If an API key is configured, test a basic live greeting.

If no API key is available, perform offline checks and report the live test as not verified.

Do not block automated tests on live API access.

==================================================
10. DOCUMENTATION
==================================================

Create a beginner-friendly README.

Include:

1. Project overview
2. Technology stack
3. Architecture diagram
4. Installation
5. Gemini API key setup
6. Local ADK launch
7. Example conversation
8. Running tests
9. Eight-milestone roadmap
10. Current functionality versus planned features

Create docs/architecture.md with a Mermaid diagram.

Clearly distinguish existing features from planned features.

Set up GitHub Actions to run the quality checks without API credentials.

==================================================
11. GITHUB CHECKPOINT
==================================================

The repository already exists.

Before committing:

- Inspect git status and current branch.
- Verify the remote is the existing GitHub repository.
- Confirm no secrets are staged.
- Confirm all tests and quality checks pass.
- Preserve any unrelated user changes.

If the workspace is clean initially and all checks pass:

Commit:

feat(m1): initialize Gemini ADK Study Coach foundation

Create annotated tag:

v0.1.0

Push:
- main
- v0.1.0

Never force-push.

If there are existing unrelated changes, remote conflicts,
failed checks, or incomplete acceptance criteria, do not
commit or push. Report the issue and leave files intact.

==================================================
12. FINAL REPORT
==================================================

After completing M1, show:

1. Files created or modified
2. Installed google-adk version
3. Configured Gemini model
4. Exact working launch command
5. ADK discovery and startup result
6. Number of passing pytest tests
7. Ruff results
8. mypy results
9. Git commit hash
10. GitHub push and tag status
11. Any limitations

STOP AFTER M1.

Do not implement M2.
```

## Files created or modified
- `pyproject.toml`
- `uv.lock`
- `.env.example`
- `.github/workflows/ci.yml`
- `GEMINI.md`
- `README.md`
- `docs/architecture.md`
- `docs/antigravity/` (01 to 08 milestone docs)
- `examples/student_request.json`
- `scripts/run_local.sh`
- `scripts/run_tests.sh`
- `src/study_coach/__init__.py`
- `src/study_coach/config.py`
- `src/study_coach/agent.py`
- `src/study_coach/models/__init__.py`
- `src/study_coach/models/student.py`
- `tests/unit/test_models.py`
- `tests/unit/test_agent.py`

## Validation commands
```bash
uv sync --all-extras
./scripts/run_tests.sh
```

## Actual test results
```
Running tests...
........                                                                 [100%]
=============================== warnings summary ===============================
.venv/lib/python3.14/site-packages/google/genai/types.py:42
  /Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/.venv/lib/python3.14/site-packages/google/genai/types.py:42: DeprecationWarning: '_UnionGenericAlias' is deprecated and slated for removal in Python 3.17
    VersionedUnionType = Union[builtin_types.UnionType, _UnionGenericAlias]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
8 passed, 1 warning in 0.60s
Running code formatting checks...
All checks passed!
18 files already formatted
Running type checks...
Success: no issues found in 7 source files
All checks passed!
```

## Git commit hash
`d353cc9` (Initial M1 commit)

## Git tag
`v0.1.0`

## Known limitations
- The `study_coach` agent uses hardcoded mock capability disclaimers inside instructions rather than coordinating actual specialized agents.
- Tests were executed entirely offline. The live agent invocation logic via ADK is deferred until the environment has an active `GOOGLE_API_KEY`.
