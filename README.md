# TodoApp

A task management API built with FastAPI and SQLAlchemy, with a static HTML frontend.

**Live demo:** https://todos-app-i8zm.onrender.com/ (free tier — first request may take ~30s to wake)

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM (SQLite)
- **Pydantic** — request/response validation
- **Uvicorn** — ASGI server
- **uv** — Python package manager
- **GitHub Actions** — CI
- **Render** — deployment

## Getting Started

```bash
git clone https://github.com/Musa24/todo-app.git
cd todo-app
uv sync
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000 in your browser.

## API Endpoints

| Method   | Path              | Description         | Status |
|----------|-------------------|---------------------|--------|
| `POST`   | `/tasks`          | Create a task       | 201    |
| `GET`    | `/tasks`          | List all tasks      | 200    |
| `GET`    | `/tasks/{id}`     | Get a single task   | 200    |
| `PUT`    | `/tasks/{id}`     | Update a task       | 200    |
| `DELETE` | `/tasks/{id}`     | Delete a task       | 204    |

## Project Structure

```
app/
  main.py        # FastAPI app and route handlers
  models.py      # SQLAlchemy ORM models
  schemas.py     # Pydantic request/response schemas
  database.py    # Database engine and session config
static/
  index.html     # Frontend UI
tests/
  test_tasks.py  # API test suite
  conftest.py    # Shared test fixtures
render.yaml      # Render deployment blueprint
```

## Running Tests

```bash
uv run pytest
```

## Deployment

The app deploys to [Render](https://render.com) via the `render.yaml` blueprint. CI runs on every push and PR to `main` through GitHub Actions (`.github/workflows/ci.yml`).

SQLite data is ephemeral on Render's free tier — it resets on each deploy or idle restart.
