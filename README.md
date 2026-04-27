# Document Insights API

A production-ready asynchronous document processing system built with FastAPI, MongoDB, and Redis. This application handles long-running document analysis tasks in the background, providing a scalable and resilient architecture for content-heavy operations.

## 🚀 Overview

The Document Insights API allows users to submit documents for processing. Instead of waiting for the processing to complete (which could take time), the API immediately queues the task and returns a document ID. A background worker then processes the queue, updating the document status and generating insights.

### Key Features

- **Asynchronous Task Queueing**: Leverages Redis for high-performance task management.
- **Resilient Background Worker**: Processes tasks with built-in retry logic and exponential backoff.
- **Content-Aware Caching**: Uses SHA-256 content hashing to identify duplicate documents and serve cached results instantly.
- **Rate Limiting**: Intelligent job limiting based on active concurrent tasks per user.
- **Service-Repository Pattern**: Clean, maintainable code architecture decoupling business logic from data access.
- **Full Docker Support**: Easy orchestration of API, Worker, MongoDB, and Redis services.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: [Python 3.11+](https://www.python.org/)
- **Database**: [MongoDB](https://www.mongodb.com/)
- **Task Queue & Cache**: [Redis](https://redis.io/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Containerization**: Docker & Docker Compose

## 📁 Project Structure

```text
├── app/
│   ├── api/             # API routes (FastAPI)
│   ├── core/            # Configuration, database setup, and helpers
│   ├── repositories/    # MongoDB data access layer
│   ├── schemas/         # Pydantic models (Request/Response)
│   ├── services/        # Business logic and external integrations
│   └── main.py          # FastAPI application entry point
├── worker/
│   └── main.py          # Background task processor
├── tests/               # Integration and unit tests
├── Dockerfile           # Multi-stage build for API and Worker
└── docker-compose.yml   # Infrastructure orchestration
```

## 🚦 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [uv](https://github.com/astral-sh/uv) (for local development)

### Running with Docker

The easiest way to get the entire stack running is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/your-username/async-operations.git
cd async-operations

# Start the services
docker-compose up --build
```

The API will be available at `http://localhost:8000`. You can access the interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

### Local Development

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Setup environment**:
   Copy `.env.example` to `.env` and fill in your local MongoDB and Redis credentials.

3. **Run the API**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

4. **Run the Worker**:
   ```bash
   uv run python -m worker.main
   ```

## 🔌 API Endpoints

### Documents

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/documents` | Submit a new document for processing |
| `GET` | `/api/v1/documents` | List documents (filtered by user/status) |
| `GET` | `/api/v1/documents/{id}` | Get document status and summary |
| `PATCH` | `/api/v1/documents/{id}` | Update document metadata |
| `DELETE` | `/api/v1/documents/{id}` | Remove a document record |

### Health Check

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Check API, MongoDB, and Redis health status |

## 🧪 Testing

The project uses `pytest` for integration testing.

```bash
# Run tests using Docker (recommended for consistency)
docker-compose run api pytest

# Run tests locally
uv run pytest
```

## 🛡 Design Decisions

- **Content Hashing**: Documents are hashed using SHA-256. If a document with the same content is submitted again, the system can bypass processing and return a cached summary, saving compute resources.
- **Concurrent Job Limiting**: To prevent a single user from monopolizing the worker pool, a configurable limit on active jobs per user is enforced at the API level.
- **Idempotent Workers**: The worker implementation ensures that multiple attempts to process the same task result in a consistent state, handling potential race conditions during status updates.

## 📈 Future Improvements

- [ ] Implement WebHooks for real-time completion notifications.
- [ ] Add support for multiple worker queues (e.g., priority-based).
- [ ] Integrate an LLM (like OpenAI or Gemini) for real document summarization.
- [ ] Implement user authentication and JWT-based authorization.

