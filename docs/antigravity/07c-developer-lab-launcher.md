# Milestone 7-C — Unified Local Developer Lab Launcher

## Original Instructions

```markdown
# M7-C — UNIFIED LOCAL DEVELOPER LAB LAUNCHER

PROJECT: gemini-adk-study-coach-lab
BRANCH: main

GOAL:
When I run ./scripts/run_local.sh, give me
a convenient first GUI from which I can open:

1. Google ADK Developer UI
2. Streamlit Study Coach
3. Streamlit Agent Ops tab
4. Streamlit Evaluations tab
5. Grafana dashboard
6. Grafana Tempo Explore
7. Prometheus

CURRENT:
./scripts/run_local.sh starts Google ADK Developer UI
on http://127.0.0.1:8000.

The Docker Study Coach exposes Prometheus metrics
on port 8000, so avoid conflicting local services.

REQUIREMENTS:

1. Read GEMINI.md, scripts/run_local.sh,
   Docker Compose, Streamlit navigation and
   all existing M7-B implementation.

2. Do not modify Google's installed ADK package.

3. Create a lightweight local Developer Lab
   launcher UI with clickable application links.

4. Provide status indicators based on actual
   health checks, not assumed running states.

5. Configure ports clearly.
   Keep the ADK UI on 8000 if available,
   otherwise show an actionable port warning.

   Use documented configurable URLs for:
   ADK UI, Study Coach, Agent Ops, Evaluations,
   Grafana, Tempo and Prometheus.

6. For Streamlit Agent Ops and Evaluations,
   implement supported direct navigation to
   the correct tabs using Streamlit session
   state or URL query parameters.

   Do not rely on fragile browser DOM scripts.

7. Update scripts/run_local.sh so I can start
   the local developer lab conveniently.

   Do not automatically start duplicate Docker
   services or conflicting metric servers.

   Preserve the existing ADK-only workflow
   through a documented flag or separate script.

8. Do not modify the Streamlit evaluation runner
   or agent logic unless required for navigation.

9. Run tests for:
   - Launcher links
   - Service health
   - Offline service behavior
   - Correct direct tab navigation
   - Port conflicts
   - Existing Study Coach functionality

10. Run:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy .
    uv run pytest -q

11. Verify the launcher in a real browser and
    confirm links open the correct interfaces.

12. Archive this COMPLETE command in:
    docs/antigravity/07c-developer-lab-launcher.md

13. Update README and workshop documentation.

14. Commit and push after validation:

    feat(m7): add unified developer lab launcher

    Do not move v0.7.0.
    Do not start M8.

STOP AFTER M7-C.
```

---

## Objective and Scope

Milestone 7-C creates a convenient, unified Developer Lab Launcher GUI providing one-click access and real-time health telemetry across the entire multi-agent ecosystem:
1. **Developer Lab Launcher GUI (`ui/launcher_app.py`)**:
   - Runs on dedicated port `8500`, preventing conflicts with Google ADK UI (`port 8000`), Streamlit Study Coach (`port 8501`), Grafana (`port 3000`), Tempo (`port 3200`), and Prometheus (`port 9090`).
   - Evaluates real HTTP/TCP socket connectivity for all 7 services.
   - Provides clean card launchers with direct URLs and action buttons.
2. **Supported Direct Tab Navigation (`ui/app.py`)**:
   - Implemented native `st.query_params` routing (`?tab=ops` and `?tab=eval`).
   - Safely updates Streamlit session state tab selection without fragile client DOM scripting.
3. **Launcher Service (`src/study_coach/services/launcher.py`)**:
   - Pydantic model `ServiceEndpoint` holding metadata, URLs, and status.
   - Socket and HTTP check utilities with graceful timeouts and exception handling.
4. **Enhanced Launcher Script (`scripts/run_local.sh`)**:
   - Defaults to launching the Developer Lab Launcher on `http://localhost:8500`.
   - Supports `--adk-only` flag to preserve standalone Google ADK Developer UI startup (`uv run adk web`).
   - Supports `--port <PORT>` to bind the launcher to custom ports.

---

## Files Created or Modified

- `src/study_coach/services/launcher.py`: Service checking live HTTP/TCP health and defining default lab endpoints.
- `ui/launcher_app.py`: Streamlit launcher application rendering service status cards and quick navigation links.
- `ui/app.py`: Added `TAB_QUERY_PARAM_MAP` and query parameter synchronization for direct URL tab routing (`?tab=ops`, `?tab=eval`).
- `scripts/run_local.sh`: Updated entrypoint script supporting both unified launcher and `--adk-only` standalone mode.
- `tests/unit/test_launcher.py`: Added 9 unit tests covering service configuration, HTTP/TCP health checks, AppTest UI rendering, and direct query parameter tab navigation.
- `README.md`: Updated Local Developer Lab Launch section and command examples.
- `docs/antigravity/07c-developer-lab-launcher.md`: Archived full original instructions, scope, validation, and limitations.

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
- `ruff format --check`: 106 files compliant (0 reformatted)
- `mypy`: Success: no issues found in 81 source files
- `pytest -q`: 155 passed in 2.57s (9 new launcher tests + 146 existing tests)

### 2. Direct Tab Navigation Verification

```bash
uv run python -c "
from streamlit.testing.v1 import AppTest
at_ops = AppTest.from_file('ui/app.py')
at_ops.query_params['tab'] = 'ops'
at_ops.run()
assert at_ops.session_state.get('main_nav_tab') == '🔭 Agent Ops'

at_eval = AppTest.from_file('ui/app.py')
at_eval.query_params['tab'] = 'eval'
at_eval.run()
assert at_eval.session_state.get('main_nav_tab') == '🧪 Evaluations'
print('Direct query navigation verified!')
"
```
**Result**: Direct query navigation verified!

### 3. Launcher Health Checks Verification

```bash
uv run python -c "
from study_coach.services.launcher import get_all_services_status
for s in get_all_services_status():
    print(f'{s.name:<30} {s.status_detail:<25} {s.url}')
"
```
**Result**:
- Google ADK Developer UI: `Online (Port 8000)`
- Streamlit Study Coach: `Online (Port 8501)`
- Streamlit Agent Ops: `Online (Port 8501/?tab=ops)`
- Streamlit Evaluations: `Online (Port 8501/?tab=eval)`
- Grafana Dashboard: `Online (Port 3000)`
- Grafana Tempo Explore: `Online (Port 3200)`
- Prometheus Scraper & TSDB: `Online (Port 9090)`

---

## Known Limitations

1. **Local Host Binding**: Service links default to `http://localhost:<PORT>` and `http://127.0.0.1:<PORT>`. If accessed over a network tunnel or remote machine, port forwarding or URL overriding is required.
2. **ADK Web Multi-Agent Loading**: The Google ADK Developer UI (`adk web`) inspects agents in the current directory and requires `uv run adk web` execution from the project root.
