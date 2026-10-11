# Milestone 7: Observability and Evaluation

## Goals
Add observability using ADK integrations and evaluate agent responses.

## Deliverables
- Telemetry configuration.
- Agent evaluation tests.

## Acceptance Criteria
- [x] Telemetry data is successfully exported.

---

## Full Antigravity Instructions

```
# M7 — RECOVER AND FINISH DOCKER OBSERVABILITY

PROJECT: gemini-adk-study-coach-lab
BRANCH: main

We are continuing M7, NOT starting again.

Previous state:
- 139 pytest tests passed.
- Ruff and mypy passed.
- OpenTelemetry instrumentation implemented.
- Tempo tracing previously verified.
- Docker failed during integration because
  the Mac ran out of disk space.
- No confirmed M7 release tag yet.

I have restarted Docker using:
docker compose up -d --build

IMPORTANT:
The observability services are configured
under Docker Compose profile "observability".

TASK:

1. Read GEMINI.md and existing M7 code/docs.
2. Inspect git status and free disk space.
3. Preserve all existing uncommitted changes.
4. Inspect Docker Compose services and profiles.

5. Run:
   docker compose --profile observability config
   docker compose --profile observability up -d --build
   docker compose --profile observability ps

6. Diagnose any failed or restarting containers
   using actual Docker logs.

7. Verify all five services:
   - Streamlit Study Coach
   - OpenTelemetry Collector
   - Grafana Tempo
   - Prometheus
   - Grafana

8. Run a REAL Gemini ADK request through
   the instrumented Study Coach application.

9. Verify:
   - OTLP telemetry reaches Collector.
   - Trace appears in Tempo with agent spans.
   - Prometheus target is UP.
   - Actual study_coach metrics exist.
   - Grafana dashboard panels have real data.
   - No sensitive prompts, API keys or private
     quiz answer keys are exported.

10. Run real ADK evaluation tests separately
    from deterministic pytest contract tests.
    Inspect installed ADK evaluation API first.

11. Run:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy .
    uv run pytest -q

12. Complete M7 docs:
    docs/antigravity/07-observability-evaluation.md
    docs/observability.md
    docs/evaluation.md
    README.md

13. Only after all acceptance checks pass:
    Commit M7 implementation.
    Create annotated v0.7.0 tag.
    Push main and v0.7.0.

14. Report:
    - Docker services and status
    - Actual error causes and fixes
    - Trace evidence
    - Prometheus metrics
    - Grafana dashboard verification
    - Evaluation results
    - Test count
    - Git commit and tag status
```

---

## Objective and Scope

Provide end-to-end observability, distributed tracing, metrics harvesting, visualization dashboards, and evaluation suites for the multi-agent AI Study Coach application:
1. **OpenTelemetry Tracing**: Implement `ADKObservabilityPlugin` bridging Google ADK agents and tools to OpenTelemetry spans, alongside `@trace_workflow_step` measuring high-level workflow latencies.
2. **Prometheus Metrics**: Expose application metrics on port 8000 with pre-initialized metric labels for immediate, zero-delay scraping.
3. **Telemetry Pipeline in Docker**: Configure OpenTelemetry Collector (`otel/opentelemetry-collector-contrib:0.111.0`), Grafana Tempo (`grafana/tempo:2.6.1`), Prometheus (`prom/prometheus:v2.54.1`), and Grafana (`grafana/grafana:11.2.0`) orchestrated under Docker Compose profile `observability`.
4. **Grafana Dashboards**: Auto-provision datasources (Prometheus, Tempo) and a rich 11-panel dashboard displaying workflow requests, latencies, agent calls, tool invocations, quiz submissions, and replanning events.
5. **Agent Evaluation Suite**: Separate deterministic pytest contract tests (19 tests) from live ADK model evaluations against real Gemini models (4 scenarios), verifying schema compliance, question quality, constraints, and latency.
6. **Privacy & Security**: Enforce API key redaction (`[REDACTED_API_KEY]`), answer-key protection before submission, and zero student PII leakage.

---

## Files Created or Modified

