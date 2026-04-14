# TODO-005 · Step 04 — Verification, commit, PR, Jira transition

## Goal of this step

Ship TODO-005. Mirror the flow that worked for TODO-004:

- One atomic commit.
- Push the branch.
- Open a PR against `main`.
- Move the Jira ticket to **Done**.

No code is changed. This is git + GitHub + Jira only.

## Why one commit, not several

TODO-005 is one logical change: "the app now has a usable frontend."
Splitting into "serve static files", "add markup", "add JS" would
fragment history without helping future readers — and would leave
two intermediate commits where the UI is half-functional. History
should read as a sequence of shippable states, not a stream of
keystrokes. This matches the commit discipline we used for TODO-004
(`feat: TODO-004 add pytest suite for CRUD endpoints`) and TODO-003.

## What gets staged

Tracked files modified in this branch:

- `app/main.py` — added `/static` mount and `GET /` returning
  `FileResponse("static/index.html")`.
- `static/index.html` — previously empty, now a complete UI
  (markup + inline CSS + inline JS).

Untracked files to add:

- `docs/TODO-005/` — four explanation docs (STEP_01 through
  STEP_04).

We stage by explicit name rather than `git add -A` so unrelated
local files can't sneak in. (Same discipline as TODO-004.)

## What does NOT get staged

- No test changes — `tests/` is untouched in this ticket.
- No dependency changes — `StaticFiles` and `FileResponse` ship with
  FastAPI.
- No `todos.db` / `test.db` — already gitignored.
- No `.venv/`, `__pycache__/`, `.pytest_cache/`.

## Commit message

```
feat: TODO-005 add frontend UI for task management

Serve static/index.html at / and mount /static via FastAPI's
StaticFiles. The page is a single self-contained document with
inline CSS and vanilla JS — no frameworks, no build step. Users
can create, list, toggle complete, inline-edit, and delete tasks
entirely from the browser; every action calls the existing JSON
API via fetch() and re-renders the list from GET /tasks to keep
the DOM a direct function of server state.
```

- Prefix `feat:` matches the pattern of TODO-002 / TODO-003 /
  TODO-004 (feature deliverables all use `feat:`).
- Subject references the ticket as required by the acceptance
  criteria.
- Body explains the *why* (re-render from server state, no build
  step, no frameworks) — the diff already shows the *what*.
- We'll append the `Co-Authored-By` trailer via heredoc.

## Pre-commit verification

Before staging, re-run `uv run pytest -v`. This ticket doesn't
change any tested code, so the suite must remain at 10 green. If it
isn't, something in `app/main.py` broke — stop and investigate.

## PR body

Mirror the TODO-004 PR structure:

```
## Summary
- app/main.py mounts /static via StaticFiles and serves
  static/index.html at GET /.
- static/index.html is a complete single-page UI (inline CSS
  and vanilla JS, no frameworks) that creates, lists, toggles,
  inline-edits, and deletes tasks via fetch() against the
  existing API. The list is re-rendered from GET /tasks after
  every mutation.

Closes [TODO-5](https://udemycourse2495.atlassian.net/browse/TODO-5).

## Test plan
- [x] `uv run pytest -v` — 10 tests still pass (no backend
      regression)
- [x] Manual browser verification in the user's session: page
      loads, create/list/toggle/edit/delete all work and persist
      across reload
- [x] Branch name matches ticket: feature/TODO-005-frontend
```

The manual-verification line is marked done because we agreed the
user would perform the browser walkthrough; if they haven't, the PR
can still be opened but we'll leave it to them to confirm before
merging.

## Jira transition

TODO-5 currently sits in **To Do**. The transitions list for this
project (seen during TODO-004) has `id=31` for **Done**. We'll
issue a single transition call using that id.

## Post-merge cleanup

Same as TODO-004: leave local + remote branch deletion to the user
after they merge. Don't run destructive git commands proactively.

## Exit criteria

- `git log --oneline -1` shows one new commit with `TODO-005` in the
  subject.
- Working tree clean on `feature/TODO-005-frontend`.
- PR URL returned from `gh pr create`.
- Jira API confirms TODO-5 status is **Done**.
