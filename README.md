# 🎯 AI Data Assistant

A comprehensive AI-powered assistant for automating data engineering processes, capable of connecting to various data sources, building ETL pipelines, designing data warehouses, and optimizing processing performance.

## 📜 Table of Contents

- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Development Setup](#-development-setup)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)

## 📁 Project Structure

```
lct-hack-2025/
├── backend/                   # Python backend application (FastAPI)
├── frontend/                  # React frontend application
├── test_dbs/                  # Test databases setup (PostgreSQL, ClickHouse, MinIO)
├── docker-compose.yaml        # Main orchestration file
└── README.md                  # This file
```

## 🏗️ Proposed Solution and Architecture

```mermaid
flowchart TD
    %% GUI Input
    GUI1[GUI: Data URI connection string\n+ button] -->|URI + thread/user ids| API1[FastAPI: Generate AI ETL request]

    %% Source Generation
    API1 --> SOURCEGEN[Generate Source from User prompt]
    SOURCEGEN --> DETECT[Detect source type and metadata]

    %% Extract phase
    DETECT --> SRC1[files S3]
    DETECT --> SRC2[Postgres]
    DETECT --> SRC3[Clickhouse]
    DETECT --> SRC4[Kafka]
    DETECT --> SRC5[XML]
    DETECT --> SRC6[JSON]
    DETECT --> SRC7[CSV]
    SRC1 & SRC2 & SRC3 & SRC4 & SRC5 & SRC6 & SRC7 --> PARSE[Parse data → Extract cfg]

    %% AI Storage Recommendation
    PARSE --> AI1[AI: Generate storage recommendations]
    AI1 --> STYPE[Choose storage type]
    STYPE --> STORE1[Clickhouse]
    STYPE --> STORE2[HDFS]
    STYPE --> STORE3[Postgres]
    STYPE --> DSTRUCT[Choose data structure in storage]
    STYPE --> INDEX[Choose indexes]
    DSTRUCT & INDEX --> LOADCFG[Load cfg]

    %% DDL Generation
    LOADCFG --> CALL2[Callable: Generate DDL]
    CALL2 --> DDL[DDL]

    %% AI Transformation
    DDL --> AI2[AI: Generate transformation recommendations]
    AI2 --> RULES[Select aggregation rules]
    AI2 --> INSTR[Generate transformation instructions]
    AI2 --> PERIOD[Select load periodicity]
    RULES & INSTR & PERIOD --> TRANSFORMCFG[Transform cfg]

    %% DAG Generation
    TRANSFORMCFG --> CALL3[Callable: Generate DAG]
    CALL3 --> READCFG[Read configs]
    READCFG --> GENSTORE[Generate storage]
    GENSTORE --> VERIFY1[Verify storage]
    VERIFY1 --> GENDAG[Generate DAG]
    GENDAG --> VERIFY2[Verify DAG]
    VERIFY2 --> DAG[DAG]

    %% Deployment
    DAG --> API2[FastAPI: Generate AI ETL response\nstreaming steps]
    API2 --> DECISION1{Ready and successful?}
    DECISION1 -- No --> GUI2[GUI: Progress bar]
    DECISION1 -- Yes --> GUI3[GUI: Creation report]

    %% Feedback Loop
    GUI3 --> DECISION2{Satisfied?}
    DECISION2 -- No --> GUI4[GUI: What is wrong?\nUser feedback]
    GUI4 --> API3[FastAPI: Update AI ETL based on feedback]
    DECISION2 -- Yes --> API4[FastAPI: Publish ETL request]

    %% Publisher
    API4 --> CALL4[Callable: Publisher]
    CALL4 --> PUBLISH1[Send Airflow command to create storage]
    PUBLISH1 --> PUBLISH2[Send ETL DAG to Airflow]
    PUBLISH2 --> REPORT[Publisher report]
    REPORT --> API5[FastAPI: Publish ETL response]

    %% Deployment Report
    API5 --> DECISION3{Ready and successful?}
    DECISION3 -- No --> GUI5[GUI: Progress bar]
    DECISION3 -- Yes --> GUI6[GUI: Deployment report]
```

For a detailed representation, refer to the [Miro board](https://miro.com/app/board/uXjVJF7uF_o=/).

### Where All This Stuff Is Implemented or Proposed to Be Implemented

#### UI
[`frontend/`](frontend/) - React-based web interface for ETL pipeline creation and management. Stakeholders: Daniil.

#### FastAPI Backend
[`backend/app/app.py`](backend/app/app.py) - Main FastAPI application handling ETL generation, update, and publish requests via streaming endpoints.

#### API Endpoints
- [`backend/app/routers/create_etl.py`](backend/app/routers/create_etl.py) - `/create_etl` - Generates ETL configurations from user prompts
- [`backend/app/routers/create_dag.py`](backend/app/routers/create_dag.py) - `/create_dag` - Creates Airflow DAG files after credentials are provided
- [`backend/app/routers/publish_etl.py`](backend/app/routers/publish_etl.py) - `/publish_etl` - Publishes DAGs to Airflow for execution
- [`backend/app/routers/update_etl.py`](backend/app/routers/update_etl.py) - `/update_etl` - Updates ETL configurations based on user feedback

#### AI Components
[`backend/ai/`](backend/ai/) - Contains AI-related logic using LangChain and YandexGPT for ETL generation and optimization.

#### Data Models
- [`backend/models/extract.py`](backend/models/extract.py) - ExtractConfig model for source data specifications
- [`backend/models/transform.py`](backend/models/transform.py) - TransformConfig model for data transformation rules
- [`backend/models/load.py`](backend/models/load.py) - LoadConfig model for target storage specifications
- [`backend/models/ddl.py`](backend/models/ddl.py) - DDL model for database schema definitions
- [`backend/models/dag.py`](backend/models/dag.py) - DAG model for Airflow pipeline definitions

#### Builders
- [`backend/builders/extract/`](backend/builders/extract/) - ExtractConfig builders for various data sources (PostgreSQL, ClickHouse, S3, Kafka, folder)
- [`backend/builders/load/`](backend/builders/load/) - LoadConfig builders with AI recommendations for target storage
- [`backend/builders/transform/`](backend/builders/transform/) - TransformConfig builders with AI-generated transformation logic
- [`backend/builders/ddl/`](backend/builders/ddl/) - DDL generators for target schema creation
- [`backend/builders/dag/`](backend/builders/dag/) - Airflow DAG file generators with templates

#### Test Infrastructure
[`test_dbs/`](test_dbs/) - Test database setup with PostgreSQL, ClickHouse, and MinIO for development and testing.

## 🚀 Deployment

### Prerequisites

- **Docker & Docker Compose**: For containerized deployment
- **Yandex Cloud Account**: For AI services
- **Git**: For cloning the repository

### Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/PE51K/lct-hack-2025
cd lct-hack-2025
```

2. **Set up environment variables:**
```bash
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env with your Yandex Cloud credentials and other settings

# Frontend configuration
cp frontend/.env.example frontend/.env
# Edit frontend/.env to set the backend API URL

# Test databases configuration
cp test_dbs/.env.example test_dbs/.env
# Edit test_dbs/.env if you need to change default database settings
```

- Refer to the `.env.example` files in each directory for variable descriptions.

3. **Start all services:**
```bash
docker compose up --build -d
```

4. **Access the services:**
- Frontend: `http://localhost:7777`
- Backend API: `http://localhost:8000/docs`
- Airflow UI: `http://localhost:8081` (admin/admin)

## 🛠️ Development Setup

### Prerequisites

- **Python 3.12+** - For backend development
- **Node.js 18+** - For frontend development
- **Docker & Docker Compose** - For running databases and services
- **Yandex Cloud Account** - For AI services (optional for basic development)

### Quick Start

1. **Start test databases:**
```bash
docker compose up -d test-postgres test-clickhouse test-minio
```

2. **Backend development:**
```bash
cd backend
cp .env.example .env
# Edit .env with your settings (Yandex GPT credentials optional for basic testing)
uv sync
uv run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend development:**
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

For detailed development instructions, refer to [Backend Documentation](backend/README.md) and [Frontend Documentation](frontend/README.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Format and lint code:
   - Backend: `cd backend && uv run ruff format && uv run ruff check --fix`
   - Frontend: `cd frontend && npm run lint`
5. Build and verify:
   - Frontend: `cd frontend && npm run build`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature/your-feature`
8. Submit a pull request

## 🙏 Acknowledgments

- **Yandex Cloud** for AI foundation models and embeddings
- **LangChain** for LLM orchestration framework
- **LangGraph** for agent workflow orchestration
- **LangFuse** for AI observability platform

---

**Happy Hacking! 🚀**