| File | Type | Description |
|---|---|---|
| `docker-compose.yml` | Modified | Added `otel-collector`, `tempo`, `prometheus`, and `grafana` services under profile `observability`; added port 8000 and OTLP env vars to `study-coach-ui` |
| `Dockerfile` | Modified | Exposed port 8000; set `ENTRYPOINT ["python", "ui/server.py"]` to start observability before accepting traffic |
| `ui/server.py` | Created | Server bootstrapper initializing `setup_tracing()` and `start_metrics_server()` before launching Streamlit |
| `src/study_coach/observability/config.py` | Modified | Configured `metrics_port` defaulting to 8000 |
| `src/study_coach/observability/metrics.py` | Modified | Added `init_metrics()` pre-registering label vectors on boot; allowed default port fallback from config |
| `src/study_coach/observability/instrumentation.py` | Modified / Created | Google ADK `BasePlugin` and `@trace_workflow_step` decorator |
| `src/study_coach/observability/tracing.py` | Created | OTLP TracerProvider initialization and graceful shutdown handling |
| `src/study_coach/services/workshop_facade.py` | Modified | Injected `ADKObservabilityPlugin` into runner; decorated `explain_topic` |
| `src/study_coach/workflows/adaptive_study.py` | Modified | Instrumented workflow methods with tracing and metric counters |
| `observability/otel-collector.yaml` | Created | Collector pipeline receiving OTLP gRPC/HTTP, exporting to Tempo and Prometheus |
| `observability/prometheus.yml` | Created | Scrape configuration targeting `study-coach-ui:8000` and `otel-collector:8889` |
| `observability/tempo.yaml` | Created | Local storage configuration for Grafana Tempo |
| `observability/grafana/provisioning/datasources/datasources.yaml` | Created | Auto-provisioning for Prometheus and Tempo datasources |
| `observability/grafana/provisioning/dashboards/dashboards.yaml` | Created | Dashboard provider pointing to `/var/lib/grafana/dashboards` |
| `observability/dashboards/study-coach-dashboard.json` | Created | Production Grafana dashboard with 11 panels |
| `tests/eval/fixtures/evaluation_scenarios.json` | Created | 10 evaluation scenarios for study planning, explaining, quizzing, and routing |
| `tests/eval/test_adaptive_workflow_evaluation.py` | Created | Deterministic evaluation of grading and replanning |
| `tests/eval/test_agent_routing.py` | Created | Deterministic evaluation of agent delegation and keyword routing |
| `tests/eval/test_planner_evaluation.py` | Created | Deterministic evaluation of daily budgets and calendar constraints |
| `tests/eval/test_quiz_evaluation.py` | Created | Deterministic evaluation of question counts, option structures, and key protection |
| `tests/eval/test_topic_expert_evaluation.py` | Created | Deterministic evaluation of curriculum alignment and schema compliance |
| `tests/eval/run_live_evaluation.py` | Created | Live Gemini ADK agent evaluation suite across 4 representative scenarios |
| `tests/unit/test_observability.py` | Created | Unit tests for configuration, redaction, and plugin lifecycle |
| `tests/unit/test_resilience_observability.py` | Created | Failure scenarios: unreachable collector, broken tracer, error propagation |
| `docs/observability.md` | Created | End-to-end architecture, configuration, and security documentation |
| `docs/evaluation.md` | Created | Evaluation methodology, dataset specifications, ADK API analysis, and live results |
| `README.md` | Modified | Updated milestone status and instructions for running observability |

---

## Validation Commands and Results

### 1. Docker Compose Services

```bash
docker compose --profile observability config
docker compose --profile observability up -d --build
docker compose --profile observability ps
```

**Output**:
```
NAME                         IMAGE                                          STATUS                    PORTS
study-coach-grafana          grafana/grafana:11.2.0                         Up 23 minutes             0.0.0.0:3000->3000/tcp
study-coach-otel-collector   otel/opentelemetry-collector-contrib:0.111.0   Up 23 minutes             0.0.0.0:4317-4318->4317-4318/tcp, 0.0.0.0:8889->8889/tcp
study-coach-prometheus       prom/prometheus:v2.54.1                        Up 23 minutes             0.0.0.0:9090->9090/tcp
study-coach-tempo            grafana/tempo:2.6.1                            Up 23 minutes             0.0.0.0:3200->3200/tcp
study-coach-workshop-ui      gemini-adk-study-coach-lab-study-coach-ui      Up (healthy)              0.0.0.0:8000->8000/tcp, 0.0.0.0:8501->8501/tcp
```

### 2. Live Prometheus Metrics Endpoint

```bash
curl -s http://localhost:8000/metrics | grep study_coach
```

