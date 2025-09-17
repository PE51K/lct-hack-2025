# 🎯 AI Data Assistant

A comprehensive AI-powered assistant for automating data engineering processes, capable of connecting to various data sources, building ETL pipelines, designing data warehouses, and optimizing processing performance.

## 📜 Table of Contents

- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Development Setup](#-development-setup)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Agents     │
│   (React + TS)  │◄──►│   (FastAPI)     │◄──►│   (LangChain)   │
│                 │    │                 │    │                 │
│ - User Interface│    │ - API Endpoints │    │ - Data Sources  │
│ - Chat Interface│    │ - Orchestration │    │ - ETL Pipelines │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Data Stores   │
                    │   (PostgreSQL)  │
                    └─────────────────┘
```

## 📁 Project Structure

```
AITHachathon/
├── backend/                   # Python backend application
├── frontend/                  # Frontend application
├── docker-compose.yaml        # Main orchestration file
└── README.md                  # This file
```

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
