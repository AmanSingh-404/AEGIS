import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import get_settings
import contextvars
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)
run_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "run_id", default=""
)


def add_context_ids(
    logger: object,
    method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
    event_dict.setdefault("request_id", request_id_var.get())
    event_dict.setdefault("run_id", run_id_var.get())
    return event_dict


structlog.configure(
    processors=[
        add_context_ids,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="Agentic AI Engineering, Governance, Intelligence, and Security Platform",
    version=settings.app_version,
)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or __import__(
            "uuid"
        ).uuid4().hex

        request_token = request_id_var.set(request_id)
        run_token = run_id_var.set(request.headers.get("X-Run-ID", ""))

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(request_token)
            run_id_var.reset(run_token)


app.add_middleware(RequestContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", tags=["Health"])
async def health() -> dict[str, str]:
    logger.info("health_check", endpoint="/api/v1/health", status="ok")
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)
