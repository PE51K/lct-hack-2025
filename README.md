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
AITHachathon/
├── backend/                   # Python backend application
├── frontend/                  # Frontend application
├── docker-compose.yaml        # Main orchestration file
└── README.md                  # This file
```

## 🏗️ Proposed Solution and Architecture

```mermaid
flowchart TD
    %% GUI Input
    GUI1[GUI: Data URI connection string\n+ button] -->|URI + thread/user ids| API1[FastAPI: Generate AI ETL request]

    %% Extract phase
    API1 --> CALL1[Callable: Input Data Analyzer Pipe]
    CALL1 --> DETECT[Detect source type and metadata]
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
[`frontend/`](frontend/) - UI for all our mad stuff. Stakeholders: Daniil.

#### FastAPI app
[`backend/app/app.py`](backend/app/app.py) - would handle ETL generation/update/publish requests. Stakeholders: Gregory.

#### AI pipelines
[`backend/ai/`](backend/ai/) - would contain the AI-related logic and processing. **Attention**: committed usage of simple LangChain pipelines without memory for now with Dima - we may need to exclude checkpointer setup in [`backend/app/app.py`](backend/app/app.py) for now. Stakeholders: Gregory and Dima.

#### ExtractConfig model
[`backend/models/extract.py`](backend/models/extract.py) - describes source data storage, metamodels for objects in the storage, and some additional metadata. Stakeholders: Anton.

#### TransformConfig model
[`backend/models/transform.py`](backend/models/transform.py) - describes transformation instructions, aggregation rules, load periodicity, and some additional metadata. Stakeholders: Nikita.

#### LoadConfig model
[`backend/models/load.py`](backend/models/load.py) - describes target data storage, data structure in the storage, indexes, and some additional metadata. Stakeholders: Anton and Nikita.

#### ExtractConfig builders
[`backend/builders/extract/`](backend/builders/extract/) - would contain builders for various data sources to build ExtractConfig. Each builder is inherited from [`BaseExtractConfigBuilder`](backend/builders/extract/__init__.py) and should implement 3 methods for getting data shard type, metamodel for each data shard, and optional method for getting any additional useful metadata. **Attention**: some builders like `backend/builders/extract/hadoop.py`, `.../sparkstreaming.py` would not be implemented during hackathon. Stakeholders: Anton, Gregory, Nikita, Daniil, Julia.

#### DDL generation
[`backend/builders/ddl.py`](backend/builders/ddl.py) - would generate DDL based on ExtractConfig and LoadConfig. Stakeholders: Anton.

#### DAG generation
[`backend/builders/dag.py`](backend/builders/dag.py) - would generate Airflow DAG based on ExtractConfig, TransformConfig, LoadConfig, and DDL. Stakeholders: Nikita.

#### DAG execution
[`backend/executors/dag.py`](backend/executors/dag.py) - would handle the execution of the generated DAGs. **Attention**: probably, would include `DAG generation` part as well. Stakeholders: Nikita.

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
# Backend configuration (use .env.prod.example for production)
cp backend/.env.prod.example backend/.env
# Edit backend/.env with your settings

# Frontend configuration (use .env.prod.example for production)
cp frontend/.env.prod.example frontend/.env
# Edit frontend/.env with your settings
```

- Refer to the [`backend/.env.dev.example`](backend/.env.dev.example) and [`frontend/.env.dev.example`](frontend/.env.dev.example) files for variable descriptions.

3. **Start all services:**
```bash
docker compose up --build -d
```

4. **Access the services:**
- Frontend: `http://localhost:{port_from_frontend_env}`
- Backend API: `http://localhost:{port_from_backend_env}/docs`

## 🛠️ Development Setup

Refer to [Backend Documentation](backend/README.md) and [Frontend Documentation](frontend/README.md) for detailed development instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Format backend code: `cd backend && uv run ruff format && uv run ruff check --fix`
5. Format frontend code: `cd frontend && npm run lint`
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
