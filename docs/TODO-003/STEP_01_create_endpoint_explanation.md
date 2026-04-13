# Step 1: POST /tasks — Create a Task

## What we're about to write

A single route handler in `app/main.py` that accepts a JSON body, validates it, saves it to the database, and returns the created task with a 201 status code.

## Part-by-part breakdown

### 1. New imports in main.py

```python
from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session
```

- `Depends` — FastAPI's dependency injection function. We use it to automatically get a database session for each request.
- `status` — a module containing HTTP status code constants like `status.HTTP_201_CREATED`. Using named constants is clearer than magic numbers like `201`.
- `Session` — the type hint for our database session parameter.

### 2. The route decorator

```python
@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
```

- `@app.post("/tasks")` — registers this function to handle POST requests to `/tasks`.
- `response_model=TaskResponse` — tells FastAPI: "take whatever I return and serialize it through `TaskResponse`." This does two things:
  1. Strips any fields not in `TaskResponse` (security — don't leak internal data)
  2. Generates the response schema in the `/docs` page automatically
- `status_code=status.HTTP_201_CREATED` — the default success status is 200. For resource creation, the HTTP standard says to use 201. This sets it globally for this route.

### 3. The function signature

```python
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
```

- `task: TaskCreate` — FastAPI sees a Pydantic model as a parameter and automatically reads the request body, parses JSON, and validates it against `TaskCreate`. If the body is invalid (e.g. missing `title`), FastAPI returns a 422 error before your code even runs.
- `db: Session = Depends(get_db)` — this is where dependency injection happens:
  1. FastAPI sees `Depends(get_db)`
  2. It calls `get_db()`, which opens a database session
  3. The session is passed as the `db` parameter
  4. After the response is sent, the `finally` block in `get_db()` closes the session
  - You never manually open or close sessions in route handlers.

### 4. The function body

```python
db_task = Task(title=task.title, description=task.description)
db.add(db_task)
db.commit()
db.refresh(db_task)
return db_task
```

Step by step:

1. **`Task(title=task.title, description=task.description)`** — creates a SQLAlchemy model instance. We unpack the Pydantic schema fields into the model constructor. Fields like `id`, `completed`, `created_at`, `updated_at` are handled by their defaults — we don't set them.

2. **`db.add(db_task)`** — stages the new task in the session. Nothing is written to the database yet — it's like `git add` before `git commit`.

3. **`db.commit()`** — writes all staged changes to the database. This is where the INSERT SQL runs. After this, the task exists in `todos.db`.

4. **`db.refresh(db_task)`** — re-reads the task from the database into our Python object. Why? Because the database generated values we don't have yet: `id` (auto-increment), `created_at`, `updated_at` (server defaults). Without refresh, `db_task.id` would be `None`.

5. **`return db_task`** — returns the SQLAlchemy object. FastAPI takes it, runs it through `TaskResponse` (which works because we set `from_attributes=True`), and sends JSON back to the client.

## The full request lifecycle

```
Client sends: POST /tasks  {"title": "Buy groceries", "description": "Milk and eggs"}
    |
    v
FastAPI validates body against TaskCreate
    |  (if invalid -> 422 error, your code never runs)
    v
FastAPI calls get_db() -> opens session
    |
    v
create_task() runs:
    Task() -> db.add() -> db.commit() -> db.refresh()
    |
    v
FastAPI serializes return value through TaskResponse
    |
    v
Client receives: 201  {"id": 1, "title": "Buy groceries", "description": "Milk and eggs", "completed": false, "created_at": "...", "updated_at": "..."}
    |
    v
get_db() finally block closes the session
```
