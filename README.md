# 🎯 ...

....

## 📜 Table of Contents

- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Development Setup](#-development-setup)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)

## 🏗️ Architecture

```
...
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
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Frontend configuration
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your settings
```

- Refer to the [`backend/.env.example`](backend/.env.example) and [`frontend/.env.example`](frontend/.env.example) files for variable descriptions.

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
3. Make your changes and add tests
4. Run linting: `cd backend && uv run ruff check`
5. Format code: `uv run ruff format`
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
