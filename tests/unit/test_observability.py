"""Unit tests for OpenTelemetry instrumentation and Prometheus metrics."""

from unittest.mock import MagicMock

import pytest

from study_coach.observability.config import ObservabilityConfig
from study_coach.observability.instrumentation import (
    ADKObservabilityPlugin,
    sanitize_value,
    trace_workflow_step,
)
from study_coach.observability.tracing import (
    setup_tracing,
)


def test_observability_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_ENABLED", raising=False)
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    cfg = ObservabilityConfig.from_env()
    assert cfg.service_name == "study-coach"
    assert cfg.environment == "development"
    assert cfg.otlp_protocol == "http"


def test_sanitize_value_scrubs_secrets() -> None:
    text = "AIzaSyABC12345 is my secret key"
    sanitized = sanitize_value(text)
    assert "[REDACTED_API_KEY]" in sanitized
    assert "AIzaSy" not in sanitized


def test_tracing_fallback_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OTEL_ENABLED", "false")
    tracer = setup_tracing()
    assert tracer is not None
    # Creating a span should succeed in no-op mode without error
    with tracer.start_as_current_span("test_span") as span:
        assert span is not None


@pytest.mark.anyio
async def test_adk_observability_plugin_lifecycle() -> None:
    plugin = ADKObservabilityPlugin()
    assert plugin.name == "adk_observability_plugin"

    # Mock invocation context
    mock_context = MagicMock()
    mock_context.agent.name = "mock_agent"
    mock_context.session_id = "mock_session_123"

    # before_run_callback
    await plugin.before_run_callback(invocation_context=mock_context)
    span = plugin._active_spans.get("mock_session_123_mock_agent")
    assert span is not None

    # tool callbacks
    mock_tool = MagicMock()
    mock_tool.name = "validate_study_plan"
    await plugin.before_tool_callback(
        tool=mock_tool, tool_args={"data": 123}, tool_context=mock_context
    )
    await plugin.after_tool_callback(
        tool=mock_tool,
        tool_args={"data": 123},
        tool_context=mock_context,
        result={"status": "ok"},
    )

    # after_run_callback
    await plugin.after_run_callback(invocation_context=mock_context)
    assert "mock_session_123_mock_agent" not in plugin._active_spans


@pytest.mark.anyio
async def test_adk_observability_plugin_error_handling() -> None:
    plugin = ADKObservabilityPlugin()
    mock_context = MagicMock()
    mock_context.agent.name = "mock_agent"
    mock_context.session_id = "mock_session_err"

    await plugin.before_run_callback(invocation_context=mock_context)
    err = RuntimeError("Simulated failure")
    await plugin.on_run_error_callback(invocation_context=mock_context, error=err)
    assert "mock_session_err_mock_agent" not in plugin._active_spans


@pytest.mark.anyio
async def test_trace_workflow_step_decorator() -> None:
    @trace_workflow_step("test_step", workflow="test_workflow", agent="test_agent")
    async def sample_func(x: int) -> int:
        return x * 2

    res = await sample_func(5)
    assert res == 10


@pytest.mark.anyio
async def test_trace_workflow_step_decorator_handles_error() -> None:
    @trace_workflow_step("failing_step", workflow="test_workflow")
    async def sample_failing_func() -> None:
        raise ValueError("Simulated step failure")

    with pytest.raises(ValueError, match="Simulated step failure"):
        await sample_failing_func()
