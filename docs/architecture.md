# Architecture

```mermaid
graph TD
    User([Student]) --> UI["Web UI / Workshop UI (Planned)"]
    UI --> Coordinator["Study Coach Coordinator Agent"]
    
    Coordinator --> Planner["Study Planner Agent"]
    Coordinator --> Expert["Topic Expert Agent (Planned)"]
    Coordinator --> Quiz["Quiz Generator Agent (Planned)"]
    
    Planner -.-> Profile[("Student Profile Data")]
    Expert -.-> Docs[("Certification Knowledge")]
    Quiz -.-> QBank[("Question Bank")]
```

### Note on Features
The `Study Coach Coordinator Agent` and `Study Planner Agent` are currently implemented for Milestone 2. The web UI and other agents (`Topic Expert Agent`, `Quiz Generator Agent`) are planned for future milestones.
