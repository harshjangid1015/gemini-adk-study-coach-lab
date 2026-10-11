"""Developer Lab Launcher UI for Gemini ADK Study Coach.

Provides a convenient local developer gateway to:
1. Google ADK Developer UI
2. Streamlit Study Coach
3. Streamlit Agent Ops tab
4. Streamlit Evaluations tab
5. Grafana Dashboard
6. Grafana Tempo Explore
7. Prometheus Scraper & TSDB
"""

import sys
from pathlib import Path

# Ensure project root and src are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st

from study_coach.services.launcher import get_all_services_status

st.set_page_config(
    page_title="Gemini ADK Developer Lab Launcher",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚀 Gemini ADK Study Coach — Developer Lab Launcher")
st.caption(
    "Unified developer gateway connecting Google ADK Developer UI, Streamlit Workshop App, "
    "Agent Ops, Visual Evaluations, Grafana Dashboards, Tempo Tracing, and Prometheus."
)

# Refresh toolbar
col_header, col_refresh = st.columns([4, 1])
with col_refresh:
    if st.button("🔄 Refresh Health Status", use_container_width=True):
        st.rerun()

services = get_all_services_status()

# Metrics overview bar
online_count = sum(1 for s in services if s.is_online)
total_count = len(services)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(
        "Services Online",
        f"{online_count} / {total_count}",
        delta="All Systems Normal"
        if online_count == total_count
        else f"{total_count - online_count} Offline",
        delta_color="normal" if online_count == total_count else "inverse",
    )
with m2:
    adk_svc = next((s for s in services if s.id == "adk_ui"), None)
    adk_status = "Online (Port 8000)" if (adk_svc and adk_svc.is_online) else "Offline"
    st.metric("Google ADK UI", adk_status)
with m3:
    ui_svc = next((s for s in services if s.id == "study_coach"), None)
    ui_status = "Online (Port 8501)" if (ui_svc and ui_svc.is_online) else "Offline"
    st.metric("Study Coach App", ui_status)
with m4:
    prom_svc = next((s for s in services if s.id == "prometheus"), None)
    obs_status = "Active (Docker)" if (prom_svc and prom_svc.is_online) else "Offline"
    st.metric("Observability Stack", obs_status)

st.markdown("---")

# Port conflict / warning guidance
adk_svc = next((s for s in services if s.id == "adk_ui"), None)
if adk_svc and not adk_svc.is_online:
    st.warning(
        "⚠️ **Google ADK UI is not running on port 8000**.\n\n"
        "To launch the ADK Developer UI directly, run:\n"
        "```bash\n"
        "./scripts/run_local.sh --adk-only\n"
        "# Or on a custom port if port 8000 is occupied by Docker:\n"
        "uv run adk web --port 8080\n"
        "```"
    )

st.subheader("🌐 Quick Navigation Hub")

# Render 2-column service cards
cols = st.columns(2)

for idx, svc in enumerate(services):
    col = cols[idx % 2]
    with col:
        badge_emoji = "🟢" if svc.is_online else "🔴"
        status_text = svc.status_detail

        # Card container with rich aesthetic
        border_color = "#34a853" if svc.is_online else "#ea4335"
        bg_color = "#ffffff"

        card_html = f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-left: 6px solid {border_color};
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            background-color: {bg_color};
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        ">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <h3 style="margin: 0; font-size: 18px; color: #1a73e8;">{svc.name}</h3>
                <span style="font-size: 13px; font-weight: bold; color: {"#137333" if svc.is_online else "#c5221f"};">
                    {badge_emoji} {status_text}
                </span>
            </div>
            <p style="margin: 4px 0 10px 0; font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">
                {svc.category} &bull; Port {svc.port}
            </p>
            <p style="margin: 0 0 14px 0; font-size: 14px; color: #3c4043; line-height: 1.4;">
                {svc.description}
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <code style="font-size: 12px; background: #f1f3f4; padding: 2px 6px; border-radius: 4px;">{svc.url}</code>
                <a href="{svc.url}" target="_blank" style="
                    display: inline-block;
                    padding: 6px 14px;
                    background-color: #1a73e8;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: 500;
                ">
                    {svc.action_label} ↗
                </a>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")

# Help & Commands Expander
with st.expander("🛠️ Developer Commands Cheat Sheet"):
    st.markdown(
        """
        ### 1. Launch Options
        - **Unified Lab Launcher (this screen)**:
          ```bash
          ./scripts/run_local.sh
          ```
        - **Google ADK UI Standalone**:
          ```bash
          ./scripts/run_local.sh --adk-only
          ```
        - **Docker Observability Stack**:
          ```bash
          docker compose --profile observability up -d
          ```

        ### 2. Port Allocation Reference
        | Service | Port | Notes |
        |---|---|---|
        | **Developer Lab Launcher** | `8500` | Streamlit launcher hub |
        | **Google ADK UI** | `8000` | FastAPI server (`adk web`) |
        | **Study Coach UI** | `8501` | Main student workshop application |
        | **Grafana** | `3000` | Auto-provisioned dashboards |
        | **Tempo** | `3200` | Trace query / OTLP gRPC: 4317, HTTP: 4318 |
        | **Prometheus** | `9090` | Time-series scraper |
        """
    )
