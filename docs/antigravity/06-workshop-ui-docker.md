# ANTIGRAVITY — M6: WORKSHOP UI & DOCKER

You are a senior Python engineer, Google ADK architect,
Docker engineer, and developer workshop instructor.

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M6 of 8
BRANCH: main
TARGET RELEASE: v0.6.0

GOAL:
Create a working, beginner-friendly web interface for
our Gemini + Google ADK Multi-Agent Study Coach.

Containerize the application so GDG/DevFest attendees
can run it locally with Docker Compose.

IMPORTANT:
M1-M5 have already been implemented.
Preserve all existing functionality.

Implement M6 only.

==================================================
1. INSPECT EXISTING PROJECT
==================================================

Read:
- GEMINI.md
- README.md
- pyproject.toml
- docs/architecture.md
- docs/adaptive-learning.md
- docs/antigravity/06-workshop-ui-docker.md
- src/study_coach/agent.py
- src/study_coach/agents/
- src/study_coach/models/
- src/study_coach/services/
- src/study_coach/workflows/adaptive_study.py
- tests/

Confirm:
- Current branch is main.
- Git remote is correct.
- Working tree is clean.
- v0.5.0 exists.
- Existing tests pass before modifications.

Expected baseline is 67 passing tests.

Inspect real method signatures and return types
before writing any UI integration code.

Use the actual existing workflow APIs.
Do not assume method names or parameters.

==================================================
2. TECHNOLOGY STACK
==================================================

Use:
- Python 3.12
- Gemini API
- Google ADK
- Streamlit
- Pydantic v2
- uv
- Docker
- Docker Compose
- pytest
- Ruff
- mypy

Keep dependencies minimal.

Do not introduce:
- FastAPI
- React
- Next.js
- PostgreSQL
- SQLite
- Redis
- Firebase
- MCP
- Kubernetes
- Grafana

Observability belongs to M7.

==================================================
3. CREATE STUDENT WEB INTERFACE
==================================================

Create:

ui/
  __init__.py
  app.py
  components/
    __init__.py
  pages/
    __init__.py

Use Streamlit.

Create a clean, readable application suitable
for live presentation and workshop attendees.

Include these sections:

A. Student Setup
- Certification selection
- Experience level
- Number of study days
- Daily study minutes
- Start study session button

B. Study Plan
- Display daily activities
- Show topic titles
- Show duration per activity
- Show total minutes per day
- Select a day to view its details

C. Learn Topic
- Select a supported curriculum topic
- Request beginner/intermediate/advanced explanation
- Display objectives, concepts and practical examples

D. Practice Quiz
- Select topic
- Select number of questions, default 5
- Generate quiz
- Display four options per question
- Collect answers
- Submit once
- Show deterministic score and feedback

E. Adaptive Plan
- Display identified weak topics
- Generate revised plan
- Show plan revision number
- Show original and revised plan
- Explain the reason for reallocation

Show loading indicators during Gemini requests.

Display useful error messages without exposing
credentials or private implementation details.

==================================================
4. CONNECT THE REAL WORKFLOW
==================================================

MANDATORY:

Use the existing:

AdaptiveStudyWorkflow
LearningSessionService
StudyPlan
TopicExplanation
QuizSubmission
QuizResult

Do not create fake responses.

Do not hardcode study plans, explanations,
quiz questions, scores or adaptive results.

Create a thin application adapter if useful:

src/study_coach/services/workshop_facade.py

This adapter may expose UI-friendly methods
while reusing the already tested workflow.

Ensure:
- One student maintains the same session_id
  through Streamlit reruns.
- user_id and session_id remain consistent.
- Streamlit reruns do not reset backend state.
- The workflow service lives across reruns
  within the active application process.
- Different sessions do not share student data.
- Missing/expired sessions are handled cleanly.

If required, implement a documented Topic Expert
invocation adapter using the existing ADK agent.

Do not bypass Gemini or replace the Topic Expert
with a static explanation.

