# main.py
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from opentelemetry import trace, propagate
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagators.aws import AwsXRayPropagator
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator
from opentelemetry.sdk.resources import Resource

from src.core.init_db import create_db_and_tables
from src.modules.hero.api import router as hero_router
from logger import get_logger  # your logger.py from earlier

logger = get_logger(__name__)

# ── Step 1: Configure ADOT / X-Ray ──────────────────────────────────────────
propagate.set_global_textmap(AwsXRayPropagator())

resource = Resource.create({
    "service.name": os.getenv("OTEL_SERVICE_NAME", "fastapi-app"),
    "service.version": "1.0.0",
    "deployment.environment": os.getenv("ENVIRONMENT", "production"),
})

tracer_provider = TracerProvider(
    resource=resource,
    id_generator=AwsXRayIdGenerator()
)

otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    insecure=True
)

tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

# ── Step 2: Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    await create_db_and_tables()
    logger.info("Database initialized")
    yield
    logger.info("Application shutting down")

# ── Step 3: FastAPI App ───────────────────────────────────────────────────────
app = FastAPI(
    title="Hero API",
    lifespan=lifespan
)

# ── Step 4: Auto-instrument FastAPI ──────────────────────────────────────────
FastAPIInstrumentor.instrument_app(app)

# ── Step 5: Request logging middleware ───────────────────────────────────────
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Request started", extra={
        "method": request.method,
        "path":   request.url.path,
    })

    response = await call_next(request)

    logger.info("Request completed", extra={
        "method":      request.method,
        "path":        request.url.path,
        "status_code": response.status_code,
    })

    return response

# ── Step 6: Include Routers ───────────────────────────────────────────────────
app.include_router(hero_router)
