# Architecture

```mermaid
graph TD
    User([Student]) --> UI["Web UI / Workshop UI (Planned)"]
    UI --> Coordinator["Study Coach Coordinator Agent"]
    
    Coordinator --> Planner["Study Planner Agent"]
    Coordinator --> Expert["Topic Expert Agent"]
    Coordinator --> Quiz["Quiz Generator Agent (Planned)"]
    
    Planner -.-> Profile[("Curriculum & Planning Tools")]
    Expert -.-> Docs[("Curriculum Knowledge & Topic Tools")]
    Quiz -.-> QBank[("Question Bank (Planned)")]
```

### Note on Features
The `Study Coach Coordinator Agent`, `Study Planner Agent`, and `Topic Expert Agent` are implemented as of Milestone 3. The web UI and `Quiz Generator Agent` are planned for future milestones.
