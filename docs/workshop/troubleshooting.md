# Workshop Troubleshooting Guide

This guide diagnoses and resolves common setup, runtime, API, and network issues encountered during the workshop.

---

## 1. API Key & Authentication Issues

### Symptom: `ValueError: No API key was provided` or `API Key: Not Found`
- **Cause**: The `.env` file does not exist, is in the wrong directory, or does not contain `GOOGLE_API_KEY`.
- **Solution**:
  1. Verify `.env` exists in the repository root:
     ```bash
     ls -la .env
     ```
  2. Ensure the key variable name is `GOOGLE_API_KEY`:
     ```env
     GOOGLE_GENAI_USE_VERTEXAI=FALSE
     GOOGLE_API_KEY=AIzaSy...your_actual_key...
     GEMINI_MODEL=gemini-3.8-flash
     ```
  3. Restart Streamlit or your terminal session so changes take effect.

### Symptom: `429 ResourceExhausted` or Quota Errors
- **Cause**: Free tier Gemini API rate limits (RPM/TPM) reached due to rapid repeated requests.
- **Solution**:
  1. Wait 30–60 seconds before retrying.
  2. Use the default `gemini-3.8-flash` (or `gemini-2.5-flash`), which has higher rate limits.
  3. Use existing saved results in the **Evaluations** tab or offline fixtures in `tests/fixtures/` as a live fallback.

---

## 2. Port Conflicts & Startup Errors

### Symptom: `Address already in use: 8501` or `8000`
- **Cause**: An earlier Streamlit or Python process is still occupying the port.
- **Solution**:
  1. Find and terminate processes running on port 8501 or 8000:
     ```bash
     # macOS / Linux
     lsof -ti :8501 | xargs kill -9
     lsof -ti :8000 | xargs kill -9
     ```
  2. Or start Streamlit on an alternate port:
     ```bash
     uv run streamlit run ui/app.py --server.port 8502
     ```

### Symptom: Docker Port Conflicts
- **Cause**: Local services (e.g., local PostgreSQL, Grafana, or Prometheus) already running on ports 3000, 9090, or 3200.
- **Solution**:
  1. Check running Docker containers: `docker ps`.
  2. Stop conflicting containers: `docker stop <container_id>`.
  3. If Docker is not required, run the app natively without Docker: `uv run streamlit run ui/app.py`.

---

## 3. Python & Dependency Issues

### Symptom: `ModuleNotFoundError: No module named 'study_coach'`
- **Cause**: Streamlit was started from outside the project directory without `PYTHONPATH` or `uv`.
- **Solution**:
  1. Always run using `uv`:
     ```bash
     cd /path/to/gemini-adk-study-coach-lab
     uv run streamlit run ui/app.py
     ```
  2. `ui/app.py` automatically injects `PROJECT_ROOT` and `src` into `sys.path`.

### Symptom: Missing Packages after `git pull`
- **Cause**: Local virtual environment is out of sync with updated `uv.lock`.
- **Solution**:
  ```bash
  uv sync --all-extras --dev
  ```

---

## 4. UI Session & State Reset

### Symptom: Session data disappears after browser reload
- **Cause**: Streamlit stores session state in memory per browser connection tab. Reloading the page reinitializes the connection.
- **Solution**:
  1. Avoid hard-refreshing (`Cmd+R` / `F5`) mid-quiz.
  2. Use the in-app tab buttons to switch views without losing progress.
  3. If reset occurs, click **Start / Reset Session** in the sidebar to begin fresh.
