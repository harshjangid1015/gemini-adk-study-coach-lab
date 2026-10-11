# Workshop Architecture Walkthrough

This document provides a guided walkthrough of the **Multi-Agent Study Coach** architecture, detailing how requests flow from user input through Google ADK agents, deterministic engines, and telemetry pipelines.

---

## 1. High-Level Multi-Agent Architecture

```mermaid
graph TD
    Student([Student Learner]) --> Streamlit["Streamlit Workshop UI (Port 8501)"]
    Streamlit --> Facade["WorkshopFacade (Service Boundary)"]
    
    subgraph MultiAgentEngine ["Google ADK Multi-Agent Core"]
        Facade --> Coordinator["Study Coach Coordinator Agent"]
        Coordinator --> Planner["Study Planner Agent"]
        Coordinator --> Expert["Topic Expert Agent"]
        Coordinator --> Quizzer["Quiz Generator Agent"]
        
        Planner --> PlanTools["Planning Tools (Time Budgets & Validation)"]
        Expert --> CurrTools["Curriculum Tools (Grounding & Taxonomy)"]
        Quizzer --> QuizTools["Quiz Tools (Question Generation)"]
    end
    
    subgraph DeterministicEngine ["Deterministic Python Services"]
        Facade --> Workflow["AdaptiveStudyWorkflow"]
        Workflow --> GradingEngine["Deterministic Grading Engine (Pure Python)"]
        Workflow --> SessionSvc["LearningSessionService (ADK In-Memory)"]
        Facade --> ResTools["Learning Resource Catalog Tools"]
        Facade --> LessonVisuals["Lesson Visuals & Code Example Registry"]
    end
    
    subgraph ObservabilityCluster ["Open-Standards Telemetry Cluster"]
        MultiAgentEngine -.-> OTelPlugin["ADKObservabilityPlugin"]
        Workflow -.-> OTelPlugin
        OTelPlugin --> OTelCollector["OpenTelemetry Collector (4317/4318)"]
        OTelCollector --> Tempo["Grafana Tempo (Traces :3200)"]
        OTelCollector --> Prometheus["Prometheus (Metrics :9090)"]
        Tempo --> Grafana["Grafana Dashboards (:3000)"]
        Prometheus --> Grafana
    end
```

---

## 2. Specialized Agent Responsibilities

### 1. Root Coordinator Agent (`study_coach`)
- **Role**: Primary entrypoint routing requests across specialized agents.
- **Tools**: Sub-agent delegation tools (`invoke_agent`).
- **Guarantees**: Maintains conversation context and routes queries to the most qualified specialist.

### 2. Study Planner Agent (`study_planner`)
- **Role**: Generates day-by-day certification preparation schedules.
- **Constraints**:
  - Respects student daily study time limit (e.g. $\le 90$ minutes).
  - Produces sequential days matching exam deadline ($N$ days).
  - All topic IDs match validated curriculum entries.
- **Output**: Structured `StudyPlan` Pydantic model via `set_model_response`.

### 3. Topic Expert Agent (`topic_expert`)
- **Role**: Explains technical concepts grounded in the curriculum syllabus.
- **Pedagogical Structure**:
  - Structured learning objectives and core vocabulary.
  - In-depth conceptual explanation adapted to target level (*beginner*, *intermediate*, *advanced*).
  - Concrete Google Cloud architecture scenarios (e.g., Cymbal Retail with Vertex AI).
  - Common misconceptions and comprehension check questions.

### 4. Quiz Generator Agent (`quiz_generator`)
- **Role**: Creates multiple-choice questions assessing curriculum concepts.
- **Design**:
  - 4 distinct answer choices per question (`A`, `B`, `C`, `D`).
  - Answer keys and detailed explanations are stored exclusively server-side.
  - Sanitized student view (`StudentQuizQuestion`) is delivered to the frontend.

---

## 3. The Adaptive Closed Loop

```mermaid
sequenceDiagram
    autonumber
    actor S as Student
    participant UI as Streamlit UI
    participant F as WorkshopFacade
    participant W as AdaptiveStudyWorkflow
    participant Q as Quiz Generator
    participant G as Python Grading Engine
    participant P as Study Planner
    
    S->>UI: Request 5-question Practice Quiz
    UI->>F: generate_quiz(topic_id)
    F->>W: generate_practice_quiz()
    W->>Q: ADK Invoke Quiz Generator
    Q-->>W: Quiz (with private answer keys)
    W->>W: Store Quiz in Session, sanitize questions
    W-->>UI: StudentQuizQuestion[] (No answer keys)
    
    S->>UI: Select answers & click Submit
    UI->>F: submit_quiz(QuizSubmission)
    F->>W: submit_quiz_answers()
    W->>G: Deterministic Python Evaluation
    G-->>W: QuizResult (Score, % score, weak topics)
    W-->>UI: Display Result, feedback & explanations
    
    opt If Score < 70% (Weak Topic Detected)
        S->>UI: Request Adaptive Replanning
        UI->>F: adapt_study_plan(completed_days=1)
        F->>W: generate_adapted_plan()
        W->>P: ADK Invoke Study Planner (with weak topic emphasis)
        P-->>W: Adapted StudyPlan (Revision 2)
        W-->>UI: Display updated roadmap prioritizing weak topics
    end
```

---

## 4. Telemetry & Security Boundaries

1. **Answer Key Protection**: Ground-truth answers never enter client-side session state or HTML before submission.
2. **Credential Sanitization**: The OpenTelemetry instrumentation scrubs authorization headers, API keys, and sensitive student tokens (`[REDACTED_API_KEY]`).
3. **Deterministic Separation**: AI agents generate candidate content, but all scoring, time addition, and topic-existence checks run in deterministic Python code.
