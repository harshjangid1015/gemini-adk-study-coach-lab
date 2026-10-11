# AI Study Coach

## Project Overview
The AI Study Coach is a multi-agent application that helps students prepare for technical certifications. By providing your certification goal, time until the exam, and study availability, the coach will eventually be able to generate study plans, explain topics, and test your knowledge.

## Technology Stack
- **Language**: Python 3.12+
- **Framework**: Google ADK
- **LLM**: Gemini API
- **Data Validation**: Pydantic v2
- **Tooling**: uv, pytest, Ruff, mypy

## Architecture Diagram
See [Architecture Diagram](docs/architecture.md).

## Installation
1. Ensure you have `uv` installed.
2. Clone this repository.
3. Run `uv sync` to install dependencies.

## Gemini API Key Setup
You need a Gemini API key to run this application.
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Create an API key.
3. Copy `.env.example` to `.env`.
4. Update `GOOGLE_API_KEY` in your `.env` file with your key.

## Local ADK Launch
To launch the Google ADK developer UI locally, run:
```bash
./scripts/run_local.sh
```

## Example Conversation
- **Student:** I'm preparing for the Google Cloud Generative AI Leader certification in 14 days. I'm a beginner and can study 90 minutes daily.

- **Coach:** Welcome! I'm the AI Study Coach. I see you are aiming for the Google Cloud Generative AI Leader certification. In the future, I will be able to help you plan your studies, explain topics, and provide quizzes. Currently, these features are still in development!

## Running Tests
To run all tests and quality checks, use:
```bash
./scripts/run_tests.sh
```

## Roadmap
- Milestone 1: Project Foundation (Done)
- Milestone 2: Study Planner Agent (Done)
- Milestone 3: Topic Expert Agent (Done)
- Milestone 4: Quiz Generator Agent (Planned)
- Milestone 5: Multi-Agent Orchestration (Planned)
- Milestone 6: Workshop UI & Docker (Planned)
- Milestone 7: Observability and Evaluation (Planned)
- Milestone 8: Workshop-Ready Release (Planned)

## Current Functionality vs Planned Features
- **Current**: 
  - Root coordinator agent (`study_coach`) routing student requests.
  - **Study Planner Agent (`study_planner`)**: Generates structured, deterministic-checked study plans adhering to daily minute limits and curriculum topic IDs.
  - **Topic Expert Agent (`topic_expert`)**: Explains certification topics adapted to beginner, intermediate, and advanced levels, with Google Cloud examples, common misconceptions, and comprehension checks.
  - Pydantic models for student profiles, requests, study plans, and topic explanations.
  - Deterministic curriculum tools reading `google_cloud_genai_leader.yaml`.
- **Planned**: Scored quiz generator agent, adaptive replanning orchestration, workshop web UI, Docker containerization, and evaluation telemetry.
