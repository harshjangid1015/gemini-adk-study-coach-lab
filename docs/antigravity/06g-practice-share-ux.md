# ANTIGRAVITY — M6-G: INTERACTIVE MCQS + PRACTICE & SHARE UX

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M6-G — Practice & Share Enhancement
BRANCH: main

## 1. Original Instructions

```text
# ANTIGRAVITY — M6-G: INTERACTIVE MCQS + PRACTICE & SHARE UX

You are a senior Python engineer, Google ADK specialist,
and Streamlit application developer.

PROJECT: gemini-adk-study-coach-lab
MILESTONE: M6-G — Practice & Share Enhancement
BRANCH: main

GOAL:
Improve the existing Learn Topic -> Practice & Share
experience by implementing interactive MCQs,
better quiz navigation, and reliable LinkedIn sharing.

Implement M6-G ONLY.
Do not start M7.

==================================================
1. INSPECT EXISTING IMPLEMENTATION
==================================================

Read:
- GEMINI.md
- README.md
- ui/app.py
- ui/components/
- src/study_coach/agent.py
- src/study_coach/agents/quiz_generator.py
- src/study_coach/models/quiz.py
- src/study_coach/tools/quiz_tools.py
- src/study_coach/services/workshop_facade.py
- src/study_coach/workflows/adaptive_study.py
- docs/antigravity/06f-resource-providers-sharing.md

Inspect real method signatures and existing state
handling before implementing changes.

Run:
uv run pytest -q

Record baseline test results.

Preserve all existing M1-M6 functionality.

==================================================
2. INTERACTIVE SELF-ASSESSMENT MCQS
==================================================

CURRENT ISSUE:
Learn Topic -> Practice & Share shows plain-text
self-assessment questions without answer options,
submission, scoring, or feedback.

REQUIRED:
Replace those plain-text questions with 3
interactive multiple-choice questions.

Example:
Selected topic: llm_architecture
Experience: Intermediate

Generate:
3 original topic-specific MCQs using the existing
Google ADK Quiz Generator Agent and Gemini.

Do not hardcode questions.

Reuse existing:
- Quiz
- QuizQuestion
- StudentQuizQuestion
- QuizSubmission
- QuizResult
- Quiz grading tools

Each question must have:
- Question text
- Four choices A/B/C/D
- Exactly one correct answer
- Explanation
- Valid curriculum topic ID

Use Streamlit st.radio for answer selection.

Provide:
- Generate Quick Check button
- Submit / Check Answers button
- Correct / incorrect feedback after submission
- Explanation for each question
- Optional Retry Quick Check button

Allow students to submit answers as one small
3-question formative check.

Do not reveal answers before submission.

==================================================
3. DETERMINISTIC SCORING
==================================================

Use existing Python grading:
grade_quiz()
calculate_score()

Never use Gemini to calculate the score.

For 3 questions:
3 correct -> 100%
2 correct -> 66.67%
1 correct -> 33.33%
0 correct -> 0%

Handle unanswered questions explicitly.

Quick Checks must remain formative:
- Do not automatically change the full quiz score.
- Do not modify weak-topic classifications.
- Do not trigger adaptive replanning.
- Do not overwrite existing formal quiz results.

Use private backend quiz state for answer keys.

Never trust student-submitted answer keys.

==================================================
4. STREAMLIT SESSION STATE
==================================================

Maintain:
- quick_check_quiz_id
- quick_check_questions
- quick_check_selections
- quick_check_result
- selected_topic_id

Use the existing backend session service for
private full quiz objects and answer keys.

Student-facing Streamlit state must contain only
sanitized questions, selections and public feedback.

Do not expose correct_answer or private explanations
before submission.

Ensure:
- Questions persist across Streamlit reruns.
- Selections persist while answering.
- Submission is processed once.
- Retry starts a fresh independent quick check.
- Changing topic invalidates stale quick checks.
- Student sessions remain isolated.

Use distinct state namespaces or backend records
so quick checks cannot overwrite full practice quizzes.

==================================================
5. PRACTICE QUIZ NAVIGATION
==================================================

CURRENT ISSUE:
"Open Practice Quiz for This Topic" only shows a
message telling students to switch tabs manually.

REQUIRED:
Improve the action.

On click:
- Preselect current topic in Practice Quiz.
- Navigate directly to Practice Quiz if supported
  by the installed Streamlit version.
- Preserve the current student session.

If direct tab switching is not officially supported,
use a supported navigation pattern, such as
st.navigation, st.segmented_control, or another
reliable controlled navigation mechanism.

Do not use brittle JavaScript or DOM manipulation.

Do not duplicate the existing Practice Quiz page.

Do not automatically generate a formal quiz
merely because the student navigated there.

==================================================
6. SHARE MY LEARNING
==================================================

Improve the existing LinkedIn sharing experience.

Current wording:
"Just completed my deep dive..."

Change default to:
"I'm learning about..."

The draft should include:
- Current learning topic
- Certification context
- Gemini + Google ADK Study Coach reference
- Relevant hashtags

Do not include:
- Quiz answers
- Private student information
- Session IDs
- Test scores by default

Provide:
- Editable LinkedIn post preview
- Reliable Copy Post mechanism or a clearly
  selectable copyable text field
- Open LinkedIn action
- Instructions to paste the text manually when
  LinkedIn does not support prefilled post text

Do not falsely claim LinkedIn prefill works.

Do not auto-publish.

Preserve all existing resource-sharing controls
implemented in M6-F.

==================================================
7. UI DESIGN
==================================================

Keep the existing dark Streamlit design.

Learn Topic -> Practice & Share should contain:

LEFT:
- Quick Knowledge Check
- 3 interactive MCQs
- Submit Answers
- Score + feedback after submission
- Retry Quick Check
- Start Full Practice Quiz

RIGHT:
- Share My Learning
- Editable LinkedIn preview
- Copy Post
- Open LinkedIn

Keep the layout compact and readable.

Avoid:
- Plain-text numbered questions with no controls
- Large empty containers
- Excessive scrolling
- Broken navigation
- Duplicated buttons
- Exposure of answer keys

==================================================
8. STEP-BY-STEP TESTING
==================================================

MANDATORY:
Follow GEMINI.md Rules 12 and 13.

Implement and test each component separately.
Fix failures before proceeding.

A. QUICK CHECK MODEL / STATE
- Generates exactly 3 questions.
- Four choices per question.
- Valid topic IDs.
- Beginner/intermediate/advanced compatibility.
- Topic change resets stale quiz state.
- Reruns preserve active questions.
- No cross-session leakage.

B. GRADING
- 3/3 = 100%.
- 2/3 approximately 66.67%.
- 1/3 approximately 33.33%.
- 0/3 = 0%.
- Unanswered question handling.
- Duplicate submission prevention.
- Correct and incorrect feedback.
- Answer-key isolation.

C. EXISTING QUIZ REGRESSION
- Full Practice Quiz still works.
- Existing scores remain unchanged.
- Weak-topic classification unchanged.
- Adaptive Plan remains functional.
- Quick Checks do not update formal quiz history.

D. NAVIGATION
- Correct topic preselected.
- Navigation works in real Streamlit.
- Session remains intact.
- No duplicate quiz generation.
- No unsupported JavaScript workaround.

E. SHARING
- Default text is accurate.
- Editable preview works.
- Copyable post text works.
- LinkedIn link opens.
- No automatic posting.
- No private data in shared text.

F. LIVE GEMINI
If GOOGLE_API_KEY is configured:
- Generate 3 actual Gemini MCQs.
- Confirm ADK Quiz Generator execution.
- Validate returned Quiz model.
- Render sanitized questions.
- Submit test answers.
- Verify deterministic scoring.

G. REGRESSION
All previous M1-M6 tests must pass.

==================================================
9. QUALITY GATES
==================================================

Run after each major implementation step
and again before Git:

uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Verify actual Streamlit browser behavior.

Do not claim UI success based solely on AppTest.

Test in Docker as well if available.

Do not hide failures or invent results.

==================================================
10. DOCUMENTATION
==================================================

MANDATORY:

Create:
docs/antigravity/06g-practice-share-ux.md

Archive THIS ENTIRE ORIGINAL INSTRUCTION verbatim,
not a summary.

Append:
- Architecture and implementation details
- Files created/modified
- Step-by-step test commands and actual results
- Live Gemini results
- Navigation verification
- Sharing verification
- Screenshots if available
- Known limitations
- Git commit and push status

Update:
docs/antigravity/README.md
README.md
docs/learning-experience.md

Preserve all previous M6 documentation.

==================================================
11. GITHUB CHECKPOINT
==================================================

Before committing:
- Confirm all required quality gates pass.
- Confirm full practice quiz regression passes.
- Confirm no secrets are staged.
- Confirm Git working tree and remote status.
- Preserve unrelated user changes.

Commit:

feat(m6): add interactive quick checks and improve sharing

Push:
origin/main

Do not force-push.
Do not modify v0.6.0 or previous tags.
Do not create v0.7.0.

If required acceptance checks fail or remain
unverified, stop and report blockers instead
of committing.

==================================================
12. FINAL REPORT
==================================================

Provide:

1. Files created or modified
2. Quick Check architecture
3. How answer keys are protected
4. Actual 3-question Gemini example
5. Deterministic grading results
6. Topic-selection behavior
7. Full Practice Quiz navigation verification
8. LinkedIn sharing verification
9. Step-by-step test results
10. Total passing pytest tests
11. Ruff and mypy results
12. Real Streamlit UI verification
13. Docker test results
14. Git commit hash and push status
15. Known limitations

STOP AFTER M6-G.

Do not implement M7 observability,
Grafana, OpenTelemetry, or future milestones.
```

