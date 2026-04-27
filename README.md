# Async Document Operations API

A production-ready asynchronous API for document processing and insights, built with FastAPI, MongoDB, Redis, and Celery.

## 🚀 Design Decisions

### 1. Asynchronous Task Architecture
The core requirement was to handle potentially long-running document processing without blocking the API. I chose **FastAPI** for its high performance and native async support, paired with **Celery** for background tasks. **Redis** serves as the message broker, ensuring reliable communication between the API and the workers.

### 2. Service-Repository Pattern
The codebase follows a structured approach to decouple concerns:
- **API Layer**: Handles HTTP requests, validation, and documentation.
- **Service Layer**: Contains business logic, coordinates between repositories and background tasks.
- **Repository Layer**: Abstracts MongoDB operations, making it easier to swap the database or mock it for testing.

### 3. Database & Caching Strategy
- **MongoDB**: Chosen for its flexible schema, which is ideal for storing varied document metadata and analysis results.
- **Redis**: Used for three critical roles:
  - Task broker for Celery.
  - Caching layer for frequently accessed document insights to reduce DB load.
  - Potential for rate limiting and session management.

### 4. Modern Python Tooling
- **uv**: Used for dependency management to ensure fast, reproducible builds.
- **Pydantic v2**: Leveraged for robust data validation and automatic OpenAPI schema generation.

## 🧠 Assumptions

- **Processing Overhead**: Assumed that document "processing" involves CPU-bound or external I/O tasks that justify an out-of-process worker rather than simple async tasks.
- **Data Persistence**: Assumed that document metadata must persist indefinitely, while insights can be recalculated if cached data expires.
- **Environment**: Assumed a Docker-based deployment strategy for consistency across development and production.

## 🛠️ What I Would Do Differently with More Time

1. **Enhanced Observability**:
   - Integrate **Flower** for real-time Celery monitoring.
   - Implement **Prometheus/Grafana** for API metrics.
   - Add structured logging with correlation IDs across services.

2. **Robust Security**:
   - Implement **OAuth2 with JWT** for authentication.
   - Add **RBAC (Role-Based Access Control)** for document access.
   - Secure the Redis and MongoDB instances with authentication and TLS.

3. **Infrastructure & Scaling**:
   - Implement a **Dead Letter Queue (DLQ)** for failed tasks that exceed retry limits.
   - Add **Autoscaling** for Celery workers based on queue length.
   - Use **MinIO or S3** for actual document file storage, keeping only metadata in MongoDB.

4. **Testing Depth**:
   - Increase integration test coverage for edge cases (e.g., Redis/DB connection drops).
   - Add **Load Testing** with Locust to identify bottlenecks in the task queue.

## 🏃 Getting Started

### Prerequisites
- Docker and Docker Compose
- `uv` (optional, for local development)

### Start the application
```bash
docker compose up -d
```

The API will be available at `http://localhost:8000` and the Swagger UI at `http://localhost:8000/docs`.
