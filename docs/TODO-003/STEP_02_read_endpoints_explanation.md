# Step 2: GET /tasks + GET /tasks/{task_id} — Read Endpoints

## What we're about to write

Two route handlers: one that returns all tasks, and one that returns a single task by ID (or a 404 error if it doesn't exist).

## Part-by-part breakdown

### 1. New import

```python
from fastapi import HTTPException
```

- `HTTPException` is how you return error responses in FastAPI. You `raise` it (not `return` it), and FastAPI catches it and converts it to a JSON error response. We need it for the 404 case.

### 2. GET /tasks — List all tasks

```python
@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()
```

- `@app.get("/tasks")` — handles GET requests to `/tasks`.
- `response_model=list[TaskResponse]` — the response is a JSON array. Each element is serialized through `TaskResponse`. The `list[...]` syntax tells FastAPI to expect a list.
- `db.query(Task)` — creates a SQL query targeting the `tasks` table. Think of it as `SELECT * FROM tasks`. It doesn't execute yet — it's a query builder.
- `.all()` — executes the query and returns all results as a Python list of `Task` objects.
- That's it. No pagination, no filtering — the simplest possible list endpoint. We return the list and FastAPI serializes each item.

### 3. GET /tasks/{task_id} — Get single task

```python
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

#### Path parameters

- `"/tasks/{task_id}"` — the curly braces define a **path parameter**. A request to `/tasks/5` sets `task_id` to `5`.
- `task_id: int` — FastAPI sees this function parameter matches the path parameter name. The `: int` type hint tells FastAPI to parse it as an integer. If someone requests `/tasks/abc`, FastAPI returns a 422 error automatically — your code never runs.

#### Querying by ID

- `db.query(Task).filter(Task.id == task_id)` — adds a WHERE clause: `SELECT * FROM tasks WHERE id = ?`. The `==` here is not a Python comparison — SQLAlchemy overloads the `==` operator on column objects to produce SQL conditions.
- `.first()` — executes the query and returns the first result, or `None` if no rows match. We use `first()` instead of `all()` because we expect at most one result (IDs are unique).

#### Handling 404

- `if not task:` — if `.first()` returned `None`, the task doesn't exist.
- `raise HTTPException(status_code=404, detail="Task not found")` — we **raise** this, not return it. FastAPI catches the exception and sends:
  ```json
  {"detail": "Task not found"}
  ```
  with a 404 status code. The `detail` field is the standard FastAPI error format.
- Why `raise` instead of `return`? Because raising an exception immediately stops execution. If you had code after the check, it wouldn't run. It also makes the intent clear: this is an error path, not a success path.

## How these two endpoints relate

```
GET /tasks        -> returns []           (empty list if no tasks)
POST /tasks       -> creates task id=1
GET /tasks        -> returns [task1]
GET /tasks/1      -> returns task1
GET /tasks/999    -> returns 404
```

The list endpoint always succeeds (even with zero tasks — an empty list is valid). The single-task endpoint can fail if the ID doesn't exist.
