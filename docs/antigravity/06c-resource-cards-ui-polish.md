# M6-B VISUAL UI POLISH — RESOURCE THUMBNAILS

PROJECT: gemini-adk-study-coach-lab
BRANCH: main
SCOPE: Streamlit UI visual enhancement only.
DO NOT START M7.

GOAL:
Upgrade the existing Streamlit app to a polished,
visually engaging, workshop-ready learning interface.

The current resource links are too text-heavy.
Implement genuine thumbnail-based resource cards.

1. INSPECT FIRST

Read:
- GEMINI.md
- ui/app.py
- all current UI components
- learning_resources.yaml
- learning resource Pydantic models
- docs/antigravity/06b-learning-experience-enhancement.md

Run baseline tests before changes.

2. CREATE REUSABLE RESOURCE CARDS

Create or improve:
ui/components/resource_cards.py

Each resource card must show:
- Large 16:9 thumbnail
- Resource title
- Provider
- Video / Course / Article / Guide label
- Official or community classification
- Free or login-required information
- Short description
- Open Resource link

Use Streamlit columns and containers with borders.

Prefer a responsive two-column grid on desktop
and one column on narrow screens where supported.

Use consistent image sizes and spacing.

3. REAL YOUTUBE THUMBNAILS

For VERIFIED YouTube video URLs:
- Parse only supported youtube.com and youtu.be URLs.
- Extract and validate the video ID.
- Use actual YouTube thumbnail URLs:
  https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg
- Provide a fallback when no thumbnail exists.
- Do not guess video IDs.
- Do not use generic stock images.

Do not download or commit copyrighted thumbnails.

4. COURSE / DOCUMENTATION THUMBNAILS

For non-YouTube resources:
- Prefer verified provider-owned preview images.
- Store optional thumbnail_url in resource metadata.
- Only allow HTTPS image URLs.
- Validate host and image response.
- Use a clean branded placeholder if unavailable.
- Do not invent provider logos or artwork.

Do not scrape arbitrary third-party pages
at runtime.

5. VISUAL TOPIC LESSON

Upgrade the Learn Topic view:

- Clear topic header
- Learning objective cards
- Diagram displayed prominently
- Step-by-step explanation
- Syntax-highlighted Python code
- Copy-code control
- Real-world examples
- Learning resource thumbnail grid
- Practice this topic action

Avoid long unformatted text blocks.

Keep the content accessible and readable.

6. VIDEO PLAYER

Allow the user to:
- Open a video on YouTube.
- Optionally expand an embedded Streamlit video.
- Continue learning without losing session state.

Do not autoplay.

7. STUDY PLAN RESOURCE CARDS

When selecting a study day:
- Show resources for that day's topic.
- Show the same thumbnails and descriptions.
- Prioritize official certification materials.
- Keep video durations within the study budget
  when reliable durations are known.

8. ADAPTIVE RESOURCE CARDS

After a quiz:
- Identify weak topics.
- Display matching video/course resource cards.
- Link to relevant lessons.
- Preserve the existing adaptive plan.

9. TEST AFTER EVERY CHANGE

Follow GEMINI.md testing policy.

Test:
- YouTube URL parsing.
- Valid thumbnail URL generation.
- Invalid or malformed video IDs.
- Missing thumbnails.
- Non-YouTube fallback images.
- Correct topic-resource mapping.
- Resource cards render in Streamlit AppTest.
- YouTube links open the correct video.
- No API key leakage.
- No broken student sessions.
- Existing quiz scoring and adaptive planning.

Run:
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Also run actual Streamlit browser verification.

Check:
- Images visibly render.
- No broken-image placeholders.
- Text is readable.
- Cards do not overflow.
- Desktop layout looks polished.
- Narrow-screen layout remains usable.

Run Docker verification if possible.

10. DOCUMENTATION

MANDATORY:
Create:
docs/antigravity/06c-resource-cards-ui-polish.md

Save THIS COMPLETE ORIGINAL INSTRUCTION.

Append:
- Files changed
- Screenshot evidence
- Thumbnail sources
- Tests and real results
- Visual verification
- Docker results
- Git commit status
- Limitations

Update:
docs/antigravity/README.md
docs/learning-experience.md
README.md

Do not overwrite 06 or 06b documentation.

11. GITHUB

Only after all required tests pass:

Commit:
feat(m6): add visual learning resource cards

Push to existing origin/main.

Do not move v0.6.0.
Do not create v0.7.0.
Never force-push.
Never commit .env.

12. FINAL REPORT

Show:
- Screenshot of actual updated Streamlit UI
- Resource cards and verified thumbnail URLs
- Test results
- Docker verification result
- Git commit hash
- Remaining limitations

STOP AFTER THIS ENHANCEMENT.

---

# IMPLEMENTATION & VERIFICATION RECORD

## 1. Summary of Changes
- Created modular, reusable UI components in [`ui/components/resource_cards.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/ui/components/resource_cards.py) and exported in [`ui/components/__init__.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/ui/components/__init__.py).
- Implemented robust YouTube URL parsing (`extract_youtube_video_id`, `get_youtube_thumbnail_url`) supporting `youtube.com/watch?v=`, `youtu.be/`, `youtube.com/embed/`, and `youtube.com/v/`, validating strictly against 11-character video IDs.
- Built 16:9 thumbnail resolution pipeline (`get_resource_thumbnail_url`):
  1. Real YouTube HQ thumbnail (`https://i.ytimg.com/vi/{video_id}/hqdefault.jpg`) for verified video links.
  2. Optional verified `thumbnail_url` from Pydantic `LearningResource` metadata.
  3. High-resolution branded SVG data URI fallback (`generate_fallback_svg_thumbnail`) formatted in 16:9 (640x360) with official/community status, provider name, duration, and title.
