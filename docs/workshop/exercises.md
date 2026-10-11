# Workshop Exercises & Hands-On Activities

These exercises provide practical hands-on tasks for workshop attendees, organized by core learning track and optional advanced extensions.

---

## Core Hands-On Exercises (During Workshop)

### Exercise 1: Build Your Custom Study Plan
- **Goal**: Generate a personalized certification schedule.
- **Task**:
  1. Set your experience level (e.g., `Intermediate`).
  2. Set your preparation timeframe (e.g., `7 days`).
  3. Set your daily study capacity (e.g., `45 minutes`).
  4. Generate your plan and inspect the daily activity breakdown.
- **Verification**: Verify that no individual day exceeds your chosen daily minute limit, and that all 7 days have sequential numbers.

### Exercise 2: Master a Core Topic & Complete Formative Quick Check
- **Goal**: Learn a technical topic with GCP architecture depth.
- **Task**:
  1. Open the **Learn Topic** tab and select `llm_architecture` or `prompt_engineering`.
  2. Review the structured lesson and the hands-on code sample.
  3. Navigate to the **Practice & Share** tab and take the 3-question **Quick Knowledge Check**.
  4. Review your score and detailed explanations for any missed questions.
- **Verification**: Confirm that your score is computed instantly and that explanations justify the correct answer choices.

### Exercise 3: Challenge Yourself with a Practice Quiz & Trigger Adaptive Replanning
- **Goal**: Experience closed-loop multi-agent adaptation.
- **Task**:
  1. Generate a 5-question practice quiz on your selected topic.
  2. Answer the questions and submit for grading.
  3. Note if any topic scored below 70% (weak topic).
  4. Navigate to the **Adaptive Plan** tab, specify 1 completed day, and generate Revision 2 of your plan.
- **Verification**: Observe that the newly generated plan reallocates study blocks to reinforce your diagnosed weak topic.

---

## Optional Advanced Exercises (Post-Workshop)

### Advanced Exercise 1: Inspect Agent Telemetry Spans
- **Goal**: Deepen understanding of distributed tracing in multi-agent workflows.
- **Task**:
  1. If running Docker observability, open `http://localhost:3000/explore`.
  2. Run a TraceQL query for `study_coach.explain_topic`.
  3. Locate the `generate_content` and `execute_tool` spans within the waterfall.
  4. Calculate what percentage of total workflow latency was spent in LLM inference vs Python tool execution.

### Advanced Exercise 2: Add a Custom Curriculum Topic
- **Goal**: Understand how the Study Coach is grounded in static curriculum data.
- **Task**:
  1. Open `src/study_coach/data/curriculum.yaml`.
  2. Add a new topic definition under the `topics` list (e.g., `multimodal_agents` with title, difficulty, and subtopics).
  3. Add corresponding resources in `src/study_coach/data/learning_resources.yaml`.
  4. Run `uv run pytest -q` to verify that existing schema validators accept your additions.
  5. Restart Streamlit and verify your new topic appears in the dropdown.

### Advanced Exercise 3: Run the CLI Evaluation Runner
- **Goal**: Execute automated regression evaluations from the command line.
- **Task**:
  1. Run the evaluation script:
     ```bash
     uv run python tests/eval/run_live_evaluation.py
     ```
  2. Inspect the generated summary report in `docs/reports/recent_evaluation_report.json`.
  3. Examine per-scenario latency and pass/fail assertion details.
