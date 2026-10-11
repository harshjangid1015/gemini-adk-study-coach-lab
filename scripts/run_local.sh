#!/usr/bin/env bash
set -e

# Default port for Developer Lab Launcher
LAUNCHER_PORT="${LAUNCHER_PORT:-8500}"

# Help message
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./scripts/run_local.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --launcher          Launch the Developer Lab Launcher GUI (default, port 8500)"
    echo "  --adk-only          Launch only the standalone Google ADK Developer UI (port 8000)"
    echo "  --port <PORT>       Specify a custom port for the launcher (default: 8500)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/run_local.sh               # Starts Developer Lab Launcher at http://localhost:8500"
    echo "  ./scripts/run_local.sh --adk-only    # Starts Google ADK Developer UI directly"
    echo "  ./scripts/run_local.sh --port 8502   # Starts Launcher on custom port"
    exit 0
fi

# ADK-only standalone workflow
if [ "$1" = "--adk-only" ]; then
    echo "Starting Google ADK Developer UI..."
    exec uv run adk web
fi

# Parse custom port if provided
if [ "$1" = "--port" ] && [ -n "$2" ]; then
    LAUNCHER_PORT="$2"
fi

echo "================================================================================"
echo "🚀 STARTING GEMINI ADK DEVELOPER LAB LAUNCHER"
echo "================================================================================"
echo "Launcher URL: http://localhost:${LAUNCHER_PORT}"
echo ""
echo "From this launcher GUI, you can access and monitor:"
echo "  1. Google ADK Developer UI       (http://127.0.0.1:8000)"
echo "  2. Streamlit Study Coach         (http://localhost:8501)"
echo "  3. Streamlit Agent Ops Tab       (http://localhost:8501/?tab=ops)"
echo "  4. Streamlit Evaluations Tab     (http://localhost:8501/?tab=eval)"
echo "  5. Grafana Dashboard             (http://localhost:3000)"
echo "  6. Grafana Tempo Explore         (http://localhost:3000/explore)"
echo "  7. Prometheus Scraper & TSDB     (http://localhost:9090)"
echo ""
echo "Note: To launch the standalone ADK UI directly without launcher, use:"
echo "      ./scripts/run_local.sh --adk-only"
echo "================================================================================"

exec uv run streamlit run ui/launcher_app.py --server.port "${LAUNCHER_PORT}" --server.headless true
