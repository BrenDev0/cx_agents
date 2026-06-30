# Stage 1: Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked --no-cache


# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/

RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "src.api.main"]