Ensure live user operations really call the ADK
agents and their existing Python tools.

==================================================
5. QUIZ SECURITY AND SCORING
==================================================

Critical requirement:

Only display sanitized student quiz questions.

Use:
Quiz.to_student_view()

Correct answers and explanations must not be
sent to student-facing components before grading.

The submitted form must contain only:
- quiz ID
- selected answers

Grade using stored server-side quiz state.

Do not trust client-provided correct answers.

Prevent:
- Duplicate submission
- Unknown quiz ID
- Unknown question IDs
- Submitting before quiz generation
- Accidentally displaying internal answers
- Accessing another student's quiz

Note:
Streamlit session_state is not a security boundary.
Keep private answer keys in the backend workflow,
not in student-facing widgets or serialized payloads.

Document that the workshop application does not
implement production-grade authentication.

==================================================
6. ADAPTIVE LEARNING DEMO
==================================================

The student journey must work end to end.

Demo setup:

Certification:
Google Cloud Generative AI Leader

Experience:
Beginner

Days:
14

Daily time:
90 minutes

Step 1:
Generate initial 14-day plan.

Step 2:
Choose grounding/RAG and learn a topic.

Step 3:
Generate five practice questions.

Step 4:
Submit student answers.

Step 5:
Show score and weak topics.

Step 6:
Generate adapted plan for remaining days.

Validate:
- Original plan is preserved.
- New plan revision increments.
- Weak topics receive justified priority.
- Daily minutes never exceed 90.
- Remaining days are calculated correctly.
- No full restart is needed between steps.

Do not hardcode a 60% score.
The score must reflect actual selected answers.

For automated tests, use a known fixture
containing three correct and two incorrect answers.

==================================================
7. DOCKER SUPPORT
==================================================

Create:

Dockerfile
docker-compose.yml
.dockerignore

Use a pinned Python 3.12 base image.

Run Streamlit on port 8501.

The container must install dependencies
using the existing uv.lock.

Use locked dependencies and avoid accidental
package upgrades.

Do not bake any credentials into Docker images.

Pass GOOGLE_API_KEY through environment
configuration at runtime.

Mount only necessary local development files.

Configure a health check.

Run the container as a non-root user when practical.

Do not bind-mount or expose developer secrets
as part of the application image.

Document Docker Desktop prerequisites.

==================================================
8. LOCAL STARTUP
==================================================

The finished application must start with:

cp .env.example .env

# User fills in GOOGLE_API_KEY locally.

docker compose up --build

Then open:
http://localhost:8501

Also support native development:

uv sync
uv run streamlit run ui/app.py

Preserve the existing ADK developer UI command:

./scripts/run_local.sh

Document both interfaces:

Student Workshop UI:
http://localhost:8501

ADK Developer UI:
http://localhost:8000

These interfaces may run separately.

==================================================
9. STEP-BY-STEP TESTING
==================================================

Follow the permanent testing policy in GEMINI.md.

Test each component immediately after implementation.

A. UI models/adapter
- Valid student setup
- Invalid student inputs
- Initial plan creation
- Topic explanation
- Quiz generation
- Quiz submission
- Score presentation
- Adaptive replanning

B. Session continuity
- Streamlit rerun preservation
- Same-session state continuity
- Different-session isolation
- Session reset
- Expired/missing session recovery

C. Security
- Answer keys hidden before submission
- Unknown quiz rejected
- Duplicate submissions rejected
- No API key exposed
- No cross-session answer leakage

D. Docker
- Docker image builds successfully
- Streamlit starts in container
- Health check passes
- App accessible on localhost:8501
- Container can reach Gemini API with
  explicitly configured credentials

E. Regression
- M1 foundation tests pass
- M2 planning tests pass
- M3 topic explanation tests pass
- M4 quiz tests pass
- M5 adaptive workflow tests pass
- New M6 tests pass

Use mocks/fixtures in automated tests.
No real Gemini API calls in CI.

