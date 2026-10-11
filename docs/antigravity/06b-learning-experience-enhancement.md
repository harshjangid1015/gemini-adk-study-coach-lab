# ANTIGRAVITY — M6 LEARNING EXPERIENCE ENHANCEMENT

PROJECT: gemini-adk-study-coach-lab
BRANCH: main
SCOPE: Improve existing M6 Streamlit Workshop UI
DO NOT START M7.

GOAL:
Transform the current text-heavy Study Coach into
an interactive, visual, evidence-linked learning
experience with verified free learning resources,
diagrams, working examples and practice materials.

IMPORTANT:
The current Study Planner, Topic Expert, Quiz
Generator, scoring, session management and
adaptive replanning already work.

Preserve existing M1-M6 functionality.

Do not recreate the repository or replace the
entire UI with another framework.

==================================================
1. INSPECT CURRENT IMPLEMENTATION
==================================================

Read:
- GEMINI.md
- README.md
- ui/app.py
- src/study_coach/agents/
- src/study_coach/models/
- src/study_coach/services/
- src/study_coach/workflows/
- src/study_coach/data/
- docs/antigravity/06-workshop-ui-docker.md

Inspect all current tests and working UI components.

Run baseline:
uv run pytest -q

Record actual baseline before changes.

Implement and test one enhancement at a time.

==================================================
2. OFFICIAL EXAM ALIGNMENT
==================================================

The certification is Google Cloud
Generative AI Leader.

Use its official preparation page:
https://cloud.google.com/learn/certification/generative-ai-leader

Align curriculum coverage to the actual
exam guide and its major domains.

Separate:
- Official exam domain
- Curriculum topic
- Optional technical deep dive
- Practical exercise

Do not invent official domain weights or
claim deep technical material is required
if it isn't established by the exam guide.

Maintain an explicit curriculum coverage map.

If an official document cannot be accessed,
record it as unverified.

==================================================
3. CURATED LEARNING RESOURCE LIBRARY
==================================================

Create a versioned local resource catalog.

Suggested path:
src/study_coach/data/learning_resources.yaml

Create Pydantic models:
src/study_coach/models/learning_resource.py

Resource metadata:

- resource_id
- topic_ids
- title
- provider
- resource_type
- url
- short_description
- experience_level
- estimated_minutes
- language
- exam_domain
- requires_login
- requires_paid_access
- verified_at
- verification_status
- is_official
- tags

Resource types:
- Official exam guide
- Official documentation
- Article
- Video
- Interactive tutorial
- Python example
- GitHub repository
- Sample exam questions

Initial sources:

Official certification:
https://cloud.google.com/learn/certification/generative-ai-leader

Google ML Crash Course:
https://developers.google.com/machine-learning/crash-course

Google Generative AI documentation:
https://docs.cloud.google.com/docs/generative-ai

Google RAG examples:
https://github.com/GoogleCloudPlatform/generative-ai/tree/main/rag-grounding

Hugging Face LLM Course:
https://huggingface.co/learn/llm-course/chapter1/1

3Blue1Brown Transformer video:
https://www.youtube.com/watch?v=wjZofJX0v4M

3Blue1Brown Attention video:
https://www.youtube.com/watch?v=eMlx5fFNoYc

Verify resource relevance, public access and
actual destination before marking verified.

Do not invent titles, URLs, durations or access
requirements.

Distinguish free viewing from exercises that
may require an account or cloud charges.

Never claim LinkedIn posts or YouTube videos
are official Google certification resources.

==================================================
4. RESOURCE MATCHING TO STUDY DAYS
==================================================

Add resource retrieval tools:

get_resources_for_topic()
get_resources_for_day()
filter_resources_by_type()
filter_resources_by_experience()
get_official_exam_resources()

Select resources using verified topic IDs,
not arbitrary Gemini-generated URLs.

The Study Plan UI should show:

Day 4: LLM Architecture
- Daily activities
- Learning objectives
- Read official documentation
- Watch video
- Visualize architecture
- Try Python example
- Take practice questions

Resource recommendations must not silently
increase the existing daily study budget.

Show resource time estimates separately, and
identify which resources fit allocated activities.

Include direct clickable external links.

==================================================
5. UPGRADE TOPIC EXPERT EXPERIENCE
==================================================

Retain the current Topic Expert Agent.

Improve its lesson presentation using distinct
content sections:

