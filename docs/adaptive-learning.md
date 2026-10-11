# Adaptive Learning Workflow

This document explains the multi-agent adaptive study architecture implemented in **Milestone 5 (M5)** of the `gemini-adk-study-coach-lab`.

---

## 1. Overview and Design Principles

The Adaptive Learning system couples Google Agent Development Kit (ADK) multi-agent capabilities with deterministic Python validation:
1. **Gemini** reasons, crafts pedagogically sound schedules, explains concepts, and writes practice items.
2. **Deterministic Python** grades answers, evaluates percentages, identifies weak learning topics, enforces time budgets, and governs session state transitions.
3. **Answer Key Protection**: Student-facing presentations are sanitized via [`Quiz.to_student_view()`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/models/quiz.py#L142), stripping correct answers and explanations until after submission.
4. **Isolated Ephemeral Sessions**: Managed by [`LearningSessionService`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/services/learning_session.py) atop Google ADK's `InMemorySessionService`.

---

## 2. Architecture & Workflow Diagram

```mermaid
flowchart TD
    Student(["Student"]) -->|Goal: 14 Days, 90 min/day| RootAgent["root_agent (study_coach)"]
    RootAgent -->|Delegates initial plan| StudyPlanner["study_planner"]
    StudyPlanner -->|Structured StudyPlan| PydanticVal["validate_study_plan()"]
    PydanticVal -->|Saves Plan Rev 1| SessionState[("LearningSession State")]

    Student -->|Learn Topic| RootAgent
    RootAgent -->|Delegates explanation| TopicExpert["topic_expert"]
    TopicExpert -->|TopicExplanation| Student

    Student -->|Generate Practice Quiz| RootAgent
    RootAgent -->|Delegates quiz| QuizGen["quiz_generator"]
    QuizGen -->|Full Quiz with Answers| SessionStore[("Private Session Quizzes")]
    SessionStore -->|Sanitized Questions| Student

    Student -->|Submits Answers| Workflow["AdaptiveStudyWorkflow"]
    Workflow -->|grade_quiz()| PythonGrader["Deterministic Python Grading (0 LLM / 0 Net)"]
    PythonGrader -->|Score & Weak Topics| SessionState

    Student -->|Update Study Plan| RootAgent
    RootAgent -->|Replan with Weak Topics| StudyPlanner
    StudyPlanner -->|Adapted StudyPlan| TimeBudgetVal["Time Budget & Day Validator"]
    TimeBudgetVal -->|Saves Plan Rev 2| SessionState
    SessionState -->|Adapted Schedule| Student
```

---

## 3. Workflow State Transitions

The [`AdaptiveStudyWorkflow`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/workflows/adaptive_study.py) controls transitions and enforces invariants:

1. **`create_initial_plan()`**:
   - Calls `study_planner` via Google ADK.
   - Validates that days equal the student's exam target and daily hours respect the student's time budget.
   - Records plan as `plan_revision = 1`.
2. **`generate_practice_quiz()`**:
   - Calls `quiz_generator` grounded in the curriculum.
   - Stores the full answer key securely in `stored_quizzes`.
   - Returns only `StudentQuizQuestion` list to the caller.
3. **`submit_quiz_answers()`**:
   - Rejects submissions if no quiz exists or if unknown `quiz_id` is passed.
   - Evaluates answers using deterministic Python `grade_quiz()`.
   - Classifies topics $< 70\%$ as weak and $\ge 70\%$ as strong.
   - Updates `LearningProgress` metrics.
4. **`generate_adapted_plan()`**:
   - Requires valid quiz results with evidence; rejects baseless replanning.
   - Preserves completed days ($14 - \text{completed}$).
   - Constrains daily budget ($\le 90$ minutes).
   - Re-runs `study_planner` prioritizing weak topics.
   - Increments `plan_revision` and maintains full plan history.

---

## 4. Session Storage & Security

- **Session State Model**: [`LearningSession`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/models/learning_session.py) holds profile, plan history, private quiz keys, and progress.
- **Answer Key Security**: Correct answers and private explanations are never passed to the student client prior to submission.
- **Trace Transparency**: ADK internal logs/traces are developer debug outputs, not student-facing interfaces.
- **In-Memory Notice**: The current V1 implementation stores sessions in memory. Data is isolated per session ID but is ephemeral across process restarts.
