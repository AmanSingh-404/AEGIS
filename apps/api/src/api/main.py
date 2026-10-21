from fastapi import FastAPI

app = FastAPI(
    title="AEGIS API",
    description="Agentic AI Engineering, Governance, Intelligence, and Security Platform",
    version="0.1.0",
)


@app.get("/api/v1/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)
