import contextvars
import uuid

import structlog
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from api.config import get_settings
from api.database import engine, get_db
from api.routes.llm import router as llm_router


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


app.include_router(llm_router)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
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


@app.get("/api/v1/health/ready", tags=["Health"])
async def readiness() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("readiness_check_failed", dependency="postgres")
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "dependency": "postgres"},
        ) from None

    logger.info("readiness_check", status="ready", dependency="postgres")
    return {"status": "ready", "database": "ok"}


@app.get("/api/v1/health/db-session", tags=["Health"])
def database_session_check(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("database_session_check_failed")
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "dependency": "postgres"},
        ) from None

    logger.info("database_session_check", status="ok")
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)
