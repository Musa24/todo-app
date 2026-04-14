# TODO-004 · Step 04 — Final verification and commit

## Goal of this step

Turn the working-tree state we just built into a single atomic commit
on `feature/TODO-004-tests`. Nothing about the code changes in this
step — this is purely about git hygiene.

## Why one commit, not several

Conventional-commit discipline says "one logical change per commit."
TODO-004 is one logical change: "the project now has an automated
test suite covering CRUD endpoints." Splitting it into
`chore: add httpx`, `test: add conftest`, `test: add test cases`
would fragment history without making anything easier to review or
revert. A future `git log --oneline` should show TODO-004 as one
line, just like TODO-001 through TODO-003.

## What gets staged

Tracked files modified in this branch:

- `.gitignore` — added `test.db`.
- `pyproject.toml` — `httpx` added to dev dependencies by `uv add --dev`.
- `uv.lock` — lockfile updated by the same `uv add` call.
- `tests/test_tasks.py` — previously empty, now the 10 test cases.

Untracked files to add:

- `tests/conftest.py` — new fixtures module.
- `docs/TODO-004/` — four explanation docs (STEP_01 through STEP_04).

We stage files by explicit name rather than `git add -A` so we can't
accidentally include unrelated local files if any sneak in.

## What does NOT get staged

- `test.db` — it's gitignored and shouldn't exist in the tree anyway
  after `drop_all` runs. If it did appear, it would be ignored.
- `todos.db` — already ignored from prior tickets.
- Anything under `.venv/`, `__pycache__/`, `.pytest_cache/`.

## Commit message

Following the ticket's acceptance criterion ("Commit message
references ticket: 'TODO-004: ...'") and the project's conventional
commit prefix rule:

```
feat: TODO-004 add pytest suite for CRUD endpoints

Add an isolated pytest suite that exercises every task endpoint
against a dedicated SQLite database. conftest provides a test engine
bound to test.db, a per-test create/drop schema fixture, a db_session
fixture, and a TestClient fixture that overrides get_db so requests
route through the test session. test_tasks covers the happy path and
404/422 error paths for POST/GET/PUT/DELETE.
```

- The subject uses `feat:` rather than `test:` because the ticket
  itself is a deliverable that adds testing as a project capability.
  Existing commits (`feat: TODO-003 ...`, `feat: TODO-002 ...`) follow
  the same pattern.
- The body explains the *why* (isolation, acceptance criteria) not
  just the *what* (a diff already shows what).
- We'll append the required `Co-Authored-By` trailer via heredoc.

## Verification performed before committing

- `uv run pytest -v` → 10 passed.
- `git status --short` → only TODO-004 files, `test.db` absent.

## What this step does NOT do

- No push to remote.
- No PR creation.
- No merge to main.
- No edits to `app/`.
- No edits to tests.

Those are follow-up actions the user may request separately.

## Exit criteria

- `git log --oneline -1` shows a single new commit on
  `feature/TODO-004-tests` with the `TODO-004` reference in the
  subject.
- `git status` is clean.
- `uv run pytest -v` remains green on the committed tree.
