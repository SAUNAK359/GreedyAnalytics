from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from core.config import settings


def init_telemetry(app):
    if not settings.ENABLE_TELEMETRY:
        return

    trace.set_tracer_provider(TracerProvider())

    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    else:
        exporter = ConsoleSpanExporter()

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(exporter)
    )

    FastAPIInstrumentor.instrument_app(app)