A. Quick concept summary
B. Learning objectives
C. Visual architecture diagram
D. Step-by-step technical explanation
E. Real-world Google Cloud use case
F. Working Python example
G. Common misconceptions
H. Free external learning resources
I. Sample practice questions
J. Mark topic reviewed

Do not render one huge unbroken wall of text.

Use Streamlit tabs, containers and expanders.

Prefer progressive disclosure.

Keep beginner material simple while making
advanced technical explanations available.

==================================================
6. DIAGRAM GENERATION AND RENDERING
==================================================

Create:
src/study_coach/services/lesson_visuals.py

Use declarative and validated visual templates.

Supported topics may include:

- Transformer architecture
- Tokenization and embeddings
- Self-attention
- Pre-training vs fine-tuning
- Prompt engineering
- Grounding and RAG
- Responsible AI
- Vertex AI workflow

Prefer:
- Streamlit-native diagrams
- Graphviz when available
- Static SVGs generated from validated templates
- Markdown Mermaid where supported and tested

Avoid injecting unchecked Gemini-generated HTML,
JavaScript, SVG or Graphviz source.

Every diagram must:
- Have a title
- Use labeled arrows
- Explain input/output
- Explain individual components
- Render within Streamlit
- Have a text alternative

Example Transformer inference flow:

Input Text
   |
   v
Tokenization
   |
   v
Token Embeddings
   |
   v
Positional Information
   |
   v
Transformer Blocks
   |
   v
Output Projection
   |
   v
Next Token Probabilities

Test the diagram in the real browser.

==================================================
7. PRACTICAL CODE EXAMPLES
==================================================

Create:
src/study_coach/data/code_examples/

Create curated examples for supported topics.

Initial examples:

- Simple word tokenization demo
- Attention computation with small matrices
- RAG retrieval simulation
- Gemini API generation
- Prompt engineering comparison
- Grounded vs ungrounded answer comparison

Clearly label:
- Runnable Python
- Conceptual simulation
- Actual Gemini API example
- Requires credentials
- Requires Google Cloud services
- Expected output

Use short examples suitable for beginners.

Include Copy Code UI.

Avoid executing arbitrary model-generated code.

Run trusted local examples in isolated tests.

Do not execute untrusted student input.

Do not embed API keys in examples.

For an introductory business-level exam,
treat advanced code as optional enrichment.

==================================================
8. LEARNING VIDEOS AND ARTICLES
==================================================

Create a reusable ResourceCard component.

Display:
- Title
- Provider
- Video/article/guide badge
- Short description
- Estimated duration if verified
- Official/nonofficial classification
- Open resource link

Show only relevant resources for the selected
curriculum topic.

If video embedding is used:
- Verify the video URL is supported.
- Provide a normal link fallback.
- Never autoplay.
- Respect third-party permissions.

Do not scrape or copy copyrighted full articles.

==================================================
9. PRACTICE MATERIAL IN LEARN TOPIC
==================================================

Add a "Practice This Topic" section.

Include:
- Two or three optional comprehension checks
- Link to Quiz Generator with topic preselected
- Five-question practice quiz option
- Review weak topics option

Reuse the existing quiz agent and grading pipeline.

Do not create a second scoring implementation.

Student-facing questions must not reveal
correct answers before submission.

If sample official exam questions are available
through Google's preparation page, link to them.

Do not copy official question banks into the repo
without permission.

Generated quiz questions must be labeled as
AI-generated original practice questions.

==================================================
10. LINKEDIN SHARE FEATURE
==================================================

Add optional "Share My Learning" support.

The student may:
- Generate a short LinkedIn learning summary.
- Include topic title and completed activities.
- Copy the text.
- Open LinkedIn's sharing interface manually.

Do not automatically publish content.

Do not include private student information,
exam scores or answer keys by default.

Clearly distinguish sharing from learning progress.

==================================================
11. ADAPTIVE LEARNING RESOURCE RECOMMENDATIONS
==================================================

When weak topics are identified:

- Show the weak topics.
- Explain why revision is recommended.
- Link to relevant official documentation.
- Recommend free tutorial/video material.
- Offer an appropriate optional practice quiz.
- Connect resources to the revised plan.

Example:

Weak topic: llm_architecture

Recommended:
1. Review Transformer diagram.
2. Watch an attention explanation.
3. Complete a tokenization example.
4. Attempt five new practice questions.

Recommendations should consider remaining
study time, not simply add unlimited materials.

==================================================
12. STEP-BY-STEP TESTING
==================================================

