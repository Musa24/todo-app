# TODO-004 · Step 02 — `tests/conftest.py`

## Goal of this step

Create the pytest fixture module that every test in this ticket will
rely on. After this step:

- Tests run against a **separate SQLite file** (`test.db`), never the
  real `todos.db`.
- Every test starts with an **empty schema** and ends with the schema
  dropped, so tests can't leak state into each other.
- Tests can ask for a `db_session` when they want direct DB access.
- Tests can ask for a `client` when they want to make HTTP calls, and
  that client will be wired to the same test session via FastAPI's
  dependency override system.

## Why a separate test database at all?

Two reasons:

1. **Safety.** If the tests ever hit `todos.db`, a bad test could
   wipe real data. Using `test.db` makes this impossible by
   construction.
2. **Isolation.** Tests need deterministic starting state. Starting
   from an empty database means tests don't depend on what previous
   runs (or the user's manual experiments) left behind.

## Why drop tables between tests?

`Base.metadata.create_all` + `Base.metadata.drop_all` on each test
gives every test a fresh, empty schema. Alternatives we rejected:

- **Truncate tables only** — faster, but adds complexity and can
  desync from schema changes.
- **One engine per process, truncate per test** — same tradeoff.
- **In-memory SQLite (`sqlite:///:memory:`)** — cleaner, but doesn't
  match the acceptance criteria (which requires `sqlite:///./test.db`)
  and is harder to reason about when a test leaves the DB file around
  for manual inspection.

Create/drop is the simplest thing that works and matches the ticket.

## The four fixtures

### 1. The test engine (module-level, not a fixture)

A single `create_engine("sqlite:///./test.db", ...)` built once when
conftest is imported. It's cheap to create and reused across every
test. We pair it with its own `sessionmaker` so test sessions don't
accidentally bind to the production engine.

We keep the same `connect_args={"check_same_thread": False}` as the
app engine because FastAPI's `TestClient` and the request handler can
end up on different threads.

### 2. Per-test schema setup/teardown

An **autouse** fixture (`scope="function"`, the default) that:

- Calls `Base.metadata.create_all(bind=test_engine)` before yielding.
- Calls `Base.metadata.drop_all(bind=test_engine)` after the test
  finishes.

`autouse=True` means every test gets this behavior automatically — a
test author can't forget to ask for it.

### 3. `db_session` fixture

A function-scoped fixture that:

- Opens a session from the test `sessionmaker`.
- `yield`s it to the test.
- Closes it in the `finally` branch so the session is always released
  even if the test raises.

Tests that want to insert a row directly (for example, to pre-populate
data before hitting an endpoint) will use this fixture.

### 4. `client` fixture

A function-scoped fixture that:

- Defines a local `override_get_db` generator that yields from the
  test `sessionmaker`.
- Registers it in `app.dependency_overrides[get_db]`. FastAPI's
  dependency override system swaps out `get_db` for this function for
  the duration of the test, so every endpoint call uses the test DB.
- Yields `TestClient(app)` to the test.
- Cleans `app.dependency_overrides` on the way out so overrides don't
  leak into other tests or into the app at runtime.

### Why two session-producing paths (`db_session` and the override)?

They produce sessions from the same `sessionmaker`, so they talk to
the same database. We just can't reuse a single session object
between the test and the request handler reliably — the request
handler closes its session when the request ends. Having each path
open its own session matches how production works and keeps the
fixtures simple.

## File layout

`tests/conftest.py` will be ~35 lines and structured as:

```
imports
test engine + test sessionmaker (module-level)
@pytest.fixture(autouse=True) setup_database
@pytest.fixture db_session
@pytest.fixture client
```

No test cases yet — those come in Step 03.

## Exit criteria for this step

- `tests/conftest.py` exists and is syntactically valid.
- `uv run pytest --collect-only` succeeds (no tests collected yet,
  but collection must not error on conftest).
- `tests/test_tasks.py` is still untouched.
