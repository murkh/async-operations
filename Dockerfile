FROM python:3.11-slim AS base

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Base app layer
FROM base AS app
COPY app /app/app
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Base worker layer
FROM base AS worker
COPY app /app/app
COPY worker /app/worker
ENV PYTHONPATH=/app
CMD ["python", "-m", "worker.main"]
