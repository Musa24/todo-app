# Step 3: PUT /tasks/{task_id} — Update a Task

## What we're about to write

A route handler that updates an existing task. The tricky part: it must support **partial updates** — the client can send only the fields they want to change, and everything else stays the same.

## The core problem: partial updates

Imagine a task looks like this in the database:

```json
{"id": 1, "title": "Buy groceries", "description": "Milk and eggs", "completed": false}
```

The client wants to mark it as completed. They send:

```json
PUT /tasks/1  {"completed": true}
```

They did NOT send `title` or `description`. We must:
- Keep the existing `title` and `description` untouched
- Only change `completed` to `true`

If we naively did `task.title = payload.title`, we'd overwrite `title` with `None` (because the client didn't send it), destroying good data.

## How we solve it: `model_dump(exclude_unset=True)`

Pydantic v2 has a method `model_dump()` that converts a Pydantic model back to a dict. With `exclude_unset=True`, it only includes fields the **client actually sent** — not the defaults.

Example:

```python
# Client sends: {"completed": true}
# Pydantic parses into: TaskUpdate(title=None, description=None, completed=True)

update.model_dump()                       # {"title": None, "description": None, "completed": True}
update.model_dump(exclude_unset=True)     # {"completed": True}   <- only what was sent
```

This is the key. We only update fields that were explicitly provided.

## Part-by-part breakdown

### 1. The route decorator

```python
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, update: TaskUpdate, db: Session = Depends(get_db)):
```

- `@app.put(...)` — handles PUT requests.
- `task_id: int` — path parameter for which task to update.
- `update: TaskUpdate` — FastAPI parses the request body into our `TaskUpdate` schema. Remember, all fields in `TaskUpdate` are optional, so the client can send as few or as many as they want.

### 2. Find the task (or 404)

```python
task = db.query(Task).filter(Task.id == task_id).first()
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

Same pattern as `get_task`. If the task doesn't exist, we return 404 before trying to update anything.

### 3. Apply only the sent fields

```python
for field, value in update.model_dump(exclude_unset=True).items():
    setattr(task, field, value)
```

- `update.model_dump(exclude_unset=True)` — returns a dict with only the fields the client sent.
- `for field, value in ....items():` — iterate over each key/value pair.
- `setattr(task, field, value)` — dynamically set that attribute on the SQLAlchemy task object. `setattr(task, "completed", True)` is equivalent to `task.completed = True`, but works when the field name is a variable.

This loop is the whole partial-update magic. If the client sent only `completed`, we only set `completed`. If they sent nothing, the loop runs zero times and nothing changes.

### 4. Commit and refresh

```python
db.commit()
db.refresh(task)
return task
```

- `db.commit()` — writes the changes. Because we imported `onupdate=func.now()` on the `updated_at` column (Step 2 of TODO-002), SQLAlchemy automatically bumps `updated_at` to the current time as part of the UPDATE statement. We don't touch it manually.
- `db.refresh(task)` — re-reads the row to pick up the new `updated_at` value that the database just generated.
- `return task` — FastAPI serializes it through `TaskResponse`.

## Why not `task.title = update.title`?

If the client doesn't send `title`, `update.title` is `None`. Assigning it would overwrite the existing title with `None`. That would be a bug — the client would lose their title.

`exclude_unset=True` is how we tell the difference between:
- "I sent `title: null` (explicitly set to null)"  (included in dump)
- "I didn't send `title` at all" (excluded from dump)

For this app we only care about the second case — a field the client didn't send should remain unchanged.
