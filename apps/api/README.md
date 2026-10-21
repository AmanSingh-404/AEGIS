# AEGIS API

FastAPI backend service for the AEGIS platform.

## Requirements

- Python 3.14
- uv

## Install dependencies

From the repository root:

    uv sync --directory apps/api

## Run the API

From the repository root:

    uv run --directory apps/api uvicorn api.main:app --host 127.0.0.1 --port 8000

## Health check

- Endpoint: GET /api/v1/health
- Expected response: {"status":"ok"}

## Interactive API documentation

When the API is running, open http://127.0.0.1:8000/docs.

## Development status

This is the initial backend foundation. The health endpoint is implemented;
other API operations remain to be developed.
