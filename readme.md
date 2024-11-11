# Autonomous Code Review Agent System

This project implements an autonomous code review agent using FastAPI, Celery, Redis, and Ollama. The system analyzes GitHub pull requests asynchronously and provides structured feedback to developers via an API. It uses an AI agent to analyze code quality, style, bugs, and performance.

## Project Setup Instructions

### Requirements:
- Docker
- Docker Compose (if you're using Docker Compose)
- Python 3.8+
- Redis
- Ollama (for local LLM inference)

### Steps to Run the Project:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/code-review-agent.git
    cd code-review-agent
    ```

2. **Build and run the Docker containers**:

    If you are using Docker Compose, run the following command:
    ```bash
    docker-compose up --build
    ```

    If you're using a standalone Docker setup, build and run the containers manually:
    ```bash
    docker build -t code-review-agent .
    docker run -p 8000:8000 -p 6379:6379 code-review-agent
    ```

3. **Check if everything is working**:
    Open your browser and visit:
    ```bash
    http://localhost:8000
    ```

    You should see the FastAPI interactive docs (Swagger UI) at `http://localhost:8000/docs`.

### Environment Configuration:

The project uses environment variables to configure the FastAPI server, Celery workers, and Ollama API. You can configure these settings in the `.env` file located in the root of the project.

Example `.env` file:
```bash
OLLAMA_API_URL=http://host.docker.internal:5000
REDIS_URL=redis://redis:6379/0
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_WORKER_CONCURRENCY=1
CELERY_WORKER_PREFETCH=1


Design Decisions
FastAPI for API Server: FastAPI is used to quickly develop and serve the REST API. It provides automatic Swagger UI documentation, making it easy for developers to interact with the API.

Celery for Asynchronous Task Management: Celery is used to manage the background tasks (i.e., code review analysis). Redis is used as the message broker and result backend for Celery.

Ollama for LLM Inference: Ollama is used for local LLM inference to analyze code. The model is hosted locally and the system communicates with it through HTTP requests.

Redis for Caching and Task Management: Redis serves as the message broker for Celery and can also be used for caching the results of repeated requests.

Scalable Architecture: The system is designed to handle multiple code review tasks concurrently by scaling the Celery worker processes. The architecture allows easy horizontal scaling.

Future Improvements:
Add support for additional programming languages.
Implement GitHub Webhooks to automatically trigger analysis on PR events.
Add more advanced code analysis features like security vulnerability detection.
Implement caching for frequently requested results.
