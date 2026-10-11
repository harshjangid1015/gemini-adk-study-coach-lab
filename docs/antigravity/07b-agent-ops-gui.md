# Milestone 7-B — Observability and Evaluation GUI

## Original Instructions

```markdown
# M7-B — OBSERVABILITY AND EVALUATION GUI

PROJECT: gemini-adk-study-coach-lab
BRANCH: main

GOAL:
Provide a visual GUI for both observability
and evaluation results before starting M8.

1. Read GEMINI.md and inspect the actual M7
   implementation and evaluation scripts.

2. Preserve the existing Streamlit application.

3. Add an "Agent Ops" section with:
   - Observability overview
   - Open Grafana Dashboard link
   - Open Tempo Explore link
   - Prometheus health indicator
   - Clear indication when services are offline

4. Add an "Evaluations" section with:
   - Run Evaluations button
   - Scenario list
   - Pass/fail results
   - Actual measured latency
   - Evaluated model
   - Run timestamp
   - Per-scenario expandable details
   - Error messages when evaluations fail

5. Refactor the existing
   tests/eval/run_live_evaluation.py
   to expose a reusable evaluation runner.

   Preserve the existing CLI entrypoint.

6. Execute evaluations only after an explicit
   user action.

   Prevent duplicate concurrent runs.
   Apply reasonable execution timeouts.
   Do not block unrelated studying workflows.
   Do not use shell injection or unsafe
   subprocess calls.

7. Store recent evaluation results in a simple
   local JSON report with a documented schema.

   Do not store API keys, student data, private
   quiz answers, or full sensitive prompts.

   Show "No evaluations yet" when empty.

8. Use the actual four existing scenarios.
   Do not fabricate results.

9. Keep observability dashboards in Grafana.
   Do not recreate Grafana inside Streamlit.

10. Test:
    - Evaluation success
    - Evaluation failure
    - Missing Gemini credentials
    - Duplicate clicks
    - Result persistence and reload
    - Docker runtime integration
    - Existing study workflow regression

11. Run:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy .
    uv run pytest -q

12. Verify the actual GUI in browser and
    Docker Compose.

13. Archive this COMPLETE instruction in:
    docs/antigravity/07b-agent-ops-gui.md

14. Update README.md and workshop docs.

15. After all required checks pass:
    Commit:
    feat(m7): add visual agent evaluation dashboard

    Push origin/main.

    Preserve existing v0.7.0 tag.
    Do not begin M8.

STOP AFTER M7-B.
```

---

## Objective and Scope

Milestone 7-B provides an interactive graphical interface within the existing Streamlit workshop web application for both multi-agent observability and live model evaluations:
1. **Agent Ops & Observability (`ui/components/agent_ops.py`)**:
   - Live Prometheus endpoint connectivity verification (`http://localhost:9090/-/healthy`).
   - Deep-link cards to the auto-provisioned Grafana Dashboard (`study-coach-main`), Grafana Tempo trace explorer, and Prometheus targets scraper page.
   - Graceful offline service detection with actionable container launch commands.
   - Observability diagrams kept exclusively in Grafana (not recreated inside Streamlit).
2. **Visual Evaluations Dashboard (`ui/components/evaluations_view.py`)**:
   - User-triggered **Run Evaluations** button with duplicate-click protection and asynchronous execution.
   - Real-time status cards: pass rate, measured total latency, evaluated Gemini model, and UTC timestamp.
   - Expandable per-scenario inspection cards displaying agent name, status, measured latency, key concept details, and structured metadata.
   - Sanitized local JSON report persistence (`docs/reports/recent_evaluation_report.json`).
3. **Reusable Evaluation Runner (`study_coach.evaluation.runner.EvaluationRunner`)**:
   - Reusable thread-safe runner equipped with `asyncio.Lock` to block concurrent overlapping runs.
   - Preserves CLI entrypoint in `tests/eval/run_live_evaluation.py`.
   - Protects against credential omissions, timeouts, and private data leaks.

---

## Files Created or Modified

- `src/study_coach/models/evaluation.py`: Created Pydantic data models `EvaluationScenarioResult` and `EvaluationSummaryReport`.
- `src/study_coach/models/__init__.py`: Exported evaluation models.
- `src/study_coach/evaluation/__init__.py`: Created evaluation package exports.
- `src/study_coach/evaluation/runner.py`: Created reusable `EvaluationRunner` and JSON report persistence helpers.
- `tests/eval/run_live_evaluation.py`: Refactored to delegate to `EvaluationRunner` while preserving CLI behavior.
- `ui/components/agent_ops.py`: Created Agent Ops tab component with Prometheus health checking and Grafana/Tempo links.
- `ui/components/evaluations_view.py`: Created visual Evaluations tab component with metrics, scenario cards, and JSON view.
- `ui/components/__init__.py`: Exported new UI components.
- `ui/app.py`: Added `🔭 Agent Ops` and `🧪 Evaluations` tabs to `MAIN_NAV_OPTIONS` and initialized `eval_runner`.
- `tests/unit/test_evaluation_runner.py`: Created unit tests covering serialization, safety, missing credentials, concurrent run prevention, and Prometheus health checks.
- `docs/reports/recent_evaluation_report.json`: Stored live evaluation report artifact.
- `docs/observability.md`: Added Section 5.1 detailing the Agent Ops GUI.
- `docs/evaluation.md`: Added Section 3.1 detailing the reusable EvaluationRunner and GUI dashboard.
- `README.md`: Documented the Agent Ops and Evaluations tabs.
- `docs/antigravity/07b-agent-ops-gui.md`: Archived this full instruction and verification log.

