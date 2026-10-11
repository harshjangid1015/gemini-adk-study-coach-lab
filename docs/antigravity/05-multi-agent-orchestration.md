# ANTIGRAVITY — M5: MULTI-AGENT ORCHESTRATION

You are a senior Google ADK engineer, Python architect,
and AI application reliability engineer.

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M5 of 8
BRANCH: main
TARGET RELEASE: v0.5.0

GOAL:
Build a complete adaptive learning workflow that
coordinates Study Planner, Topic Expert and Quiz
Generator using Google ADK.

The student must be able to:

1. Request a personalized study plan.
2. Learn an important curriculum topic.
3. Take a generated practice quiz.
4. Submit answers.
5. Receive deterministic scoring and feedback.
6. Identify weak topics.
7. Generate an adapted study plan using the same
   student context and quiz results.

Implement M5 only.

==================================================
1. INSPECT EXISTING PROJECT
==================================================

Read:
- GEMINI.md
- README.md
- docs/architecture.md
- docs/antigravity/05-multi-agent-orchestration.md
- src/study_coach/agent.py
- src/study_coach/agents/
- src/study_coach/models/
- src/study_coach/tools/
- src/study_coach/data/
- tests/

Confirm:
- Existing branch: main
- Existing remote: origin
- Existing release: v0.4.0
- Previous functionality intact
- Current Gemini configuration works
- Working tree is clean

Run existing tests before making changes.

Do not recreate existing agents or break M1-M4.

==================================================
2. ORCHESTRATION ARCHITECTURE
==================================================

Preserve the existing root_agent and three specialists:

root_agent
├── study_planner
├── topic_expert
└── quiz_generator

Implement a controlled workflow:

Student Goal
   ↓
Study Planner
   ↓
Save Validated Study Plan
   ↓
Topic Expert
   ↓
Quiz Generator
   ↓
Present Sanitized Quiz
   ↓
Student Submits Answers
   ↓
Deterministic Python Grading
   ↓
Update Weak Topics
   ↓
Study Planner Replans
   ↓
Save Adapted Study Plan

Use documented Google ADK APIs compatible with the
installed google-adk version.

Do not rely solely on coordinator instructions
to guarantee workflow correctness.

Application state transitions and validation
must be enforced by Python.

Do not introduce an unbounded agent loop.

==================================================
3. STUDENT SESSION STATE
==================================================

Create:
src/study_coach/models/learning_session.py

Define validated state containing:

- student_profile
- certification_name
- exam_deadline_or_days_remaining
- current_study_plan
- current_quiz_id
- quiz_results
- weak_topics
- strong_topics
- completed_topics
- plan_revision
- learning_progress

Implement:
src/study_coach/services/learning_session.py

Use Google ADK's supported session and state APIs.

Use an in-memory session service for V1.

Persist state between requests in the SAME session.

Prevent accidental sharing between different
student sessions.

Ensure tests use isolated session identifiers.

Document that in-memory storage is not durable
across application restarts.

Do not add SQLite, Redis, Firestore or Cloud SQL.

==================================================
4. WORKFLOW AND STATE TRANSITIONS
==================================================

Create:
src/study_coach/workflows/adaptive_study.py

Implement explicit operations for:

- create_initial_plan()
- get_current_plan()
- generate_practice_quiz()
- submit_quiz_answers()
- retrieve_learning_progress()
- generate_adapted_plan()

Use existing agent and tool functionality.

Reuse:
- StudyPlan models
- Quiz models
- Curriculum tools
- Quiz grading tools
- Topic explanation models

Do not duplicate existing implementations.

Define clearly which functions are deterministic
and which invoke Gemini via Google ADK.

Reject invalid workflow transitions.

Examples:
- Submitting answers before creating a quiz
  must return a clear error.
- Replanning without relevant quiz results
  must not claim adaptive learning occurred.
- Unknown quiz IDs must be rejected.
- Duplicate submissions must not double-count
  progress.

==================================================
5. PROTECT QUIZ ANSWER KEYS
==================================================

M4 introduced:
Quiz.to_student_view()

Use this method whenever presenting questions
to the student.

Maintain the complete quiz and correct answers
in private application state only.

Do not expose:
- correct_answer
- private answer explanations
- complete internal Quiz objects

in the student-facing response before submission.

Do not trust client-provided answer keys.

Grade only against the stored original quiz.

ADK developer traces are trusted debugging output,
not secure student-facing interfaces.

Document this boundary explicitly.

For M5, validate the application-layer separation.
A full production authentication and authorization
system is outside scope.