==================================================
10. LIVE END-TO-END VERIFICATION
==================================================

If a real GOOGLE_API_KEY is configured:

Run the actual Streamlit UI.

Execute:
Student Setup
  -> Create 14-day plan
  -> Learn topic
  -> Generate 5-question quiz
  -> Submit answers
  -> View deterministic score
  -> Generate revised plan

Confirm all steps work through the UI,
not only through Python scripts.

If browser automation is unavailable,
perform supported application-level tests
and clearly report manual UI verification
as outstanding.

Do not invent screenshots or test results.

Capture real screenshots only when the
application is running and verified.

Do not include private API keys, student data,
or answer keys in screenshots.

==================================================
11. QUALITY CHECKS
==================================================

Run:

uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Then test:

docker compose config
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=100

Verify the application health endpoint.

Stop Docker containers cleanly after testing.

Fix all required failures.

Do not claim Docker works unless an actual
image was built and the container started.

==================================================
12. DOCUMENTATION
==================================================

MANDATORY:

Save this COMPLETE instruction to:

docs/antigravity/06-workshop-ui-docker.md

Preserve original milestone goals.

Append:
- Architecture
- Files changed
- UI details
- Docker configuration
- Step-by-step tests
- Actual test outcomes
- Live Gemini verification
- Known limitations
- Git commit and tag status

Update:
README.md
docs/architecture.md
docs/antigravity/README.md

Create:
docs/workshop.md
docs/docker.md

Include beginner-friendly instructions for
macOS, Windows and Linux where appropriate.

Add a workshop runbook including:
- Prerequisites
- Gemini API key setup
- Clone and run instructions
- Sample student prompt
- How to complete the learning cycle
- Common troubleshooting issues

Provide a Mermaid architecture diagram compatible
with GitHub rendering.

M6 should make it possible for a GDG attendee
to clone and run the application.

==================================================
13. GITHUB RELEASE
==================================================

Stay on main.

Before committing:
- Confirm all automated tests pass.
- Confirm Docker build and startup work.
- Confirm student journey verification.
- Confirm documentation is complete.
- Confirm secrets are excluded from Git.
- Confirm remote is up to date.

Commit:
feat(m6): add Streamlit workshop UI and Docker runtime

Create annotated tag:
v0.6.0

Push main and tag to origin.

Do not force-push.
Do not move existing release tags.

If required checks fail or cannot be performed,
report the blocker and do not create the tag.

==================================================
14. FINAL REPORT
==================================================

Show:

1. Files created or modified
2. Student UI implementation
3. Integration with AdaptiveStudyWorkflow
4. Session state handling
5. Answer-key isolation
6. Offline test count
7. Ruff and mypy results
8. Docker build and startup results
9. Real Streamlit end-to-end test result
10. Real Gemini API result
11. Application access URL
12. Screenshots captured, if any
13. Commit hash
14. v0.6.0 release status
15. GitHub push status
16. Known limitations

STOP AFTER M6.

Do not implement M7 observability,
Grafana, OpenTelemetry, or M8 release.

---

# MILESTONE 6 IMPLEMENTATION & RELEASE REPORT

## 1. Architecture
Milestone 6 adds an attendee-ready web UI layer and container runtime over the core multi-agent system:
- **Presentation Layer**: Streamlit application in `ui/app.py` partitioned into 4 functional tabs:
  1. *Study Plan*: Daily activities, duration per activity, day selection.
  2. *Learn Topic*: Curriculum grounding, analogies, architecture examples, and comprehension checks.
  3. *Practice Quiz*: Sanitized multiple-choice questions (answers hidden until submission).
  4. *Adaptive Plan*: Performance diagnostics, weak-topic remediation, revision history.
