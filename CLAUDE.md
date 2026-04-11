# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TodoApp — a FastAPI-based todo/task management application with SQLAlchemy ORM, served with Uvicorn. Frontend is static HTML in `static/`.

## Commands

- **Run server:** `uv run uvicorn app.main:app --reload`
- **Run all tests:** `uv run pytest`
- **Run single test:** `uv run pytest tests/test_tasks.py::test_name -v`
- **Add dependency:** `uv add <package>`
- **Lock dependencies:** `uv lock`

## Architecture

- `app/main.py` — FastAPI app entry point and route handlers
- `app/models.py` — SQLAlchemy ORM models
- `app/schemas.py` — Pydantic request/response schemas
- `app/database.py` — Database engine, session, and base configuration
- `tests/` — pytest test suite (uses httpx for API testing)
- `static/` — Frontend HTML/CSS/JS

## Ticket Workflow (Explain-then-Code)

This is a learning project. When implementing Jira tickets, work incrementally one chunk at a time:

1. **Announce** what will be done (file, purpose, why now)
2. **Wait** for explicit approval
3. **Write explanation first** — create a markdown file in `docs/<TICKET>/` (e.g. `STEP_01_explanation.md`) that explains the intuition, what the code will do, and why
4. **Wait** for approval of the explanation
5. **Only then** write the code for that chunk
6. **Pause** and describe the next step, then repeat

Never combine steps. Never write code before the explanation is approved. Explanation docs live in `docs/<TICKET>/`.

## Conventions

- Python 3.13+, managed with `uv` (no pip, no requirements.txt)
- Always use `uv run` to execute scripts (never bare `python3`)
- Type hints on all function signatures
- Pydantic models for all API input/output validation
- Keep route handlers thin — business logic in service modules
- Use `logging` module, never `print()` in committed code
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Jira ticket references in branch names (`feature/TODO-XXX-description`) and commit messages