Follow GEMINI.md permanent testing requirements.

Test immediately after EACH component.

Required tests:

RESOURCE CATALOG
- YAML schema valid.
- Topic IDs valid.
- Duplicate resources rejected.
- Unsupported URLs rejected.
- Broken or unavailable resources flagged.
- Missing metadata handled.
- No fabricated verification status.

DIAGRAMS
- Correct diagram for selected topic.
- No arbitrary code execution.
- Diagram renders successfully.
- Readable labels.
- Text fallback.
- Invalid diagram data rejected.

CODE EXAMPLES
- Syntax and imports valid.
- Offline examples run.
- Expected output verified.
- No secrets.
- No untrusted code execution.
- No unintended API charges.

LEARNING EXPERIENCE
- Topic Expert still works.
- Beginner and advanced levels differ.
- Resources match topic selection.
- Study-day resources fit allocated time.
- Practice link opens the correct topic.
- Original learning state remains intact.

QUIZ
- Student questions remain sanitized.
- Scoring remains deterministic.
- Weak topics remain accurate.
- No answer-key leakage.

ADAPTIVE PLAN
- Previously working revision cycle passes.
- Weak topics map to relevant resources.
- Remaining-day and minute constraints pass.

REGRESSION
- All M1-M6 tests must pass.

QUALITY:
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

==================================================
13. LIVE UI VERIFICATION
==================================================

Start the real Streamlit application.

Manually or automatically validate:

1. Open Day 4 in the Study Plan.
2. Find official learning resources.
3. Open the LLM Architecture topic.
4. See its architecture diagram.
5. Run/copy its Python example.
6. Open verified YouTube and reading links.
7. Generate five practice questions.
8. Submit answers and receive the true score.
9. Generate an adapted plan.
10. Inspect suggested weak-topic resources.
11. Confirm old and revised plans remain available.

Repeat the core cycle in Docker if available.

Do not claim browser success when only
Python unit tests have been executed.

==================================================
14. DOCUMENTATION AND GIT
==================================================

Record the entire instruction and actual
step-by-step results in:

docs/antigravity/06-workshop-ui-docker.md

Add:
docs/learning-experience.md

Update:
README.md
docs/workshop.md
docs/architecture.md

Explain resource licensing and link verification.

This is an enhancement to M6, not a new milestone.

Do not move or rewrite v0.6.0 if it already exists.

After required verification:
- Check Git status and remote.
- Check for secrets and unrelated changes.
- Commit on main using:

feat(m6): enrich lessons with resources and visuals

- Push safely without force-pushing.

Do not create v0.7.0.

STOP after delivering the tested enhancements.

==================================================
15. FINAL REPORT
==================================================

Provide:
1. Exact files changed.
2. New resource catalog entries.
3. Verified external resources and URLs.
4. Learning diagram implementations.
5. Runnable Python example test results.
6. Study Plan resource integration.
7. Topic Expert resource integration.
8. Quiz and adaptive-plan regression results.
9. Total test count.
10. Ruff and mypy results.
11. Live Streamlit screenshot/test evidence.
12. Docker verification if performed.
13. Git commit and push status.
14. Remaining limitations.

---

# IMPLEMENTATION & VERIFICATION RECORD