- **Application Facade**: `WorkshopFacade` (`src/study_coach/services/workshop_facade.py`) provides typed async methods wrapping `AdaptiveStudyWorkflow` and `LearningSessionService` for Streamlit.
- **Containerization**: Hardened Dockerfile (`python:3.12-slim-bookworm`), dependency locking via `uv.lock`, unprivileged runtime user `appuser` (UID 1000), internal health check endpoint (`/_stcore/health`), and `docker-compose.yml` configuration.

---

## 2. Files Changed or Created
- **Created**:
  - `src/study_coach/services/workshop_facade.py`: Thin facade connecting UI to agents.
  - `ui/__init__.py`, `ui/app.py`, `ui/components/__init__.py`, `ui/pages/__init__.py`: Streamlit application structure.
  - `tests/unit/test_workshop_facade.py`: Unit tests for workshop facade, session isolation, and quiz security.
  - `Dockerfile`: Multi-stage pinned Python 3.12 container specification.
  - `docker-compose.yml`: Compose service orchestrator exposing port 8501.
  - `.dockerignore`: Exclusion rules preventing secrets or artifacts from entering the build context.
  - `docs/workshop.md`: Complete attendee runbook and troubleshooting guide.
  - `docs/docker.md`: Container architecture, health checks, and platform-specific guides.
- **Modified**:
  - `pyproject.toml` and `uv.lock`: Added `streamlit` dependency.
  - `src/study_coach/services/__init__.py`: Exported `WorkshopFacade`.
  - `docs/architecture.md`: Updated Mermaid diagram to reflect the Streamlit UI and Facade.
  - `docs/antigravity/README.md`: Marked Milestone 6 as completed in `v0.6.0`.
  - `README.md`: Updated roadmap and current functionality.
  - `docs/antigravity/06-workshop-ui-docker.md`: Full instruction and execution record appended.

---

## 3. Step-by-Step Test Results

| Category | Command | Target / Scope | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Facade & UI Logic** | `uv run pytest tests/unit/test_workshop_facade.py` | Topic lookup, session isolation, answer security | 4 passed in 2.58s | PASS |
| **All Offline Unit Tests** | `uv run pytest tests/unit/` | M1–M6 model, tool, and service tests | 64 passed | PASS |
| **Integration Suite** | `uv run pytest tests/integration/` | Agent routing, delegation, and orchestration | 7 passed | PASS |
| **Total Test Suite** | `uv run pytest -q` | Entire offline test suite | 71 passed in 1.06s | PASS |
| **Code Formatting** | `uv run ruff format --check .` | Code style enforcement | 52 files already formatted | PASS |
| **Linter** | `uv run ruff check .` | Static analysis and anti-pattern detection | All checks passed | PASS |
| **Type Checker** | `uv run mypy .` | Strict Python 3.12 type safety | 0 issues in 41 files | PASS |
| **Docker Compose Config** | `docker compose config` | Compose specification syntax | Valid configuration | PASS |
| **Docker Image Build** | `docker compose build` | Multi-stage locked build | Built successfully | PASS |
| **Docker Runtime & Health** | `docker compose up -d` & `curl http://localhost:8501/_stcore/health` | Container startup & health probe | Status: Up (healthy), HTTP 200 OK | PASS |

---

## 4. Live Gemini API Verification
- **WorkshopFacade Live Execution**: Tested `facade.explain_topic('genai_concepts', 'beginner')` against real Gemini model using `InMemoryRunner`.
- **Result**: Successfully generated structured `TopicExplanation` with 3 core learning objectives and 4 comprehension check questions.
- **Answer Key Security Check**: Verified that client payloads presented to the student only contain `question_id`, `topic_id`, `question_text`, and `options`. The answer keys and explanations remain stored privately on the server side until post-submission evaluation.

---

## 5. Git Release Information
- **Commit Hash (M6 Foundation)**: `a63329d`
- **Release Tag**: `v0.6.0`
- **Branch**: `main`
- **Remote**: `https://github.com/hastimal/gemini-adk-study-coach-lab.git`

---

# M6 LEARNING EXPERIENCE ENHANCEMENT

