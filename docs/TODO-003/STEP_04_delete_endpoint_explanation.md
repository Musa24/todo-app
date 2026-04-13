# Step 4: DELETE /tasks/{task_id} — Delete a Task

## What we're about to write

A route handler that deletes a task by ID and returns an empty response with a 204 status code.

## Part-by-part breakdown

### 1. The route decorator

```python
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
```

- `@app.delete(...)` — handles DELETE requests.
- `status_code=status.HTTP_204_NO_CONTENT` — 204 means "success, but I have nothing to send back." This is the HTTP convention for DELETE. The task is gone — there's no meaningful data to return.
- Notice: **no `response_model`**. Since we return nothing, there's no schema to serialize through.

### 2. The function signature

```python
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
```

- Same pattern as get and update: path parameter + database session.
- Return type is `None` — we return nothing.

### 3. Find the task (or 404)

```python
task = db.query(Task).filter(Task.id == task_id).first()
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

Same pattern as the other endpoints. You can't delete a task that doesn't exist.

### 4. Delete and commit

```python
db.delete(task)
db.commit()
```

- `db.delete(task)` — marks this object for deletion in the session. Like `db.add()`, it doesn't immediately hit the database.
- `db.commit()` — executes the `DELETE FROM tasks WHERE id = ?` SQL.
- No `db.refresh()` needed — the object is gone, there's nothing to refresh.
- No `return` statement — Python functions return `None` by default, which is exactly what a 204 response needs (empty body).

## How DELETE differs from the other endpoints

| Endpoint | Returns data? | Status code | Has response_model? |
|----------|--------------|-------------|---------------------|
| POST     | Yes (created task) | 201 | Yes (TaskResponse) |
| GET      | Yes (task(s))      | 200 | Yes (TaskResponse) |
| PUT      | Yes (updated task) | 200 | Yes (TaskResponse) |
| DELETE   | No (empty body)    | 204 | No                 |

## What happens if you accidentally return data with 204?

FastAPI will ignore it. The HTTP spec says 204 responses must have no body. FastAPI enforces this — even if you `return task`, the response body will be empty. The 204 status code overrides any return value.