---

## 2. Architecture & Implementation Details

### A. Quick Knowledge Check Architecture
- **Workflow (`AdaptiveStudyWorkflow`):** Added `generate_quick_check` and `evaluate_quick_check`. Generates exactly 3 MCQs calibrated to learner experience level and curriculum topic ID using Google ADK's `quiz_generator` Agent and Gemini.
- **Answer Key Protection:** The complete `Quiz` with answer keys (`correct_answer`) and explanations is securely persisted only in the backend session state under `session.stored_quizzes[qc_id]`. Only sanitized `StudentQuizQuestion` models (where `correct_answer` and `explanation` are absent) are returned to the client and Streamlit session state prior to evaluation.
- **Formative Isolation:** Quick check grading executes deterministically in pure Python (`grade_quiz`, zero LLM / zero network calls). Unlike formal practice quizzes, `evaluate_quick_check` does **not** mutate `session.quiz_results`, does **not** reclassify `session.weak_topics`, and does **not** increment `session.learning_progress`. Formal quiz history remains completely isolated.
- **Deterministic Scoring:** Uses `calculate_score(correct_count, 3)`:
  - 3/3 correct = 100.0%
  - 2/3 correct = 66.7%
  - 1/3 correct = 33.3%
  - 0/3 correct = 0.0%
  Unanswered questions default to incorrect.