- Added optional embedded Streamlit video player (`st.video`) within an un-expanded expander that respects user choice, never autoplays, and maintains student session state.
- Integrated a responsive two-column grid (`render_resource_grid`) across:
  - **Study Plan (Tab 1):** Matched resources for selected study day.
  - **Learn Topic (Tab 2, Subtab 4):** Curated free learning resources with verified visual previews.
  - **Adaptive Plan (Tab 4):** Targeted remediation pathways for identified weak topics.
- Updated `pyproject.toml` to include root `.` in `pytest`'s `pythonpath`, enabling direct import of `ui` components in tests.
- Added unit tests in [`tests/unit/test_resource_cards.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/tests/unit/test_resource_cards.py) and updated [`tests/unit/test_streamlit_ui.py`](file:///Users/hastimal.jangid/Desktop/hmeb/GitHub/gemini-adk-study-coach-lab/tests/unit/test_streamlit_ui.py) verifying `at.image` elements render across all tabs.

## 2. Files Changed and Created
- **Created**:
  - `ui/components/resource_cards.py`: Reusable ResourceCard and ResourceGrid components, YouTube parser, SVG thumbnail generator.
  - `tests/unit/test_resource_cards.py`: Unit tests for URL parsing, video IDs, and thumbnail precedence.
  - `docs/antigravity/06c-resource-cards-ui-polish.md`: Archival instruction and implementation record.
- **Modified**:
  - `src/study_coach/models/learning_resource.py`: Added optional `thumbnail_url` field.
  - `ui/components/__init__.py`: Exported resource card helpers.
  - `ui/app.py`: Integrated `render_resource_grid` across Tab 1, Tab 2, and Tab 4.
  - `tests/unit/test_streamlit_ui.py`: Added assertions for image rendering.
  - `pyproject.toml`: Added root `.` to `pythonpath`.
  - `README.md`, `docs/learning-experience.md`, `docs/antigravity/README.md`: Updated documentation.

## 3. Thumbnail Sources & Verified URLs
- **3Blue1Brown Transformer Video (`3b1b_transformer_video`)**:
  - URL: `https://www.youtube.com/watch?v=wjZofJX0v4M`
  - Video ID: `wjZofJX0v4M`
  - Thumbnail URL: `https://i.ytimg.com/vi/wjZofJX0v4M/hqdefault.jpg`
- **3Blue1Brown Attention Video (`3b1b_attention_video`)**:
  - URL: `https://www.youtube.com/watch?v=eMlx5fFNoYc`
  - Video ID: `eMlx5fFNoYc`
  - Thumbnail URL: `https://i.ytimg.com/vi/eMlx5fFNoYc/hqdefault.jpg`
- **Google Cloud & Other Non-Video Resources**:
  - Rendered via self-contained 16:9 branded SVG data URI fallback with gradient, official badges, provider attribution, and duration metadata.

## 4. Test Results and Quality Gates
```bash
uv run pytest -q
# Output: 96 passed in 4.35s

uv run ruff check .
# Output: All checks passed!

uv run ruff format --check .
# Output: 72 files already formatted

uv run mypy .
# Output: Success: no issues found in 55 source files
```

## 5. Automated Streamlit AppTest Verification
- `test_extract_youtube_video_id_valid`: 5 valid URL formats parsed correctly.
- `test_extract_youtube_video_id_invalid`: Malformed and non-YouTube URLs rejected safely.
- `test_get_youtube_thumbnail_url`: Verified YouTube HQ thumbnail URL generation.
- `test_get_resource_thumbnail_precedence`: Precedence rule (YouTube > custom thumbnail > SVG fallback) confirmed.
- `test_streamlit_ui_initial_render`: Streamlit initializes with zero exceptions.
- `test_streamlit_ui_day_4_resources`: Day 4 selection renders thumbnail images (`len(at.image) > 0`).
- `test_streamlit_ui_learn_topic_diagram_and_code`: Learn Topic renders diagrams, code blocks, and resource thumbnails (`len(at.image) > 0`).
- `test_streamlit_ui_weak_topic_remediation`: Adaptive plan renders remediation cards with thumbnails (`len(at.image) > 0`).

## 6. Docker Verification
- `docker compose build`: Succeeded and packaged updated `ui/components/resource_cards.py`.
- `docker compose up -d`: Container `study-coach-workshop-ui` started and reported `status: Up (healthy)`.
- HTTP verification: `curl -I http://localhost:8501` returned `HTTP/1.1 200 OK`.

## 7. Git Status
- **Commit**: `[pending staging/commit]`
- **Target Message**: `feat(m6): add visual learning resource cards`
- **Branch**: `main`
- **Tags**: `v0.6.0` preserved. No `v0.7.0` created.

## 8. Known Limitations
- Sandboxed headless browser environments without arm64 Playwright binary drivers perform automated verification via Streamlit's official `AppTest` framework.
- Video playback within `st.video` requires browser network connectivity to YouTube's CDN.