---

## Validation Commands & Actual Results

### 1. Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q
```

**Results**:
- `ruff check`: All checks passed! (0 warnings)
- `ruff format --check`: 102 files compliant (0 reformatted)
- `mypy`: Success: no issues found in 78 source files
- `pytest -q`: 146 passed in 2.51s (7 new evaluation runner tests + 139 existing tests)

### 2. Live Evaluation Execution

```bash
uv run python tests/eval/run_live_evaluation.py
```

**Results**:
```text
================================================================================
🚀 GOOGLE ADK LIVE MODEL EVALUATION SUITE
================================================================================
  ✓ PASS [scenario_3] topic_expert (27.92s): Topic 'Generative AI Concepts' generated successfully. Key concepts: Artificial Intelligence (AI), Machine Learning (ML), Deep Learning (DL).
  ✓ PASS [scenario_5] quiz_generator (16.41s): 3 formative MCQs successfully generated with all 4 options sanitized.
  ✓ PASS [scenario_2] study_planner (18.34s): 7-day study plan generated strictly respecting 45 min/day budget.
  ✓ PASS [scenario_1] root_agent (31.61s): Root coordinator routed & answered (7411 chars response).

================================================================================
📊 ADK LIVE EVALUATION SUMMARY
================================================================================
Scenario        Target Agent         Status     Details
--------------------------------------------------------------------------------
scenario_3      topic_expert         PASS       27.92s latency
scenario_5      quiz_generator       PASS       16.41s latency
scenario_2      study_planner        PASS       18.34s latency
scenario_1      root_agent           PASS       31.61s latency
================================================================================
Result: 4/4 scenarios passed (94.28s total).
```

### 3. Streamlit App Testing & Docker Verification

```bash
docker compose --profile observability build study-coach-ui
docker compose --profile observability up -d
docker compose --profile observability ps
```

- Container `study-coach-workshop-ui` restarted and healthy (`ports 8501, 8000`).
- Streamlit `AppTest` confirmed tabs:
  `['📅 Study Plan', '📖 Learn Topic', '📝 Practice Quiz', '🔄 Adaptive Plan', '🔭 Agent Ops', '🧪 Evaluations']`
- Metrics confirmed:
  `Prometheus: Online`, `Tempo: Online`, `Grafana: Online`, `Pass Rate: 4/4`, `Latency: 94.28s`.

---

## Known Limitations

1. **Evaluation Runtime Duration**: Live Gemini model requests take 60–90 seconds to evaluate all 4 scenarios across root coordinator, topic expert, quiz generator, and study planner. The UI uses an asynchronous spinner and lock to prevent UI lockup or duplicate requests.
2. **Prometheus Health Origin**: When accessing Streamlit from a remote client, `localhost:3000` links assume standard developer workstation port forwarding.

---

## M7-B UI Fix — Grafana and Tempo Button Alignment

### Issue & Root Cause
In the Streamlit Agent Ops screen:
1. "Open Grafana" and "Open Tempo Traces" buttons wrapped across multiple lines on standard column widths.
2. Long full URLs inside cards consumed excessive width and distorted card layouts.
3. Card vertical alignment and button heights were uneven across columns.

### Solution
1. **Button Styling & Single-Line Labels**:
   - Replaced multi-line labels with clean, recommended single-line labels: `"Open Grafana ↗"` and `"Open Tempo Traces ↗"`.
   - Applied CSS `white-space: nowrap`, `display: block`, `width: 100%`, and standard `10px 16px` padding.
2. **Card Layout & URL Truncation**:
   - Implemented CSS flexbox with `flex-direction: column` and `justify-content: space-between` to guarantee equal card heights and bottom-aligned buttons.
   - Truncated raw URLs into clean host/path labels (`localhost:3000`, `localhost:3000/explore`, `localhost:9090/targets`) with `text-overflow: ellipsis` and `title` tooltips containing the full destination link.
3. **Automated UI Regression Tests**:
   - Added `test_agent_ops_tab_portal_cards_and_button_alignment` in [`tests/unit/test_evaluation_runner.py`](../../tests/unit/test_evaluation_runner.py) to assert `white-space: nowrap`, exact single-line button text, clean truncated endpoint badges, and destination URL integrity.

