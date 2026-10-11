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
The `Study Coach Coordinator Agent`, `Study Planner Agent`, `Topic Expert Agent`, and `Quiz Generator Agent` are implemented as of Milestone 4. The web UI and adaptive multi-agent orchestration are planned for future milestones.