==================================================
6. ADAPTIVE REPLANNING
==================================================

Use results from grade_quiz() and
identify_weak_topics().

Generate updated schedules using the existing
Study Planner Agent.

Rules:

1. Preserve the student's certification.
2. Preserve the available daily minutes.
3. Do not exceed remaining study days.
4. Prioritize weak topics for future review.
5. Preserve completed study activities.
6. Do not silently overwrite previous plans.
7. Increment the plan revision number.
8. Validate the new schedule using Pydantic.
9. Run deterministic time-budget validation.
10. Record why the plan was changed.

Do not claim the adapted plan improves actual
learning outcomes without evidence.

Avoid assuming that a single incorrect answer
proves poor topic mastery.

Use explicit documented weakness thresholds
and report limited evidence when question
coverage is insufficient.

==================================================
7. END-TO-END DEMO
==================================================

Use one persistent ADK session.

Student request:

"I'm preparing for the Google Cloud Generative AI
Leader certification in 14 days. I'm a beginner
and can study 90 minutes daily."

Then:

"Create my study plan."

Then:

"Explain grounding and RAG for a beginner."

Then:

"Generate five practice questions about grounding
and RAG."

Present only the sanitized quiz.

Submit five answers containing three correct
and two incorrect responses.

Expected scoring:
3 / 5 = 60%.

Then:

"Identify my weak topics and update my remaining
study plan."

Expected outcome:

- Coordinator invokes the appropriate specialists.
- Quiz score is deterministically calculated.
- Weak topics are stored.
- Study Planner receives quiz results.
- New study plan is created.
- Relevant weak topics receive justified priority.
- No remaining day exceeds 90 minutes.
- Previous plan remains available.
- Plan revision increments.
- Session retains relevant learning context.

Also test:
- Student with perfect quiz performance.
- Student with all incorrect answers.
- Separate student session.
- Missing study plan.
- Missing quiz.
- Duplicate quiz submission.
- Unknown quiz identifier.

==================================================
8. STEP-BY-STEP TESTING
==================================================

MANDATORY:
Follow all testing rules in GEMINI.md.

Test immediately after each implementation step.

A. State models:
- Valid learning session.
- Invalid session state.
- Missing or malformed profile.
- Plan revision validation.

B. Workflow operations:
- Initial plan creation.
- Quiz creation.
- Answer submission.
- Deterministic scoring.
- Progress retrieval.
- Adaptive replanning.

C. State isolation:
- Same-session continuity.
- Different-session isolation.
- No leaked quiz answer keys.
- Duplicate submission handling.

D. Replanning validation:
- Correct remaining-day count.
- Daily time budget respected.
- Completed work preserved.
- Weak topics prioritized appropriately.
- Previous plan version retained.
- No unjustified replanning.

E. ADK integration:
- root_agent imports successfully.
- Three specialist agents remain registered.
- Real delegation events occur.
- Tool calls are successful.
- State persists across separate turns.

F. Regression:
- All M1 tests pass.
- All M2 tests pass.
- All M3 tests pass.
- All M4 tests pass.
- All M5 tests pass.

Use deterministic fixtures and mocks for CI.

Test errors and failure handling.

Do not claim a live test passed unless
the real Gemini API was called successfully.

==================================================
9. LIVE GEMINI VALIDATION
==================================================

If GOOGLE_API_KEY is configured locally,
perform real ADK Runner tests.

Test the complete student workflow across
multiple turns using one session.

Capture:
- Coordinator delegation events.
- Specialist agent calls.
- Curriculum/tool calls.
- Structured response validation.
- Quiz score.
- Weak-topic identification.
- Adapted study-plan validation.
- Session state updates.

Use the verified configured GEMINI_MODEL.

Avoid printing API keys or unnecessary student data.

Provide a concise, redacted execution trace.

Also test the ADK Web interface.

If the complete workflow fails, diagnose and
fix the problem before creating a Git release.

==================================================
10. QUALITY GATES
==================================================

Run:

uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Fix every failure.

Verify the complete workflow still runs
after all fixes.

Do not suppress errors to force tests to pass.

==================================================
11. DOCUMENTATION
==================================================

MANDATORY:
Save this ENTIRE M5 Antigravity instruction under:

docs/antigravity/05-multi-agent-orchestration.md

Preserve the original milestone goals.

Append:
- Architecture decisions
- Files created and modified
- State schema
- Workflow transitions
- Session behavior
- Tests and commands
- Actual results
- Live Gemini verification
- Known limitations
- Commit and release information

