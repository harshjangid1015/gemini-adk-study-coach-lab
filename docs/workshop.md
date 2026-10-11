# Workshop Hub & Documentation Index

Welcome to the **Gemini + Google ADK Multi-Agent Study Coach** workshop hub. This documentation suite prepares instructors and attendees for a complete 60-minute hands-on lab.

---

## Workshop Documentation Suite

| Document | Target Audience | Description |
| :--- | :--- | :--- |
| **[Instructor Guide](workshop/instructor-guide.md)** | Workshop Facilitators | 60-minute timeline, teaching objectives, pre-flight checklists, and live fallback paths. |
| **[Attendee Setup Guide](workshop/attendee-setup.md)** | Attendees / Developers | Step-by-step setup on macOS, Linux, and Windows, prerequisite installations, and quickstart commands. |
| **[Demo Script](workshop/demo-script.md)** | Instructors | Exact talking points, live student prompt, expected UI behaviors, and demonstration flow. |
| **[Hands-On Exercises](workshop/exercises.md)** | Attendees | Interactive lab exercises covering study planning, formative quick checks, formal quizzes, and telemetry inspection. |
| **[Troubleshooting Guide](workshop/troubleshooting.md)** | Everyone | Quick diagnosis and resolutions for missing API keys, port collisions, rate limits, and Docker startup issues. |
| **[Architecture Walkthrough](workshop/architecture-walkthrough.md)** | Instructors / Attendees | In-depth architectural breakdown of agent specialization, deterministic engines, and telemetry pipelines. |

---

## 60-Minute Workshop At a Glance

```text
00–05m: Intro to Gemini & Google ADK Multi-Agent Patterns
05–15m: Multi-Agent Architecture Walkthrough
15–25m: Hands-On 1: Generate a 14-Day Personalized Study Plan
25–35m: Hands-On 2: Learn a Topic & Complete Formative Quick Check
35–45m: Hands-On 3: Practice Quiz & Trigger Adaptive Replanning
45–52m: OpenTelemetry in Action: Inspect Metrics & Tempo Traces
52–57m: Multi-Agent Evaluations Suite Walkthrough
57–60m: Wrap-Up, Q&A, and Next Steps
```

---

## Quick Launch Summary

```bash
# 1. Clone & sync dependencies
git clone https://github.com/hastimal/gemini-adk-study-coach-lab.git
cd gemini-adk-study-coach-lab
uv sync

# 2. Configure credentials
cp .env.example .env
# Insert GOOGLE_API_KEY in .env

# 3. Launch Student Web UI (No Docker needed)
uv run streamlit run ui/app.py
# Access at http://localhost:8501

# 4. (Optional) Launch Observability Stack
docker compose --profile observability up -d
# Access Grafana at http://localhost:3000
```
