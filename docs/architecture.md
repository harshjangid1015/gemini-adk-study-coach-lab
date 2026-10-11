# Architecture

```mermaid
graph TD
    User([Student]) --> UI["Web UI / Workshop UI (Planned)"]
    UI --> Coordinator["Study Coach Coordinator Agent"]
    
    Coordinator --> Planner["Study Planner Agent"]
    Coordinator --> Expert["Topic Expert Agent"]
    Coordinator --> Quiz["Quiz Generator Agent"]
    
    Planner -.-> Profile[("Curriculum & Planning Tools")]
    Expert -.-> Docs[("Curriculum Knowledge & Topic Tools")]
    Quiz -.-> QBank[("Curriculum Tools & Python Grading Engine")]
```

### Note on Features
The `Study Coach Coordinator Agent`, `Study Planner Agent`, `Topic Expert Agent`, `Quiz Generator Agent`, and `Adaptive Learning Multi-Agent Orchestration Workflow` are implemented as of Milestone 5. Session state management is powered by Google ADK `InMemorySessionService`, and answer grading and time-budget validation are 100% deterministic Python. Workshop containerization and telemetry are planned for future milestones.
