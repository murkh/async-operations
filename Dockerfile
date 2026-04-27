FROM ghcr.io/astral-sh/uv:python3.11-alpine AS base

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"

# Base app layer
FROM base AS app
COPY app /app/app
COPY worker /app/worker
ENV PYTHONPATH=/app
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Base worker layer
FROM base AS worker
COPY app /app/app
COPY worker /app/worker
ENV PYTHONPATH=/app
CMD ["uv", "run", "celery", "-A", "worker.celery_app", "worker", "--loglevel=info"]