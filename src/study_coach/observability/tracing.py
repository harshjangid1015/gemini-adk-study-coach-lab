"""OpenTelemetry tracing setup and tracer utilities for study-coach."""

import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.trace import Tracer

from study_coach.observability.config import ObservabilityConfig

logger = logging.getLogger(__name__)

_TRACER_PROVIDER: TracerProvider | None = None
_TRACER: Tracer | None = None


def setup_tracing(config: ObservabilityConfig | None = None) -> Tracer:
    """Initializes OpenTelemetry TracerProvider with OTLP exporter.

    If OTLP collector is unreachable or disabled, falls back cleanly to no-op.
    """
    global _TRACER_PROVIDER, _TRACER

    if _TRACER is not None:
        return _TRACER

    cfg = config or ObservabilityConfig.from_env()

    if not cfg.enabled or not cfg.export_traces:
        _TRACER = trace.get_tracer(cfg.service_name, cfg.service_version)
        return _TRACER

    resource = Resource.create(
        {
            "service.name": cfg.service_name,
            "service.version": cfg.service_version,
            "deployment.environment": cfg.environment,
        }
    )

    provider = TracerProvider(resource=resource)

    # Configure exporter safely
    try:
        from opentelemetry.sdk.trace import SpanProcessor
        from opentelemetry.sdk.trace.export import SpanExporter

        exporter: SpanExporter
        if cfg.otlp_protocol == "grpc":
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            exporter = OTLPSpanExporter(endpoint=cfg.otlp_endpoint, insecure=True)
        else:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter as HttpOTLPSpanExporter,
            )

            # Ensure /v1/traces path is attached if root endpoint is passed
            endpoint = cfg.otlp_endpoint.rstrip("/")
            if not endpoint.endswith("/v1/traces"):
                endpoint = f"{endpoint}/v1/traces"
            exporter = HttpOTLPSpanExporter(endpoint=endpoint)

        processor: SpanProcessor
        if cfg.environment in ("test", "testing"):
            processor = SimpleSpanProcessor(exporter)
        else:
            processor = BatchSpanProcessor(exporter)

        provider.add_span_processor(processor)
    except (ImportError, RuntimeError, ValueError) as err:
        logger.warning(
            "Failed to configure OpenTelemetry OTLP trace exporter (%s). Falling back to in-memory tracing.",
            err,
        )

    trace.set_tracer_provider(provider)
    _TRACER_PROVIDER = provider
    _TRACER = provider.get_tracer(cfg.service_name, cfg.service_version)
    return _TRACER


def get_tracer() -> Tracer:
    """Returns the configured global Tracer, initializing if needed."""
    if _TRACER is None:
        return setup_tracing()
    return _TRACER


def shutdown_tracing() -> None:
    """Flushes and shuts down the active TracerProvider safely."""
    global _TRACER_PROVIDER, _TRACER
    if _TRACER_PROVIDER is not None:
        try:
            _TRACER_PROVIDER.shutdown()
        except (RuntimeError, ValueError) as err:
            logger.warning("Error shutting down TracerProvider: %s", err)
        _TRACER_PROVIDER = None
        _TRACER = None