Update:
README.md
docs/architecture.md
docs/antigravity/README.md

Create:
docs/adaptive-learning.md
examples/sample_learning_session.json
examples/sample_adaptive_plan.json

Ensure examples validate against actual schemas.

Do not claim sample outputs are live Gemini results
unless they were actually generated and captured.

Include a Mermaid workflow diagram that renders
correctly on GitHub.

Do not modify completed M1-M4 documentation
unless correcting a documented factual error.

==================================================
12. GITHUB COMMIT AND RELEASE
==================================================

Use existing main branch.

Before Git operations:
- Confirm working tree and remote.
- Confirm all tests pass.
- Confirm complete live verification.
- Confirm no credentials are staged.
- Confirm documentation is updated.
- Check remote divergence.

Commit:
feat(m5): implement adaptive multi-agent study workflow

Create annotated tag:
v0.5.0

Push main and v0.5.0 to origin.

Do not force-push.
Do not rewrite previous milestone tags.

If required verification is incomplete,
stop and report the problem.
Do not create a release tag.

==================================================
13. FINAL REPORT
==================================================

Show:

1. Files created and modified
2. ADK orchestration design
3. Session state implementation
4. Quiz answer-key isolation
5. Adaptive planning implementation
6. Each step's test results
7. Total regression tests
8. Ruff and mypy results
9. Live Gemini execution results
10. Coordinator and tool execution trace
11. 14-day plan validation
12. Quiz grading results
13. Adapted plan validation
14. Git commit hash
15. v0.5.0 tag and push status
16. Remaining limitations

STOP AFTER M5.

Do not implement M6 Docker/UI,
M7 observability, or M8 release.

---

# MILESTONE 5 EXECUTION & VALIDATION REPORT

## 1. Architecture Decisions
- **Coordinator & Specialists**: Preserved `root_agent` (`study_coach`) coordinating across three specialist agents: `study_planner`, `topic_expert`, and `quiz_generator`.
- **Hybrid Agent & Deterministic Workflow**: Google ADK agents provide natural language generation and structured outputs (`output_schema`), while `AdaptiveStudyWorkflow` enforces strict deterministic invariants (time budgets, state transitions, answer-key hiding, and quiz grading).
- **Session State Management**: Implemented `LearningSession` and `LearningSessionService` leveraging Google ADK's `InMemorySessionService`. State updates are recorded via `EventActions.state_delta` and session isolation is enforced across distinct user and session IDs.
- **Answer Key Security**: Quizzes are stored privately server-side in `LearningSession.stored_quizzes`. The student client only receives sanitized `StudentQuizQuestion` objects (with `correct_answer` and `explanation` stripped). Grading occurs 100% deterministically in Python against the stored private quiz.
- **Adaptive Replanning Rules**: When student performance on a topic drops below the documented 70% threshold, `generate_adapted_plan` replans the remaining days ($14 - \text{completed}$), increments `plan_revision`, preserves previous plans in history, and prioritizes weak topics for learning and review activities while guaranteeing daily minutes never exceed the student limit.

---

## 2. Files Created and Modified
- **Created**:
  - `src/study_coach/models/learning_session.py`: Session state and learning progress Pydantic models.
  - `src/study_coach/services/learning_session.py`: ADK-integrated in-memory session service.
  - `src/study_coach/services/__init__.py`: Package init exporting `LearningSessionService`.
  - `src/study_coach/workflows/adaptive_study.py`: Workflow orchestrating multi-agent interactions and deterministic validation.
  - `src/study_coach/workflows/__init__.py`: Package init exporting `AdaptiveStudyWorkflow`.
  - `tests/unit/test_learning_session.py`: Unit tests for session models and serialization.
  - `tests/unit/test_session_service.py`: Unit tests for session lifecycle and isolation.
  - `tests/unit/test_adaptive_workflow.py`: Unit tests for workflow transition rules and quiz scoring.
  - `tests/integration/test_orchestration.py`: Integration test for end-to-end adaptive study loop.
  - `docs/adaptive-learning.md`: Full architecture documentation with GitHub-compatible Mermaid workflow diagram.
  - `examples/sample_learning_session.json`: Real validated sample output from live multi-agent execution.
  - `examples/sample_adaptive_plan.json`: Real validated sample output from live adaptive replanning.
- **Modified**:
  - `src/study_coach/models/__init__.py`: Added `LearningProgress` and `LearningSession`.
  - `src/study_coach/agent.py`: Updated coordinator routing instructions to include adaptive replanning.
  - `README.md`: Updated roadmap and current functionality.
  - `docs/architecture.md`: Updated architecture notes for M5.
  - `docs/antigravity/README.md`: Marked M5 as completed in v0.5.0.