### B. Streamlit Session State & Lifecycle
The following dedicated session state variables are tracked:
- `quick_check_quiz_id`: Server quiz ID identifier.
- `quick_check_questions`: Sanitized 3 questions.
- `quick_check_selections`: Real-time student choices (`A`, `B`, `C`, `D`).
- `quick_check_result`: Formative `QuizResult` containing question-by-question feedback.
- `selected_topic_id`: Active topic ID.
- `_prev_quick_check_topic_id`: Topic invalidation tracker. If the student switches topics in "Learn Topic", stale quick checks are automatically reset.

### C. Practice Quiz Navigation
- Configured Streamlit 1.65 native programmatic tab control on `st.tabs(..., key="main_nav_tab", on_change="rerun")`.
- When clicking "📝 Start Full Practice Quiz", the callback sets:
  ```python
  st.session_state.preselected_quiz_topic = chosen_topic_id
  st.session_state.main_nav_tab = "📝 Practice Quiz"
  st.session_state.quiz_topic_select = topic_label
  ```
- Because callbacks execute before widget instantiation, Streamlit directly navigates to the Practice Quiz tab with the exact topic preselected.
- Preserves the student session and requires zero brittle JavaScript or DOM hacks.

### D. Upgraded LinkedIn Sharing UX
- Updated default wording from `"Just completed my deep dive..."` to `"I'm learning about '{exp.topic_title}' as part of my preparation for the {certification_name} certification with Gemini & Google ADK Study Coach! #GoogleCloud #GenerativeAI #StudyCoach #GeminiADK #ContinuousLearning"`.
- Editable preview in `st.text_area`.
- One-click copyable block in `st.code`.
- Direct `st.link_button` to LinkedIn.
- Transparent notice explaining modern LinkedIn sharing URL restrictions and instructing the learner to paste manually.
- Strict privacy guarantee: Zero test scores, answers, or student tokens are included.

---

## 3. Files Created or Modified

1. `src/study_coach/workflows/adaptive_study.py` (Modified):
   - Added `generate_quick_check(session_id, user_id, topic_id, experience_level)` returning `(qc_id, list[StudentQuizQuestion])`.
   - Added `evaluate_quick_check(session_id, user_id, submission)` with pure Python deterministic evaluation and formative state isolation.
2. `src/study_coach/services/workshop_facade.py` (Modified):
   - Exposed `generate_quick_check` and `evaluate_quick_check` methods to the UI layer.
3. `ui/app.py` (Modified):
   - Wired `st.tabs` with key and change handler for seamless navigation.
   - Initialized M6-G session state keys.
   - Replaced plain-text comprehension check with the 2-column "Practice & Share" container (Left: 3 interactive MCQs with `st.radio`, submission, score banner, and feedback; Right: enhanced LinkedIn sharing with editable preview, copy block, and instructions).
   - Implemented `navigate_to_practice_quiz_callback` for instant tab switching with topic preselection.
