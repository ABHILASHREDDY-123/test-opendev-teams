# test-opendev-teams

A **mono-repo** for testing the openDevTeams multi-agent development platform.

## Repository Structure

```
├── backend/         # Python/FastAPI backend services
│   ├── auth.py      # JWT authentication (login, register)
│   ├── main.py      # Application entry point
│   └── ...
├── frontend/        # React/TypeScript frontend application
│   ├── src/
│   │   ├── pages/   # Page components (Login, Profile, etc.)
│   │   ├── App.tsx
│   │   └── ...
│   └── package.json
├── requirements.txt # Python dependencies
└── README.md
```

## Purpose

This repository is used by AI agents (managed by openDevTeams) to:

1. **Implement features** — Agents clone this repo, create feature branches, write code, and push
2. **Collaborate across teams** — Backend and Frontend teams work in the same repo on shared features
3. **Test CI/CD workflows** — Validate the agent-driven development pipeline

## How Agents Work With This Repo

- **Clone**: `git clone <repo_url>` (credentials injected by the platform)
- **Branch**: `git checkout -b feature/<feature-name>`
- **Code**: Write implementation files in `backend/` or `frontend/`
- **Push**: `git commit -am "message" && git push origin feature/<feature-name>`
- **PR**: Create pull requests via the GitHub API

## Teams

| Team | Scope | Folder |
|------|-------|--------|
| Backend | Python/FastAPI APIs, auth, database | `backend/` |
| Frontend | React/TypeScript UI, pages, components | `frontend/` |

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, JWT (python-jose), bcrypt
- **Frontend**: React 18+, TypeScript, Vite
