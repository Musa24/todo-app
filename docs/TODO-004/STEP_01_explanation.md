# TODO-004 · Step 01 — Branch, gitignore, and test dependency

## Goal of this step

Set up the scaffolding needed before we write any test code:

1. Move onto the branch the ticket requires (`feature/TODO-004-tests`).
2. Make sure the test database file will never be committed.
3. Make sure the test-only HTTP client library is available.

No test code is written in this step. This step is purely about getting
the environment in the right shape so the next step can focus on
fixtures.

## Intuition

Writing tests touches three things outside of the test files themselves:

- **Git state** — work must happen on the right branch, and artifacts
  created by running the tests (a SQLite file) must not be tracked.
- **Dependencies** — FastAPI's `TestClient` is a thin wrapper around
  the `httpx` library. If `httpx` is not installed, `from
  fastapi.testclient import TestClient` will still import, but the
  first `TestClient(app)` call will raise `RuntimeError: The starlette
  .testclient module requires the httpx package to be installed.` We
  install it up front so we never hit that error.
- **Working directory hygiene** — the test database lives beside the
  app database. We keep them separate by name (`test.db` vs
  `todos.db`) and by ignoring both in git.

## What will change

### `.gitignore`

Add one line under the existing `# Database` section:

```
test.db
```

`todos.db` is already ignored. `test.db` is the file pytest will
create when the test engine opens `sqlite:///./test.db`. Without this
line, the first test run would dirty the working tree.

### `pyproject.toml` (via `uv add --dev httpx`)

`uv add --dev httpx` adds `httpx` to the `[dependency-groups].dev`
section and updates `uv.lock`. We use `--dev` rather than a plain
dependency because `httpx` is only needed by the test suite, not by
the running application.

### Git branch

Create and check out `feature/TODO-004-tests` from the current HEAD
(tip of `feature/TODO-003-crud-endpoints`). Acceptance criteria
require this exact branch name.

## What will NOT change in this step

- No files under `tests/` are created or edited.
- No app code is touched.
- No commits are made yet — we'll commit once the full ticket is
  green, so the commit tells a single coherent story.

## Exit criteria for this step

- `git branch --show-current` → `feature/TODO-004-tests`
- `.gitignore` contains `test.db`
- `uv run python -c "import httpx; print(httpx.__version__)"` succeeds
- No files added under `tests/` yet
