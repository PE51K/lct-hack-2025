# Backend - ...

This folder contains the backend code for the ...

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project structure](#project-structure)
- [Development Setup](#development-setup)
- [Linting and formatting](#linting-and-formatting)
- [Dependency management](#dependency-management)

## Technology Stack

- **python3.12** - Core programming language
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
├── ai
│   ├── agents
│   │   ├── calculcator_agent.py
│   │   └── __init__.py
│   ├── __init__.py
│   └── llm
│       └── __init__.py
├── app
│   └── app.py
├── core
│   ├── __init__.py
│   ├── logging.py
│   └── settings.py
├── docker-compose.langfuse.yaml
├── docker-compose.yaml
├── dockerfile
├── init-multiple-databases.sh
├── pyproject.toml
├── README.md
└── uv.lock
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

4. Copy `.env.example` to `.env` and update the environment variables as needed:
```bash
cp .env.example .env
# Edit .env to set your configurations
```

6. **Start supporting services (Postgres, LangFuse)**:
```bash
# Run from the project root directory
docker compose up -d postgres langfuse-web
```

7. Run fastapi server:
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