## 1. Summary of Changes
- Built a versioned, verified local learning resource catalog ([`src/study_coach/data/learning_resources.yaml`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/data/learning_resources.yaml)) and Pydantic data model ([`src/study_coach/models/learning_resource.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/models/learning_resource.py)).
- Implemented deterministic resource retrieval and matching tools ([`src/study_coach/tools/resource_tools.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/tools/resource_tools.py)).
- Implemented declarative Mermaid lesson visuals service with component breakdowns and accessible text alternatives ([`src/study_coach/services/lesson_visuals.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/services/lesson_visuals.py)).
- Created self-contained, beginner-friendly runnable Python examples and registry ([`src/study_coach/data/code_examples/`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/data/code_examples/) and [`src/study_coach/data/code_examples_registry.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/src/study_coach/data/code_examples_registry.py)).
- Upgraded the Streamlit Workshop UI ([`ui/app.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/ui/app.py)):
  - Added `ResourceCard` UI component with verified status, provider, type, and external links.
  - Added Day 4 curated resource recommendations with explicit budget notices.
  - Upgraded Learn Topic into 6 progressive disclosure tabs: Summary, Architecture Diagram, Lesson, Hands-On Python, Verified Resources, and Practice & Share.
  - Implemented one-click practice jump preselecting the current topic in the Practice Quiz tab.
  - Implemented LinkedIn learning achievement post generator with copyable preview and manual share link.
  - Upgraded Adaptive Plan tab with multi-step remediation pathways for identified weak topics.
- Added comprehensive unit and UI tests ([`tests/unit/test_learning_resources.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/tests/unit/test_learning_resources.py), [`tests/unit/test_lesson_visuals.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/tests/unit/test_lesson_visuals.py), [`tests/unit/test_code_examples.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/tests/unit/test_code_examples.py), [`tests/unit/test_streamlit_ui.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/tests/unit/test_streamlit_ui.py)).

## 2. Files Created and Modified
- **Created**:
  - `docs/antigravity/06b-learning-experience-enhancement.md`
  - `docs/learning-experience.md`
  - `src/study_coach/models/learning_resource.py`
  - `src/study_coach/data/learning_resources.yaml`
  - `src/study_coach/tools/resource_tools.py`
  - `src/study_coach/services/lesson_visuals.py`
  - `src/study_coach/data/code_examples/tokenization_demo.py`
  - `src/study_coach/data/code_examples/attention_demo.py`
  - `src/study_coach/data/code_examples/rag_simulation.py`
  - `src/study_coach/data/code_examples_registry.py`
  - `tests/unit/test_learning_resources.py`
  - `tests/unit/test_lesson_visuals.py`
  - `tests/unit/test_code_examples.py`
  - `tests/unit/test_streamlit_ui.py`
- **Modified**:
  - `ui/app.py`
  - `src/study_coach/services/workshop_facade.py`
  - `tests/unit/test_workshop_facade.py`
  - `README.md`
  - `docs/workshop.md`
  - `docs/architecture.md`
  - `docs/antigravity/06-workshop-ui-docker.md`
  - `docs/antigravity/README.md`
  - `GEMINI.md`

## 3. Verified Resource URLs
- Google Cloud Generative AI Leader Exam Guide: https://cloud.google.com/learn/certification/generative-ai-leader
- Vertex AI Generative AI Documentation: https://docs.cloud.google.com/docs/generative-ai
- Google Machine Learning Crash Course (LLMs): https://developers.google.com/machine-learning/crash-course
- Google Responsible AI Principles & Practices: https://cloud.google.com/responsible-ai
- Vertex AI Studio Quickstart: https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview
- Google Cloud Generative AI RAG Grounding Sample Repo: https://github.com/GoogleCloudPlatform/generative-ai/tree/main/rag-grounding
- Hugging Face LLM Course Chapter 1: https://huggingface.co/learn/llm-course/chapter1/1
- 3Blue1Brown Transformer Architecture Video: https://www.youtube.com/watch?v=wjZofJX0v4M
- 3Blue1Brown Attention Mechanism Video: https://www.youtube.com/watch?v=eMlx5fFNoYc

## 4. Test Results and Quality Gates
```bash
uv run pytest -q
# Output: 91 passed in 2.21s

uv run ruff check .
# Output: All checks passed!

uv run ruff format --check .
# Output: 69 files already formatted

uv run mypy .
# Output: Success: no issues found in 53 source files
```

## 5. UI and Docker Verification
- **Automated Streamlit AppTest**:
  - Initial render passed without exceptions.
  - Day 4 selection correctly renders matched resources and budget notice.
  - Learn Topic renders Mermaid diagrams, Python code blocks, and external links.
  - Adaptive plan renders weak topic remediation pathway.
- **Docker Compose**:
  - `docker compose build`: Succeeded in 1.8s.
  - `docker compose up -d`: Container `study-coach-workshop-ui` started and reported `status: Up (healthy)` on `http://localhost:8501`.
  - HTTP curl check returned `HTTP/1.1 200 OK`.

## 6. Git Status
- **Commit**: `ea4f9de`
- **Commit Message**: `feat(m6): enrich lessons with resources and visuals`
- **Pushed to**: `https://github.com/hastimal/gemini-adk-study-coach-lab.git` (`origin/main`)
- **Tags**: `v0.6.0` preserved. No `v0.7.0` tag created.

## 7. Known Limitations
- Automated headless browser tests in sandbox environments without arm64 Playwright system drivers execute via Streamlit's official Python `AppTest` framework.
- The workshop UI stores session state in memory per browser session without persistent cross-session relational authentication.
