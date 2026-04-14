# TODO-004 · Step 03 — `tests/test_tasks.py`

## Goal of this step

Write the 10 test cases the acceptance criteria require. Every test
uses the `client` fixture (and occasionally `db_session`) from
`conftest.py`. Each test starts with a fresh, empty database thanks
to the autouse `setup_database` fixture.

## Guiding principles

- **One behavior per test.** Each test name reads like a
  specification — what the endpoint should do under one specific
  condition.
- **Assert the contract, not the implementation.** We assert status
  codes, response shapes, and observable side effects (e.g. a
  subsequent GET returns 404 after DELETE). We don't poke at internal
  SQLAlchemy state unless the test is specifically about persistence.
- **No shared state between tests.** The autouse fixture handles
  this. Tests that need pre-existing data create it themselves via
  `client.post(...)` so the path of creation is realistic.
- **Short, readable bodies.** Arrange → Act → Assert. No helper
  functions yet — 10 small tests don't justify a helper layer.

## The 10 tests in detail

### 1. `test_create_task_returns_201_and_echoes_fields`
`POST /tasks` with `{"title": "Buy milk", "description": "2% please"}`.
Assert status 201, response JSON has `title == "Buy milk"`,
`description == "2% please"`, `completed is False`, and `id` is an
integer. This nails down the creation contract.

### 2. `test_create_task_returns_422_when_title_missing`
`POST /tasks` with `{"description": "no title here"}`. Assert 422.
We don't inspect the error body shape — that's FastAPI's territory;
we only care that the validator rejects the input.

### 3. `test_list_tasks_is_empty_initially`
`GET /tasks` on an empty DB. Assert status 200, body is `[]`. This
also implicitly verifies the autouse teardown from a previous test
actually ran.

### 4. `test_list_tasks_returns_created_tasks`
Create two tasks via POST, then `GET /tasks`. Assert status 200,
length 2, and both titles appear in the response. We don't assert
ordering because the endpoint doesn't promise one.

### 5. `test_get_task_returns_correct_task`
Create a task, capture its `id`, `GET /tasks/{id}`, assert status
200 and the fields match.

### 6. `test_get_task_returns_404_for_unknown_id`
`GET /tasks/99999`. Assert status 404.

### 7. `test_update_task_updates_only_provided_fields`
Create a task with title "A" and description "desc". PUT
`{"title": "B"}` only. Assert status 200, response shows
`title == "B"` **and** `description == "desc"` (unchanged). This
directly tests the partial-update behavior of `TaskUpdate` +
`model_dump(exclude_unset=True)`.

### 8. `test_update_task_returns_404_for_unknown_id`
`PUT /tasks/99999` with any valid body. Assert status 404.

### 9. `test_delete_task_returns_204_and_task_is_gone`
Create a task, `DELETE /tasks/{id}`, assert status 204, then
`GET /tasks/{id}` and assert 404. Two-step assertion because "204
was returned" alone doesn't prove the row is gone.

### 10. `test_delete_task_returns_404_for_unknown_id`
`DELETE /tasks/99999`. Assert status 404.

## What the test file will NOT do

- No parametrization. 10 distinct behaviors, each worth its own
  name; `@pytest.mark.parametrize` would hurt readability here.
- No mocks. The whole point of the TODO-004 design is to run tests
  against a real SQLite DB so SQLAlchemy, Pydantic, and FastAPI
  integrate for real.
- No global constants for test payloads. Inline dicts keep each test
  self-contained.

## Exit criteria for this step

- `uv run pytest -v` shows 10 tests, all green.
- No changes to `app/` code.
- Only new file: `tests/test_tasks.py`.
