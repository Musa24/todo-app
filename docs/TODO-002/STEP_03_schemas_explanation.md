# Step 3: app/schemas.py — Pydantic Validation Schemas

## What we're about to write

Three Pydantic classes that control what data flows in and out of our API. They are completely separate from SQLAlchemy models — models describe database tables, schemas describe API contracts.

## Why separate models and schemas?

Consider this: your database `Task` has `id`, `created_at`, `updated_at`. But when a client creates a task, they should only send `title` and optionally `description`. They don't get to choose their own `id` or set timestamps. Schemas enforce this boundary — they're a gatekeeper between the outside world and your database.

## Part-by-part breakdown

### 1. `TaskCreate` — What the client sends to create a task

```python
class TaskCreate(BaseModel):
    title: str
    description: str | None = None
```

- Only two fields. The client sends a JSON body like `{"title": "Buy groceries"}` or `{"title": "Buy groceries", "description": "Milk, eggs, bread"}`.
- `title: str` — required. If the client omits it, Pydantic automatically returns a 422 error with a clear message. You don't write any validation code yourself.
- `description: str | None = None` — optional, defaults to `None`. The `str | None` is Python 3.10+ union syntax (same as `Optional[str]`).

### 2. `TaskUpdate` — What the client sends to update a task

```python
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
```

- **Everything is optional.** This enables partial updates — the client can send just `{"completed": true}` without touching the other fields.
- Why `None` as default? In the route handler (TODO-003), we'll check which fields are not `None` and only update those in the database. If a field is `None`, it means "don't change this".

### 3. `TaskResponse` — What the API sends back to the client

```python
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
```

- Includes **all** fields — the client sees the full picture.
- **`model_config = ConfigDict(from_attributes=True)`** — this is the critical line. Here's why:
  - Our data comes from SQLAlchemy model instances. These are objects with attributes: `task.title`, `task.id`, etc.
  - By default, Pydantic expects dictionaries: `task["title"]`, `task["id"]`.
  - `from_attributes=True` tells Pydantic: "read from object attributes instead of dict keys."
  - Without this, returning a SQLAlchemy `Task` object from a route would fail with a validation error.
  - This was called `orm_mode = True` in Pydantic v1. In v2, it's `from_attributes` inside `ConfigDict`.

## How schemas will be used (preview for TODO-003)

```python
# In a future route handler:
@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    ...
```

- `task: TaskCreate` — FastAPI reads the request body, passes it to Pydantic, which validates it against `TaskCreate`. Invalid input never reaches your code.
- `response_model=TaskResponse` — FastAPI takes whatever you return, serializes it through `TaskResponse`, and sends only those fields as JSON. Even if your SQLAlchemy object has extra internal attributes, they won't leak to the client.
