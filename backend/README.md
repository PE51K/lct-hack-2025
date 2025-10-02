# Backend - AI Data Assistant

This folder contains the backend code for the AI Data Assistant

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project structure](#project-structure)
- [Development Setup](#development-setup)
- [Linting and formatting](#linting-and-formatting)
- [Dependency management](#dependency-management)

## Technology Stack

- **python3.12** - Core programming language
- **UV** - Dependency management
- **Ruff** - Linting and formatting
- **FastAPI** - Web API building
- **pydantic-settings** - Configuration management
- **LangChain** - LLM orchestration and agent framework
- **LangGraph** - Agentic workflow management
- **YandexGPT** - Foundation models for text generation and embeddings
- **PostgreSQL** - Relational database for structured data
- **Docker & Docker Compose** - Containerization and orchestration

## Project structure

```plaintext
backend/
├── ai/                          # AI-related modules
│   ├── __init__.py
│   └── llm/                     # Large Language Model integrations
│       └── __init__.py
├── app/                         # FastAPI application
│   ├── app.py                   # Main FastAPI application
│   └── routers/                 # API route handlers
│       ├── create_dag.py        # DAG creation endpoints
│       ├── create_etl.py        # ETL creation endpoints
│       ├── publish_etl.py       # ETL publishing endpoints
│       ├── update_etl.py        # ETL update endpoints
│       └── __init__.py
├── builders/                    # ETL configuration builders
│   ├── dag/                     # DAG file generation
│   │   ├── builder.py
│   │   ├── file_generator.py
│   │   └── templates/           # Jinja2 templates for DAG generation
│   ├── ddl/                     # DDL statement generation
│   │   ├── builder.py
│   │   └── __init__.py
│   ├── extract/                 # ExtractConfig builders for various sources
│   │   ├── base.py              # Base extract builder
│   │   ├── clickhouse.py        # ClickHouse ExtractConfig builder
│   │   ├── folder.py            # Folder ExtractConfig builder
│   │   ├── kafka.py             # Kafka ExtractConfig builder
│   │   ├── postgres.py          # PostgreSQL ExtractConfig builder
│   │   ├── s3.py                # S3 ExtractConfig builder
│   │   └── __init__.py
│   ├── load/                    # LoadConfig builders
│   │   ├── builder.py
│   │   └── __init__.py
│   ├── transform/               # TransformConfig builders
│   │   ├── builder.py
│   │   └── __init__.py
│   └── __init__.py
├── core/                        # Core utilities and configurations
│   ├── __init__.py
│   ├── logging.py               # Logging configuration
│   └── settings.py              # Application settings and configuration
├── dags/                        # Generated Airflow DAGs directory
│   └── .gitignore
├── docker-compose.airflow.yaml   # Docker Compose for Airflow
├── docker-compose.yaml          # Main Docker Compose configuration
├── dockerfile                   # Dockerfile for backend container
├── init-multiple-databases.sh   # Script to initialize databases
├── models/                      # Pydantic data models and schemas
│   ├── app/                     # Application-specific models
│   ├── dag.py                   # DAG data models
│   ├── ddl.py                   # DDL data models
│   ├── extract.py               # Extract data models
│   ├── load.py                  # Load data models
│   ├── transform.py             # Transform data models
│   └── __init__.py
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

4. Copy `.env.example` to `.env` and update the environment variables as needed:
```bash
cp .env.example .env
# Edit .env to set your configurations (especially Yandex GPT credentials)
```

6. **Start supporting services from the project root directory**:
```bash
# Run from the project root directory
docker compose up -d test-postgres test-clickhouse test-minio
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