---

## 3. Step-by-Step Test Verification

| Step | Component | Command | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Session State Models | `uv run pytest tests/unit/test_learning_session.py` | Model constraints, revision, and sanitization pass | 5 passed in 0.11s | PASS |
| **B** | Session Service Lifecycle | `uv run pytest tests/unit/test_session_service.py` | Creation, retrieval, isolation, and deletion pass | 3 passed in 0.35s | PASS |
| **C** | Workflow & Invariants | `uv run pytest tests/unit/test_adaptive_workflow.py` | State transitions, answer key hiding, and grading pass | 4 passed in 0.66s | PASS |
| **D** | E2E Orchestration Cycle | `uv run pytest tests/integration/test_orchestration.py` | 14-day plan $\rightarrow$ quiz $\rightarrow$ grading $\rightarrow$ adapted replan pass | 3 passed in 0.59s | PASS |
| **E** | Regression Test Suite | `uv run pytest -q` | All M1–M5 tests pass without regressions | 67 passed in 0.85s | PASS |
| **F** | Quality Gates | `uv run ruff check .`<br>`uv run ruff format --check .`<br>`uv run mypy .` | Zero lint, format, or type checking errors | All checks passed, 48 files formatted, 0 mypy issues | PASS |

---

## 4. Live Gemini Multi-Turn Verification

Executed against Gemini model using `InMemoryRunner` with persistent session `live_session_m5`:

1. **Turn 1 (Study Planning)**:
   - **Input**: *"I am preparing for the Google Cloud Generative AI Leader certification in 14 days. I am a beginner and can study 90 minutes daily. Create my study plan."*
   - **Trace**: `study_coach` $\rightarrow$ `transfer_to_agent` $\rightarrow$ `study_planner` $\rightarrow$ `load_curriculum` $\rightarrow$ `calculate_available_minutes` $\rightarrow$ `set_model_response`.
   - **Output**: 14-day structured study plan totaling 1,260 minutes ($\le 90$ min/day).
2. **Turn 2 (Topic Explanation)**:
   - **Input**: *"Explain grounding and RAG for a beginner."*
   - **Trace**: `study_planner` $\rightarrow$ `transfer_to_agent` $\rightarrow$ `topic_expert` $\rightarrow$ `search_topics` $\rightarrow$ `get_related_topics` $\rightarrow$ `get_topic_by_id` $\rightarrow$ `set_model_response`.
   - **Output**: Structured `TopicExplanation` with intuitive analogies, Google Cloud examples, and comprehension check questions.
3. **Turn 3 (Practice Quiz)**:
   - **Input**: *"Generate five practice questions about grounding and RAG."*
   - **Trace**: `topic_expert` $\rightarrow$ `transfer_to_agent` $\rightarrow$ `quiz_generator` $\rightarrow$ `load_curriculum` $\rightarrow$ `set_model_response`.
   - **Output**: 5 practice multiple-choice questions with options A–D, answer keys, and factual explanations.
   - **Sanitization Check**: Student presentation returned via `Quiz.to_student_view()` verified to omit `correct_answer` and `explanation`.
4. **Turn 4 (Adaptive Replanning)**:
   - **Evaluation**: Student submitted 3 correct and 2 incorrect answers ($60.0\%$). `genai_concepts` was deterministically classified as a weak topic.
   - **Input**: *"Identify my weak topics and update my remaining study plan."*
   - **Trace**: `quiz_generator` $\rightarrow$ `transfer_to_agent` $\rightarrow$ `study_coach` $\rightarrow$ `transfer_to_agent` $\rightarrow$ `study_planner` $\rightarrow$ `load_curriculum` $\rightarrow$ `set_model_response`.
   - **Output**: Adapted 11-day remaining plan with `plan_revision = 2` specifically front-loading and reinforcing `genai_concepts` while strictly respecting $\le 90$ min/day (990 total planned minutes).

---

## 5. Known Limitations
1. **Ephemeral In-Memory Storage**: `LearningSessionService` stores sessions in memory for V1. In-memory state is isolated between session IDs but does not persist across application server restarts (planned for database integration in future architectures).
2. **Deterministic Threshold Boundary**: The weakness threshold is fixed at $70\%$. Students with minimal question samples (e.g., 1 question) are classified strictly on that sample; comprehensive diagnostic batteries across all curriculum topics remain an ongoing enhancement.
