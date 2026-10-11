"""Agent Operations & Observability UI Component.

Renders Prometheus service health, active links to Grafana and Tempo,
and status indications for the observability stack.
"""

import urllib.error
import urllib.request

import streamlit as st

GRAFANA_URL = "http://localhost:3000/d/study-coach-main/study-coach-lab-observability-telemetry?orgId=1&refresh=5s"
TEMPO_URL = "http://localhost:3000/explore?orgId=1&left=%7B%22datasource%22:%22Tempo%22,%22queries%22:%5B%7B%22refId%22:%22A%22%7D%5D%7D"
PROMETHEUS_HEALTH_URL = "http://localhost:9090/-/healthy"
PROMETHEUS_TARGETS_URL = "http://localhost:9090/targets"


def check_prometheus_health() -> bool:
    """Checks if Prometheus server is online and responding at port 9090."""
    try:
        req = urllib.request.Request(PROMETHEUS_HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return bool(resp.status == 200)
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def render_agent_ops_tab() -> None:
    """Renders the Agent Ops overview tab with live observability health and links."""
    st.header("🔭 Agent Ops & Observability Stack")
    st.write(
        "Monitor live OpenTelemetry distributed traces, Prometheus metrics, and Grafana "
        "dashboards for the Google ADK multi-agent swarm in real time."
    )

    is_prom_healthy = check_prometheus_health()

    # Health Indicators Row
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

    with col_stat1:
        if is_prom_healthy:
            st.metric("Prometheus (Port 9090)", "Online", delta="Healthy")
        else:
            st.metric(
                "Prometheus (Port 9090)",
                "Offline",
                delta="-Unreachable",
                delta_color="inverse",
            )

    with col_stat2:
        if is_prom_healthy:
            st.metric("Tempo Tracing (Port 3200)", "Online", delta="Ready")
        else:
            st.metric(
                "Tempo Tracing (Port 3200)",
                "Unknown",
                delta="-Prometheus offline",
                delta_color="inverse",
            )

    with col_stat3:
        if is_prom_healthy:
            st.metric("Grafana UI (Port 3000)", "Online", delta="Port 3000")
        else:
            st.metric(
                "Grafana UI (Port 3000)",
                "Offline / Standby",
                delta="-Needs profile",
                delta_color="inverse",
            )

    with col_stat4:
        st.metric("App Metrics Exporter", "Port 8000", delta="/metrics")

    st.markdown("---")

    # Observability Navigation Links
    st.subheader("📊 Observability Portals")
    col_link1, col_link2, col_link3 = st.columns(3)

    with col_link1:
        st.markdown(
            f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
                <h4 style="margin-top: 0;">📈 Grafana Dashboard</h4>
                <p style="color: #555; font-size: 14px;">View agent invocations, token consumption, latency histograms, and budget alerts.</p>
                <a href="{GRAFANA_URL}" target="_blank" style="display: inline-block; padding: 8px 16px; background-color: #1a73e8; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                    Open Grafana Dashboard ↗
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_link2:
        st.markdown(
            f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
                <h4 style="margin-top: 0;">🔍 Tempo Trace Explorer</h4>
                <p style="color: #555; font-size: 14px;">Inspect distributed spans, tool execution, and root-agent-to-subagent delegations.</p>
                <a href="{TEMPO_URL}" target="_blank" style="display: inline-block; padding: 8px 16px; background-color: #0f9d58; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                    Open Tempo Explore ↗
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_link3:
        st.markdown(
            f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
                <h4 style="margin-top: 0;">🎯 Prometheus Targets</h4>
                <p style="color: #555; font-size: 14px;">Verify scraper health, active endpoints, and raw scrape intervals.</p>
                <a href="{PROMETHEUS_TARGETS_URL}" target="_blank" style="display: inline-block; padding: 8px 16px; background-color: #ea4335; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                    Open Prometheus ↗
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Service Instructions & Offline Banner
    if not is_prom_healthy:
        st.warning(
            "⚠️ **Observability Services Offline**: The Prometheus, Tempo, or Grafana containers "
            "are currently not responding on localhost ports (3000, 3200, 9090).\n\n"
            "To launch the full observability stack, start Docker Compose with the `observability` profile:\n\n"
            "```bash\n"
            "docker compose --profile observability up -d\n"
            "```"
        )
    else:
        st.success(
            "✅ **Telemetry Pipeline Active**: OTLP Spans and Prometheus metrics are flowing from the "
            "Study Coach application to OpenTelemetry Collector, Tempo, and Prometheus."
        )

    with st.expander("ℹ️ Telemetry Architecture & Port Map"):
        st.markdown(
            """
            - **Streamlit Web UI**: `http://localhost:8501`
            - **Prometheus Metrics Exporter**: `http://localhost:8000/metrics`
            - **Prometheus Server**: `http://localhost:9090`
            - **Grafana Dashboard**: `http://localhost:3000` (User: `admin`, Pass: `admin` / Anonymous enabled)
            - **Grafana Tempo (HTTP query)**: `http://localhost:3200`
            - **OpenTelemetry Collector OTLP HTTP/gRPC**: Ports `4318` / `4317`
            """
        )
