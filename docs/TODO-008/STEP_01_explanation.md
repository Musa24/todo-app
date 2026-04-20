# TODO-008 Step 1: Write the README

## What we're doing

Rewriting the currently empty `README.md` at the project root into a proper project README.

## Why

The project is built, tested, CI is green, and the app is deployed on Render. The README is the front door — anyone visiting the GitHub repo sees it first. Right now it's blank, which makes the project look incomplete.

## What the README will cover

1. **Project title and one-liner** — what this app is in one sentence.
2. **Live demo link** — the Render deployment URL so people can try it immediately.
3. **Tech stack** — FastAPI, SQLAlchemy, SQLite, Uvicorn, Pydantic, uv.
4. **Getting started** — clone, install with `uv sync`, run with `uv run uvicorn ...`, open browser.
5. **API endpoints** — a table listing each route (`POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`) with method, path, and description.
6. **Project structure** — a tree showing the key files/folders and a one-liner for each.
7. **Running tests** — `uv run pytest`.
8. **Deployment** — brief note that the app deploys to Render via `render.yaml`, with CI via GitHub Actions.

## What we will NOT include

- No badges (keep it simple).
- No lengthy paragraphs — concise and scannable.
- No contribution guide or license section (not needed for a learning project).

## Why this structure

It follows the standard open-source README pattern (what, how to run, API, structure, tests, deploy) and keeps things concise per the project conventions.
