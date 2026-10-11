# Workshop Instructor Guide (60-Minute Hands-On Lab)

Welcome to the **Gemini + Google ADK Multi-Agent Study Coach** workshop guide, designed for GDG chapters, DevFest sessions, and hands-on developer meetups.

---

## 1. Workshop Overview & Learning Objectives

This 60-minute session teaches participants how to build production-grade, multi-agent AI systems with **Google Agent Development Kit (ADK)**, **Gemini models**, deterministic Python validation, and open-standards observability.

### Key Objectives
1. **Understand Multi-Agent Specialization**: Move beyond monolithic prompt wrappers to role-specialized agents (Planner, Expert, Quizzer, Coordinator).
2. **Deterministic Guarantees**: Combine probabilistic LLMs with strict deterministic validation in pure Python (time budgets, answer keys, scoring).
3. **Session & Security Isolation**: Protect evaluation ground truth from client-side inspection.
4. **Agent Observability**: Trace agent and tool lifecycles in real time using OpenTelemetry, Prometheus, and Grafana Tempo.

---

## 2. 60-Minute Session Timeline

| Time | Duration | Segment | Format | Lead Activity | Attendee Activity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **00–05m** | 5 min | **Introduction & Welcome** | Presentation | Welcome, why multi-agent architectures, Gemini & ADK intro | Ensure laptop setup, verify terminal & browser ready |
| **05–15m** | 10 min | **Architecture Walkthrough** | Deep Dive & Code Tour | Explain Coordinator, Planner, Expert, Quizzer, and Workflow | Follow architecture diagram in `docs/architecture.md` |
| **15–25m** | 10 min | **Hands-On 1: Study Planner** | Interactive Exercise | Demonstrate 14-day 90-min plan generation in UI | Generate personalized plan with custom time budget |
| **25–35m** | 10 min | **Hands-On 2: Learn & Quick Check** | Interactive Exercise | Explain `genai_concepts`, review GCP examples & diagrams | Complete 3-question formative Quick Knowledge Check |
| **35–45m** | 10 min | **Hands-On 3: Quiz & Adaptive Replan** | Interactive Exercise | Run 5-question Practice Quiz, intentionally miss 2 items | Experience deterministic scoring & adaptive replan |
| **45–52m** | 7 min | **Observability in Action** | Demo / Guided Walk | Inspect Prometheus metrics & Tempo trace waterfall | Open Agent Ops tab, view spans & model latencies |
| **52–57m** | 5 min | **Evaluation Suite Walkthrough** | Demo / Discussion | Explain deterministic vs live agent evaluation | Review evaluation scenarios in Evaluations tab |
| **57–60m** | 3 min | **Recap, Roadmap & Q&A** | Wrap-Up | Review key takeaways, show GitHub repo, next steps | Star repo, explore follow-up exercises |

---

## 3. Preparation & Pre-Flight Checklist

### 1 Week Prior
- [ ] Send [Attendee Setup Guide](attendee-setup.md) to registered participants.
- [ ] Remind attendees to obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).
- [ ] Ensure Python 3.12+ and `uv` package manager instructions are highlighted.

### 1 Hour Prior
- [ ] Clone clean repository and run `uv sync`.
- [ ] Populate local `.env` file with working `GOOGLE_API_KEY`.
- [ ] Run test suite: `uv run pytest -q`.
- [ ] Start Streamlit UI: `uv run streamlit run ui/app.py`.
- [ ] (Optional) Start Docker observability stack: `docker compose --profile observability up -d`.
- [ ] Have [Demo Script](demo-script.md) and [Troubleshooting Guide](troubleshooting.md) open.

---

## 4. Live Demo Fallback Strategy

If attendees or the instructor encounter Wi-Fi latency, API rate limits, or quota exhaustion:

1. **Deterministic Test Fixtures**:
   The test suite includes comprehensive offline unit fixtures (`tests/fixtures/`) that exercise all schema validations, scoring calculations, and session transitions without live Gemini calls.
2. **Pre-Generated Evaluation Report**:
   The Evaluations tab automatically displays the saved evaluation report (`docs/reports/recent_evaluation_report.json`), allowing instant inspection of real pass/fail metrics, latencies, and model behavior without re-triggering API calls.
3. **Trace Screenshot Reference**:
   The pre-captured distributed trace waterfall is available at `docs/images/grafana-tempo-agent-trace-waterfall.png` for presenting span hierarchies even if Docker is not running locally.