**Output**:
```
# HELP study_coach_requests_total Total incoming user requests across all workflows.
# TYPE study_coach_requests_total counter
study_coach_requests_total{status="success",workflow="topic_explanation"} 0.0
study_coach_requests_total{status="success",workflow="study_plan_generation"} 0.0
study_coach_requests_total{status="success",workflow="quiz_generation"} 0.0
study_coach_requests_total{status="success",workflow="quiz_grading"} 0.0
# HELP study_coach_agent_calls_total Total invocations of Google ADK specialized agents.
# TYPE study_coach_agent_calls_total counter
study_coach_agent_calls_total{agent="topic_expert",model="gemini-3.8-flash"} 0.0
study_coach_agent_calls_total{agent="study_planner",model="gemini-3.8-flash"} 0.0
study_coach_agent_calls_total{agent="quiz_generator",model="gemini-3.8-flash"} 0.0
# HELP study_coach_tool_calls_total Total invocations of deterministic curriculum and grading tools.
# TYPE study_coach_tool_calls_total counter
study_coach_tool_calls_total{status="success",tool="search_topics"} 0.0
study_coach_tool_calls_total{status="success",tool="validate_study_plan"} 0.0
# HELP study_coach_quiz_submissions_total Total formative quick-check or practice quiz submissions.
# TYPE study_coach_quiz_submissions_total counter
study_coach_quiz_submissions_total{quiz_type="quick_check"} 0.0
study_coach_quiz_submissions_total{quiz_type="practice_quiz"} 0.0
```

### 3. Prometheus Target Verification

```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool
```
Both `study-coach-ui:8000` and `otel-collector:8889` targets reported `health: up`, `lastError: ""`.

### 4. Tempo Distributed Tracing Verification

```bash
curl -s "http://localhost:3200/api/search?limit=5" | python3 -m json.tool
```
Traces successfully registered:
- `study_coach.create_initial_plan` (Study Planner agent + validate_study_plan tool)
- `study_coach.generate_practice_quiz` (Quiz Generator agent + sanitized view)
- `study_coach.explain_topic` (Topic Expert agent + search_topics tool)
- `invocation` (Root Coordinator agent delegation)

### 5. Live ADK Model Evaluation

```bash
uv run python tests/eval/run_live_evaluation.py
```

**Output**:
```
================================================================================
🚀 GOOGLE ADK LIVE MODEL EVALUATION SUITE
================================================================================
[1/4] Evaluating Topic Expert agent (Scenario 3: Grounding & RAG)...
  ✓ PASS: 'Generative AI Concepts: Grounding & Retrieval-Augmented Generation (RAG)' generated in 128.60s
    - Key concepts (7): Grounding, Retrieval-Augmented Generation (RAG), Hallucination
[2/4] Evaluating Quiz Generator agent (Scenario 5: 3 formative MCQs)...
  ✓ PASS: 3 formative MCQs generated in 39.44s (all with 4 sanitized options)
[3/4] Evaluating Study Planner agent (Scenario 2: 7 days, 45 mins/day)...
  ✓ PASS: 7-day study plan generated in 15.34s adhering strictly to daily budget (<= 45 min)
[4/4] Evaluating Root Coordinator agent delegation (Scenario 1)...
  ✓ PASS: Root Coordinator routed & responded in 29.27s (8306 chars)
================================================================================
Result: 4/4 scenarios passed.
```

### 6. Code Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q
```

**Results**:
- `ruff check`: All checks passed! (0 warnings)
- `ruff format --check`: 94 files compliant (0 reformatted)
- `mypy`: Success: no issues found in 72 source files
- `pytest`: 139 passed in 2.35s

---

## Known Limitations

1. **`google-adk[eval]` Vertex AI Dependency**: Google ADK's built-in `AgentEvaluator` requires Google Cloud Vertex AI SDK (`vertexai` / `google-cloud-aiplatform`). For developer setups using direct Gemini Developer API keys (`GOOGLE_GENAI_USE_VERTEXAI=FALSE`), `tests/eval/run_live_evaluation.py` provides standalone evaluation without Vertex AI infrastructure requirements.
2. **Prometheus Multi-Process Storage**: In production deployments running multiple Streamlit worker threads or pods, Prometheus metrics should use Prometheus pushgateway or OTel collector Prometheus exporter instead of local process ports.
3. **Trace Retention**: Grafana Tempo is configured with 24-hour retention (`block_retention: 24h`) in local storage mode for local workstation efficiency.

---

## Git Release Verification

- **Git Commit Hash**: `e169cd2`
- **Git Tag**: `v0.7.0`
- **Release Status**: Verified and released
