# Backend - AI Data Assistant

This folder contains the backend code for the AI Data Assistant

## Table of Contents

- [Backend - AI Data Assistant](#backend---ai-data-assistant)
  - [Table of Contents](#table-of-contents)
  - [Technology Stack](#technology-stack)
  - [Project structure](#project-structure)
  - [Development Setup](#development-setup)
  - [Linting and formatting](#linting-and-formatting)
  - [Dependency management](#dependency-management)
- [Requests for basic scenarios](#requests-for-basic-scenarios)
  - [get\_meta](#get_meta)

## Technology Stack

- **python3.12** - Core programming language
- **UV** - Dependency management
- **Ruff** - Linting and formatting
- **FastAPI** - Web API building
- **pydantic-settings** - Configuration management
- **LangChain** - LLM orchestration and agent framework
- **LangGraph** - Agentic workflow management
- **LangFuse** - Observability and tracing for LLM applications
- **YandexGPT** - Foundation models for text generation and embeddings
- **PostgreSQL** - Relational database for structured data
- **Docker & Docker Compose** - Containerization and orchestration

## Project structure

```plaintext
backend/
├── ai/                          # AI-related modules
│   ├── agents/                  # AI agents for specific tasks
│   │   ├── calculcator_agent.py # Calculator agent for computations
│   │   └── __init__.py
│   ├── __init__.py
│   └── llm/                     # Large Language Model integrations
│       └── __init__.py
├── app/                         # Application entry point
│   └── app.py                   # FastAPI application
├── core/                        # Core utilities and configurations
│   ├── __init__.py
│   ├── logging.py               # Logging configuration
│   └── settings.py              # Application settings and configuration
├── docker-compose.langfuse.yaml # Docker Compose for LangFuse
├── docker-compose.yaml          # Main Docker Compose configuration
├── dockerfile                   # Dockerfile for backend container
├── init-multiple-databases.sh   # Script to initialize databases
├── pyproject.toml               # Python project configuration
├── README.md                    # This file
└── uv.lock                      # Dependency lock file
```

## Development Setup

1. Navigate to the `backend` directory:
```bash
cd backend
```

2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) if you haven't done so already:
```bash
pip install uv
```

3. Sync dependencies:
```bash
uv sync
```

4. Copy `.env.dev.example` to `.env` and update the environment variables as needed:
```bash
cp .env.dev.example .env
# Edit .env to set your configurations
```

6. **Start supporting services (Postgres, LangFuse) from the project root directory**:
```bash
# Run from the project root directory
docker compose up -d postgres langfuse-web
```

7. Run local fastapi server:
```bash
uv run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

## Linting and formatting

The project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting. The configuration is defined in the `pyproject.toml` file. To ensure consistent code style, please run the linter before committing changes.

1. To run linter:
```bash
uv run ruff check
```

2. To format code:
```bash
uv run ruff format
```

## Dependency management

The project uses [uv](https://docs.astral.sh/uv/) for dependency management. Dependencies are defined in the `pyproject.toml` file. To manage dependencies, use the following commands:

1. To install all dependencies:
```bash
uv sync
```

2. To add a new dependency:
```bash
uv add <package-name>
```

3. To add a development dependency (wont be included in production build):
```bash
uv add <package-name> --dev
```

4. To remove a dependency:
```bash
uv remove <package-name>
```


# Requests for basic scenarios

## get_meta

curl "http://localhost:8000/get_meta?user_input=file:D:\MyProject\ict-hack-2025-doc\syn_csv"

curl "http://localhost:8000/get_meta?user_input=postgresql://user:password@localhost:5432/mydatabase"

curl "http://localhost:8000/get_meta?user_input=clickhouse://user:password@localhost:9000/mydatabase"

curl "http://localhost:8000/get_meta?user_input=kafka://broker1:9092,broker2:9092/my-topic?group.id=my-consumer-group"

curl "http://localhost:8000/get_meta?user_input=hdfs://namenode:8020/user/data"

curl "http://localhost:8000/get_meta?user_input=sparkstreaming"