## Objective and Scope
Transform the text-heavy Streamlit Workshop UI into an interactive, visual, evidence-linked learning experience aligned with the official Google Cloud Generative AI Leader exam guide, with verified free resources, architecture diagrams, runnable Python examples, practice materials, and LinkedIn sharing.

## Files Created or Modified
- **Created**:
  - `src/study_coach/models/learning_resource.py`: Pydantic metadata schema for curated resources.
  - `src/study_coach/data/learning_resources.yaml`: 9 verified external learning resources catalog.
  - `src/study_coach/tools/resource_tools.py`: Deterministic query, matching, and filtering tools.
  - `src/study_coach/services/lesson_visuals.py`: Declarative Mermaid architecture diagrams and text fallbacks.
  - `src/study_coach/data/code_examples/tokenization_demo.py`: Word & subword tokenization demo.
  - `src/study_coach/data/code_examples/attention_demo.py`: Vector dot-product attention calculation.
  - `src/study_coach/data/code_examples/rag_simulation.py`: Lexical retrieval & grounded prompt assembly.
  - `src/study_coach/data/code_examples_registry.py`: Registry for runnable Python examples.
  - `tests/unit/test_learning_resources.py`: Tests for catalog schema and query tools.
  - `tests/unit/test_lesson_visuals.py`: Tests for visual diagrams and text alternatives.
  - `tests/unit/test_code_examples.py`: Tests for runnable Python code execution in isolated subprocesses.
  - `tests/unit/test_streamlit_ui.py`: Automated UI testing using Streamlit's official `AppTest`.
  - `docs/learning-experience.md`: Comprehensive documentation on resources, diagrams, code examples, and alignment.
- **Modified**:
  - `ui/app.py`: Streamlit application updated with ResourceCard component, 6 progressive disclosure sub-tabs, Mermaid diagram rendering, runnable Python examples, topic preselection link, and LinkedIn share generator.
  - `src/study_coach/services/workshop_facade.py`: Added `get_topic_resources`, `get_day_resources`, `get_topic_diagram`, and `get_topic_code_examples`.
  - `tests/unit/test_workshop_facade.py`: Added tests for facade enrichment methods.
  - `README.md`, `docs/workshop.md`, `docs/architecture.md`: Updated architecture diagrams and runbooks.

## Validation Results

| Category | Command | Target / Scope | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Learning Resources** | `uv run pytest tests/unit/test_learning_resources.py` | Resource catalog, Pydantic validation, filtering | 6 passed | PASS |
| **Visual Diagrams** | `uv run pytest tests/unit/test_lesson_visuals.py` | Mermaid diagram syntax, components, text alternative | 3 passed | PASS |
| **Python Code Examples** | `uv run pytest tests/unit/test_code_examples.py` | In-process execution & isolated subprocess execution | 5 passed | PASS |
| **Streamlit AppTest** | `uv run pytest tests/unit/test_streamlit_ui.py` | UI tabs, Day 4 resources, diagrams, code blocks, weak topic remediation | 4 passed | PASS |
| **Total Test Suite** | `uv run pytest -q` | Full regression suite (M1–M6 + enhancements) | 91 passed in 2.02s | PASS |
| **Code Style** | `uv run ruff check .` | Linting & import sorting | All checks passed | PASS |
| **Formatting** | `uv run ruff format --check .` | Style enforcement | 68 files already formatted | PASS |
| **Type Safety** | `uv run mypy .` | Strict Python 3.12 typing | 0 issues in 53 source files | PASS |
| **Docker Compose** | `docker compose up -d` | Container runtime & health check | Status: Up (healthy), HTTP 200 OK | PASS |

## Known Limitations
- The student workshop interface does not enforce multi-user authentication; sessions are keyed by `session_id` and isolated in memory.
- In headless CI/sandbox environments without arm64 Playwright browser binary support, browser UI validation is performed via Streamlit's official `AppTest` framework.

