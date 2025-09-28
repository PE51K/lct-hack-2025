# Frontend - AI Data Assistant

This folder contains the frontend code for the AI Data Assistant, a web interface for interacting with the AI-powered data engineering automation system.

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Linting and Formatting](#linting-and-formatting)
- [Dependency Management](#dependency-management)

## Technology Stack

- **React** - UI library for building user interfaces
- **TypeScript** - Typed JavaScript for better development experience
- **Vite** - Fast build tool and development server
- **ESLint** - Linting for code quality
- **Docker & Docker Compose** - Containerization and orchestration

## Project Structure

```
frontend/
├── public/                      # Static assets served directly
│   └── vite.svg                # Vite logo
├── src/                         # Source code
│   ├── assets/                  # Static assets imported in code
│   │   └── react.svg            # React logo
│   ├── components/              # React components
│   │   ├── CreationReport.tsx   # ETL creation report component
│   │   ├── DeploymentProgress.tsx # Deployment progress component
│   │   ├── DeploymentReport.tsx # Deployment report component
│   │   ├── FeedbackForm.tsx     # User feedback form component
│   │   ├── InputForm.tsx        # Input form for ETL generation
│   │   └── ProgressBar.tsx      # Progress indicator component
│   ├── services/                # API service functions
│   │   └── api.ts               # API client and type definitions
│   ├── App.css                 # Main application styles
│   ├── App.tsx                 # Main application component
│   ├── index.css               # Global styles
│   ├── main.tsx                # Application entry point
│   └── vite-env.d.ts           # Vite environment types
├── docker-compose.yaml          # Docker Compose configuration
├── dockerfile                   # Dockerfile for frontend container
├── eslint.config.js             # ESLint configuration
├── index.html                   # HTML template
├── package.json                 # Node.js project configuration
├── package-lock.json            # Dependency lock file
├── README.md                    # This file
├── tsconfig.app.json            # TypeScript config for app
├── tsconfig.json                # Main TypeScript configuration
├── tsconfig.node.json           # TypeScript config for Node.js
└── vite.config.ts               # Vite configuration
```

## Development Setup

1. Navigate to the `frontend` directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy `.env.dev.example` to `.env` and update the environment variables as needed:
```bash
cp .env.dev.example .env
# Edit .env to set your configurations
```

4. Start the development server:
```bash
npm run dev
```

5. Open your browser and navigate to `http://localhost:5173` (or the port specified in the output).

## Linting and Formatting

The project uses ESLint for linting. The configuration is defined in the `eslint.config.js` file.

To run the linter:
```bash
npm run lint
```

## Dependency Management

Dependencies are managed via npm and defined in the `package.json` file.

To add a new dependency:
```bash
npm install <package-name>
```

To add a development dependency:
```bash
npm install <package-name> --save-dev
```

To remove a dependency:
```bash
npm uninstall <package-name>
