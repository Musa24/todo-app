# Step 4: app/main.py — Wiring It Together

## What we're about to write

A small file that creates the FastAPI application and ensures the database tables exist when the app starts. We'll also update `.gitignore` to exclude the generated `todos.db` file.

## Part-by-part breakdown

### 1. Imports

```python
from app.database import Base, engine
```

- We import `Base` (the registry that knows about our `Task` model) and `engine` (the database connection).
- We don't import `Task` directly here, but we **do** need to import `models` — more on that below.

### 2. Importing models to register them

```python
from app import models  # noqa: F401
```

- This import looks like it does nothing — we never use `models` in this file. But it's essential.
- When Python imports `models.py`, the `Task` class definition runs, which calls `class Task(Base)`. That registers `Task` into `Base.metadata`.
- If we skip this import, `Base.metadata` has zero tables registered, and `create_all()` would create nothing.
- `# noqa: F401` tells linters "yes, this import is unused on purpose — don't warn me."

### 3. Creating tables

```python
Base.metadata.create_all(bind=engine)
```

- `Base.metadata` holds the schema of every model that inherited from `Base`.
- `create_all()` generates `CREATE TABLE IF NOT EXISTS` SQL for each registered model and runs it against the engine.
- `IF NOT EXISTS` is key — on first run it creates the table; on subsequent runs it does nothing. Safe to call every time the app starts.
- This runs at module level (not inside a function), so it executes as soon as the app is imported by uvicorn.

### 4. The FastAPI instance

```python
app = FastAPI()
```

- Creates the application. Uvicorn looks for this object when you run `uv run uvicorn app.main:app`.
- No routes yet — that's TODO-003. But even without routes, the app starts and serves the auto-generated docs at `/docs`.

### 5. Updating `.gitignore`

- `todos.db` is generated at runtime when the app first starts. It's local data, not source code.
- Committing it would cause merge conflicts (everyone's local DB would differ) and bloat the repo.
- We add `todos.db` to `.gitignore` so git never tracks it.

## What happens when you run the app after this step

```
$ uv run uvicorn app.main:app --reload

1. Uvicorn imports app.main
2. app.main imports app.database → engine, Base created
3. app.main imports app.models → Task registered in Base.metadata
4. Base.metadata.create_all() runs → todos.db file created with "tasks" table
5. FastAPI app starts → /docs is accessible (no routes yet, just empty docs)
```

This is a good validation checkpoint — if the app starts without errors and `/docs` loads, the entire data layer is working.