4. `tests/unit/test_quick_check.py` (Created):
   - 12 comprehensive unit and AppTest tests covering models, scoring, isolation, UI rendering, submission, and navigation.
5. `docs/antigravity/06g-practice-share-ux.md` (Created):
   - Complete verbatim prompt archive and milestone implementation documentation.
6. `docs/antigravity/README.md` (Modified):
   - Added M6-G index entry and description.
7. `README.md` (Modified):
   - Updated feature set with M6-G Quick Knowledge Checks, tab navigation, and LinkedIn sharing.
8. `docs/learning-experience.md` (Modified):
   - Updated Practice & Share specifications.

---

## 4. Live Gemini ADK Execution Example

Executed live with `GOOGLE_API_KEY` configured against `gemini-2.5-flash`:

```text
Generated Quick Check ID: quick_check_llm_architecture_1
Question Count: 3

Q1 (q1): In the Transformer architecture powering modern Large Language Models (LLMs), what is the primary function of the self-attention mechanism?
  A) It calculates contextual relevance between all tokens in a sequence concurrently, capturing long-range semantic dependencies.
  B) It sequentially processes tokens one by one to preserve chronological order through internal hidden recurrent states.
  C) It compresses the entire input sequence into a single static fixed-length vector to minimize memory consumption.
  D) It randomly masks a subset of tokens during inference to prevent the model from overfitting to prompt instructions.

Q2 (q2): An organization wants to deploy a specialized customer support assistant using an LLM. Why would the engineering team choose to fine-tune an existing foundation model rather than pre-train a new model from scratch?
  A) Pre-training cannot handle natural language tasks, whereas fine-tuning introduces fundamental grammar and vocabulary.
  B) Fine-tuning adapts existing model parameters on a smaller, task-specific dataset, requiring vastly fewer compute resources than pre-training from scratch.
  C) Fine-tuning locks all model parameters permanently so the model can only retrieve responses from an exact predefined script.
  D) Pre-training requires continuous human-annotated labeling for billions of tokens, whereas fine-tuning is entirely unsupervised.

Q3 (q3): A practitioner observes that a foundation model occasionally returns unwanted conversational text instead of valid JSON when using zero-shot prompting. Which prompt engineering technique is best suited to guide the model toward the exact output format without modifying model weights?
  A) Reinforcement Learning from Human Feedback (RLHF)
  B) Low-Rank Adaptation (LoRA)
  C) Few-shot prompting
  D) Full parameter fine-tuning

Server-side Answer Keys (protected):
  q1: A -> The self-attention mechanism is a cornerstone of the Transformer...
  q2: B -> Foundation model pre-training requires massive computational...
  q3: C -> Few-shot prompting provides the model with a few input-output...

Deterministic Evaluation Result (1 correct, 1 incorrect, 1 unanswered):
  Total Questions: 3
  Correct: 1
  Score Percentage: 33.3%
```

---

## 5. Validation Commands and Actual Results

### Quality Gate 1: Ruff Lint Check
```bash
uv run ruff check .
```
Output:
```text
All checks passed!
```

### Quality Gate 2: Ruff Format Check
```bash
uv run ruff format --check .
```
Output:
```text
79 files already formatted
```

### Quality Gate 3: Mypy Static Type Analysis
```bash
uv run mypy .
```
Output:
```text
Success: no issues found in 58 source files
```

### Quality Gate 4: Pytest Suite
```bash
uv run pytest -q
```
Output:
```text
........................................................................ [ 65%]
......................................                                   [100%]
110 passed in 2.34s
```

### Quality Gate 5: Docker Container Build
```bash
docker compose build
```
Output:
```text
[+] build 1/1
 ✔ Image gemini-adk-study-coach-lab-study-coach-ui Built                    1.6s
```

---

## 6. Known Limitations
1. **LinkedIn Open Graph Sharing API:** LinkedIn does not permit third-party web apps to pre-fill the text field when opening external share windows. The application clearly explains this to students and provides a one-click copyable markdown block to paste directly into LinkedIn.
2. **Offline Fallback for Quick Checks:** Generating original quick checks requires internet connectivity and valid Gemini API credentials (`GOOGLE_API_KEY`). If credentials are not present, an informational error guides the student to configure `.env`.
3. **M7 Features:** Observability, OpenTelemetry, Grafana dashboards, and multi-user production telemetry are deferred to subsequent milestones.

---

## 7. Git Checkpoint Status
- Branch: `main`
- Commit Message: `feat(m6): add interactive quick checks and improve sharing`
- Prior tags (`v0.6.0`, etc.) preserved without alteration.
