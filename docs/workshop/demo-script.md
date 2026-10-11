# Workshop Demo Script (Instructor Walkthrough)

This script provides step-by-step speaker notes, prompts, and expected outputs for conducting a seamless live demonstration of the Study Coach application.

---

## Demo Scenario: College Student Preparing for Google Cloud Certification

**Persona Prompt**:
> *"I'm a college student preparing for the Google Cloud Generative AI Leader certification in 14 days. I'm a beginner and can study 90 minutes per day. Create my daily plan, explain important topics, and generate practice questions."*

---

## Segment 1: Study Planning Demonstration (Minutes 15–25)

### Actions in Streamlit UI
1. Open sidebar **Student Setup**:
   - Target Certification: `Google Cloud Generative AI Leader`
   - Experience Level: `Beginner`
   - Days until Exam: `14`
   - Daily Study Budget: `90 minutes`
   - Click **Start / Reset Session**.
2. Navigate to **Tab 1: 📅 Study Plan**:
   - Click **Generate Initial Plan**.

### Talking Points
- *"Notice that the request is routed through our Google ADK Coordinator to the Study Planner agent."*
- *"The agent uses structured outputs via `set_model_response` and curriculum tools."*
- *"Crucially, the resulting plan is not just plain markdown—it is parsed into a Pydantic `StudyPlan` model and verified with deterministic Python checks."*
- *"Look at the day cards: Day 1 (90 min), Day 2 (90 min), ..., Day 14 (90 min). The plan guarantees the daily budget is never exceeded, and all topic IDs match the verified curriculum syllabus."*

---

## Segment 2: Topic Learning & Formative Quick Check (Minutes 25–35)

### Actions in Streamlit UI
1. Navigate to **Tab 2: 📖 Learn Topic**:
   - Select Topic: `genai_concepts` (Generative AI Concepts)
   - Detail Level: `Beginner`
   - Click **Teach This Topic**.
2. Walk through the 6 sub-tabs:
   - **Summary & Objectives**: Review structured learning objectives and vocabulary.
   - **Architecture Diagram**: Inspect the Mermaid workflow diagram showing Discriminative vs Generative AI models.
   - **Step-by-Step Lesson**: Highlight the real-world GCP architecture example (*Cymbal Retail Virtual Assistant* using Vertex AI Search & Conversation).
   - **Hands-On Python**: Show the runnable Python code snippet calling Gemini models.
   - **Verified Resources**: Highlight the compact resource cards with verified brand logos (Google Cloud, YouTube, GitHub, Hugging Face).
   - **Practice & Share**: Focus on the 3-question **Quick Knowledge Check**.
3. Answer the 3 MCQs:
   - Select options for Q1, Q2, and Q3 using `st.radio`.
   - Click **Submit Quick Knowledge Check**.

### Talking Points
- *"The Topic Expert agent produces grounded explanations adapted to beginner comprehension."*
- *"Notice that the 3 formative questions were delivered to the browser without exposing the answer key in HTML or JavaScript state."*
- *"When we click submit, our backend deterministically scores the answers in pure Python (100%, 66.7%, 33.3%, 0%), revealing explanations and feedback instantly without modifying formal quiz history."*

---

## Segment 3: Practice Quiz & Adaptive Replanning (Minutes 35–45)

### Actions in Streamlit UI
1. In the **Practice & Share** tab, click **Launch Formal Practice Quiz ↗** (or switch to **Tab 3: 📝 Practice Quiz**).
   - Notice the topic `genai_concepts` is preselected automatically.
   - Question Count: `5`
   - Click **Generate Practice Quiz**.
2. Complete the quiz:
   - Intentionally select a mixture of correct and incorrect choices (e.g., answering 2 correctly and 3 incorrectly).
   - Click **Submit Answers for Deterministic Grading**.
   - Review diagnostic feedback: Score is 40.0% ($< 70\%$), flagging `genai_concepts` as a **Weak Topic**.
3. Navigate to **Tab 4: 🔄 Adaptive Plan**:
   - Observe that `genai_concepts` is listed under identified weak topics.
   - Set Completed Days: `1`
   - Click **Generate Adapted Plan**.

### Talking Points
- *"The Quiz Generator agent creates formal multiple-choice questions anchored in our curriculum."*
- *"Because the student struggled on `genai_concepts`, the Adaptive Learning Workflow triggers Revision 2 of the study plan."*
- *"Notice the adapted schedule: Completed work is preserved, remaining days adjust to 13 days, and priority review blocks are inserted for the weak topic while strictly maintaining the 90-minute daily ceiling."*

---

## Segment 4: Agent Ops & Distributed Traces (Minutes 45–52)

### Actions in Streamlit UI & Grafana
1. Navigate to **Tab 5: 🔭 Agent Ops**:
   - Check container status indicators: Prometheus, Tempo, Grafana, and Collector show green checks.
   - Click **Open Tempo Traces ↗** (or open `http://localhost:3000/explore`).
2. In Grafana Tempo Explore:
   - Show the TraceQL query `{ name = "study_coach.explain_topic" }` or view trace `90e5b380f4578c51555172d91ff7940a`.
   - Expand the trace waterfall.

### Talking Points
- *"OpenTelemetry instrumentation bridges Google ADK agent and tool lifecycles directly into OpenTelemetry spans."*
- *"Notice the hierarchical tree: `study_coach.explain_topic` is the root span, delegating to `adk.agent.topic_expert`, calling LLM inference spans (`generate_content gemini-3.8-flash`), and invoking curriculum tools (`get_topic_by_id`, `get_related_topics`, `search_topics`)."*
- *"Sensitive student data and API keys are automatically redacted (`[REDACTED_API_KEY]`), ensuring telemetry is production-safe."*

---

## Segment 5: Agent Evaluations (Minutes 52–57)

### Actions in Streamlit UI
1. Navigate to **Tab 6: 🧪 Evaluations**:
   - Review the loaded evaluation summary: Model `gemini-3.8-flash`, 4 scenarios evaluated, 100% pass rate, duration 94.28s.
   - Expand **Scenario 1** (14-day study plan) and **Scenario 3** (Topic explanation).

### Talking Points
- *"Agent evaluation is critical for reliable AI. We distinguish between three levels of evaluation:"*
  1. *Deterministic offline tests (156 pytest assertions)*
  2. *Live multi-agent scenario evaluations (checking structured schema, curriculum validity, and latency)*
  3. *Official Google ADK AgentEvaluator integrations*
- *"The UI allows non-technical stakeholders and engineers alike to inspect evaluation outcomes on demand."*
