# Architecture

```mermaid
graph TD
    User([Student]) --> UI[Web UI / Workshop UI (Planned)]
    UI --> Coordinator[Study Coach Coordinator Agent]
    
    Coordinator --> Planner[Study Planner Agent (Planned)]
    Coordinator --> Expert[Topic Expert Agent (Planned)]
    Coordinator --> Quiz[Quiz Generator Agent (Planned)]
    
    Planner -.-> Profile[(Student Profile Data)]
    Expert -.-> Docs[(Certification Knowledge)]
    Quiz -.-> QBank[(Question Bank)]
```

### Note on Features
The `Study Coach Coordinator Agent` is currently implemented as a basic ADK agent for Milestone 1. The web UI and all other agents (`Study Planner Agent`, `Topic Expert Agent`, `Quiz Generator Agent`) are planned for future milestones.
