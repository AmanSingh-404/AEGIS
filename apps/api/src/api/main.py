import structlog
from fastapi import FastAPI

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="AEGIS API",
    description="Agentic AI Engineering, Governance, Intelligence, and Security Platform",
    version="0.1.0",
)


@app.get("/api/v1/health", tags=["Health"])
async def health() -> dict[str, str]:
    logger.info("health_check", endpoint="/api/v1/health", status="ok")
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)
