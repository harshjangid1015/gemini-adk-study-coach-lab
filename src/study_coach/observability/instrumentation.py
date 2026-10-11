"""Google ADK Plugin and contextual span decorators for study-coach observability."""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.genai import types
from opentelemetry.trace import Status, StatusCode, Tracer

from study_coach.config import GEMINI_MODEL
from study_coach.observability import metrics
from study_coach.observability.tracing import get_tracer

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def sanitize_value(val: Any) -> str:
    """Scrub sensitive credentials, tokens, and PII from telemetry attribute values."""
    if not isinstance(val, str):
        val = str(val)
    # Redact common Gemini/Google API key patterns (AIzaSy...)
    import re

    redacted = re.sub(r"AIzaSy[A-Za-z0-9_-]+", "[REDACTED_API_KEY]", val)
    return redacted


class ADKObservabilityPlugin(BasePlugin):
    """Native Google ADK BasePlugin bridging ADK agent execution to OpenTelemetry and Prometheus."""

    def __init__(self, tracer: Tracer | None = None) -> None:
        super().__init__(name="adk_observability_plugin")
        self.tracer: Tracer = tracer or get_tracer()
        self._active_spans: dict[str, Any] = {}
        self._tool_spans: dict[str, Any] = {}
        self._start_times: dict[str, float] = {}

    async def before_run_callback(
        self, *, invocation_context: Any
    ) -> types.Content | None:
        """Called by ADK runner before an agent run starts."""
        try:
            agent = getattr(invocation_context, "agent", None)
            agent_name = getattr(agent, "name", "study_coach")
            model = getattr(agent, "model", GEMINI_MODEL)
            session_id = getattr(invocation_context, "session_id", "default_session")

            metrics.AGENT_CALLS_TOTAL.labels(agent=agent_name, model=model).inc()

            span = self.tracer.start_span(
                f"adk.agent.{agent_name}",
                attributes={
                    "study_coach.workflow": "agent_execution",
                    "study_coach.agent": agent_name,
                    "study_coach.model": str(model),
                    "study_coach.operation": "run",
                },
            )
            key = f"{session_id}_{agent_name}"
            self._active_spans[key] = span
            self._start_times[key] = time.time()
        except (AttributeError, RuntimeError, ValueError) as err:
            logger.debug("Error in before_run_callback: %s", err)
        return None

    async def after_run_callback(self, *, invocation_context: Any) -> None:
        """Called by ADK runner after an agent run completes."""
        try:
            agent = getattr(invocation_context, "agent", None)
            agent_name = getattr(agent, "name", "study_coach")
            session_id = getattr(invocation_context, "session_id", "default_session")
            key = f"{session_id}_{agent_name}"

            span = self._active_spans.pop(key, None)
            if span:
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("study_coach.status", "success")
                span.end()
        except (AttributeError, RuntimeError, ValueError) as err:
            logger.debug("Error in after_run_callback: %s", err)

    async def on_run_error_callback(
        self, *, invocation_context: Any, error: Exception
    ) -> None:
        """Called when an agent run errors."""
        try:
            agent = getattr(invocation_context, "agent", None)
            agent_name = getattr(agent, "name", "study_coach")
            session_id = getattr(invocation_context, "session_id", "default_session")
            key = f"{session_id}_{agent_name}"

            err_type = type(error).__name__
            metrics.AGENT_ERRORS_TOTAL.labels(
                agent=agent_name, error_type=err_type
            ).inc()

            span = self._active_spans.pop(key, None)
            if span:
                span.set_status(Status(StatusCode.ERROR, description=str(error)))
                span.set_attribute("study_coach.status", "error")
                span.set_attribute("study_coach.error_type", err_type)
                span.record_exception(error)
                span.end()
        except (AttributeError, RuntimeError, ValueError) as err:
            logger.debug("Error in on_run_error_callback: %s", err)

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: Any,
    ) -> dict[str, Any] | None:
        """Called before an agent invokes a tool."""
        try:
            tool_name = getattr(tool, "name", getattr(tool, "__name__", "unknown_tool"))
            metrics.TOOL_CALLS_TOTAL.labels(tool=tool_name, status="invoked").inc()

            span = self.tracer.start_span(
                f"adk.tool.{tool_name}",
                attributes={
                    "study_coach.workflow": "tool_execution",
                    "study_coach.operation": tool_name,
                },
            )
            self._tool_spans[tool_name] = span
        except (AttributeError, RuntimeError, ValueError) as err:
            logger.debug("Error in before_tool_callback: %s", err)
        return None

    async def after_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: Any,
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Called after an agent tool invocation finishes."""
        try:
            tool_name = getattr(tool, "name", getattr(tool, "__name__", "unknown_tool"))
            span = self._tool_spans.pop(tool_name, None)
            if span:
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("study_coach.status", "success")
                span.end()
        except (AttributeError, RuntimeError, ValueError) as err:
            logger.debug("Error in after_tool_callback: %s", err)
        return None

    async def on_tool_error_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: Any,
        error: Exception,
    ) -> None:
        """Called when tool execution raises an exception."""
        try:
            tool_name = getattr(tool, "name", getattr(tool, "__name__", "unknown_tool"))
            span = self._tool_spans.pop(tool_name, None)
            if span:
                span.set_status(Status(StatusCode.ERROR, description=str(error)))
                span.set_attribute("study_coach.status", "error")
                span.set_attribute("study_coach.error_type", type(error).__name__)
                span.record_exception(error)
                span.end()
        except (AttributeError, RuntimeError, ValueError) as err:
            logger.debug("Error in on_tool_error_callback: %s", err)


def trace_workflow_step(
    operation_name: str,
    workflow: str,
    agent: str | None = None,
    quiz_type: str | None = None,
) -> Callable[[F], F]:
    """Decorator for tracing higher-level asynchronous application workflow boundaries."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            start_time = time.time()
            span_name = f"study_coach.{operation_name}"

            attrs = {
                "study_coach.workflow": workflow,
                "study_coach.operation": operation_name,
            }
            if agent:
                attrs["study_coach.agent"] = agent
            if quiz_type:
                attrs["study_coach.quiz_type"] = quiz_type

            with tracer.start_as_current_span(span_name, attributes=attrs) as span:
                try:
                    res = await func(*args, **kwargs)
                    duration = time.time() - start_time

                    span.set_status(Status(StatusCode.OK))
                    span.set_attribute("study_coach.status", "success")

                    metrics.REQUESTS_TOTAL.labels(
                        workflow=workflow, status="success"
                    ).inc()
                    metrics.REQUEST_DURATION_SECONDS.labels(
                        workflow=workflow, status="success"
                    ).observe(duration)

                    return res
                except Exception as exc:
                    duration = time.time() - start_time
                    err_type = type(exc).__name__

                    span.set_status(Status(StatusCode.ERROR, description=str(exc)))
                    span.set_attribute("study_coach.status", "error")
                    span.set_attribute("study_coach.error_type", err_type)
                    span.record_exception(exc)

                    metrics.REQUESTS_TOTAL.labels(
                        workflow=workflow, status="error"
                    ).inc()
                    metrics.REQUEST_DURATION_SECONDS.labels(
                        workflow=workflow, status="error"
                    ).observe(duration)

                    raise

        return wrapper  # type: ignore[return-value]

    return decorator
