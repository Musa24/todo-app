# TODO-007 · Step 04 — Deployment record

## Live URL

**https://todos-app-i8zm.onrender.com/**

Service was created via Render Blueprint, reading `render.yaml`
from branch `feature/TODO-007-deployment` of `Musa24/todo-app`.

## Acceptance criteria — verified

Smoke test executed at 2026-04-16, against the live URL, on a
warm instance. Results:

| # | Check | Result |
| - | --- | --- |
| 1 | `GET /` returns the frontend HTML | 200 |
| 2 | `GET /static/index.html` resolves | 200 |
| 3 | `POST /tasks` creates a task | 201, returns id |
| 4 | `GET /tasks/{id}` reads it back | 200 |
| 5 | `PUT /tasks/{id}` edits it | 200 |
| 6 | Edit took effect (re-read shows new title) | confirmed |
| 7 | `DELETE /tasks/{id}` removes it | 204 |
| 8 | `GET /tasks/{id}` after delete | 404 |

The Step 03 static-path fix is confirmed working in production:
`/` and `/static/index.html` both resolve, despite the static
files living under a path Render's process CWD might not have
matched.

## Known caveats (already accepted, recorded for the next reader)

### 1. Free-tier cold start — intermittent `no-server` 404s

After ~15 min of inactivity the Render free tier spins the
instance down. The next request lands while the container is
still waking, and Render's edge proxy returns a 404 with header
`x-render-routing: no-server` — *before* the request reaches
uvicorn. Subsequent requests succeed once the instance is up
(typically within a few seconds).

This is method-agnostic and not a code bug. During the initial
smoke test, one PUT happened to be the cold-start victim; a retry
loop confirmed 4/5 PUTs succeed cleanly and the 1 failure shows
`x-render-routing: no-server` (proxy-level, never reached our
app).

If cold-start latency becomes a real problem for users, the fix
is upgrading off the free plan — not a code change.

### 2. Ephemeral SQLite

`DATABASE_URL = "sqlite:///./todos.db"` writes to the container's
local filesystem, which Render free-tier wipes on every restart
or redeploy. Tasks created through the deployed UI will disappear
after the next deploy or idle-restart.

This trade-off was explicitly accepted in Step 01. Durable storage
(Postgres add-on or a Render persistent disk) belongs in a
separate ticket if needed.

## Auto-deploys

Render's Blueprint flow defaults to `autoDeploy: true`, so future
pushes to `feature/TODO-007-deployment` (and, after merge, to
`main`, depending on which branch the Blueprint is reconnected to)
trigger automatic rebuilds. No further manual deploy steps.

## Exit criteria for Step 04

- [x] Service deployed and reachable at a public URL.
- [x] All ticket acceptance criteria pass on the live service.
- [x] URL recorded in this document and shared.
- [ ] PR #6 merged to `main` once the URL has been confirmed by
      the user.
