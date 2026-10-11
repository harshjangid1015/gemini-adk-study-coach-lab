# Architecture

```mermaid
graph TD
    User([Student]) --> UI["Streamlit Workshop UI (Port 8501)"]
    UI --> Facade["WorkshopFacade"]
    Facade --> Workflow["AdaptiveStudyWorkflow"]
    Facade --> Coordinator["Study Coach Coordinator Agent"]
    Facade --> Visuals["Lesson Visuals Service"]
    Facade --> Examples["Code Examples Registry"]
    Facade --> ResTools["Learning Resource Catalog Tools"]
    
    Coordinator --> Planner["Study Planner Agent"]
    Coordinator --> Expert["Topic Expert Agent"]
    Coordinator --> Quiz["Quiz Generator Agent"]
    
    Planner -.-> Profile[("Curriculum & Planning Tools")]
    Expert -.-> Docs[("Curriculum Knowledge & Topic Tools")]
    Quiz -.-> QBank[("Curriculum Tools & Python Grading Engine")]
    ResTools -.-> Catalog[("learning_resources.yaml")]
```

### Note on Features
The `Study Coach Coordinator Agent`, `Study Planner Agent`, `Topic Expert Agent`, `Quiz Generator Agent`, `Adaptive Learning Multi-Agent Orchestration Workflow`, `Streamlit Workshop Web UI`, `Interactive Learning Visuals`, `Curated Learning Resources Library`, `Runnable Python Examples`, and `Docker / Docker Compose Runtime` are implemented as of Milestone 6. Answer grading, resource filtering, and time-budget validations remain 100% deterministic Python. Telemetry, Prometheus, and Grafana are planned for Milestone 7.

