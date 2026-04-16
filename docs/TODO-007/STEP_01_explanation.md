# TODO-007 · Step 01 — Deployment blueprint

## Goal of this step

Agree on *how* the app will be deployed to Render before we write
a single line of deployment config. After this step the only thing
left is to translate this plan into a `render.yaml` and push it.

This step produces **no code** — only this explanation and the new
branch `feature/TODO-007-deployment`.

## What "deploy to Render" actually means

Render is a managed platform: we hand it a Git repo, tell it two
things — *how to build* and *how to start* — and it gives us back a
public HTTPS URL pointed at a container running our app.

So the entire ticket reduces to answering three questions:

1. How does Render know how to build our project?
2. How does Render know how to run our project?
3. How does our running process talk to the outside world?

Everything else (TLS, DNS, zero-downtime deploys, log streaming) is
Render's problem, not ours.

## Choice: `render.yaml` over `Procfile`

Render accepts either. We're picking `render.yaml` (a Blueprint)
because:

- It's declarative and version-controlled — the service's shape
  (build command, start command, env, plan) lives in the repo, not
  in a dashboard nobody can audit.
- It's the path Render's current docs lead with; `Procfile` is the
  Heroku-legacy compatibility layer.
- It lets us describe the whole service in ~10 lines, which is the
  right size for a single-service app like this one.

A `Procfile` would work and would be shorter, but every other
setting (Python version, build command) would live *only* in
Render's web UI — invisible to anyone reading the repo.

## Render's runtime contract — the only two things we must obey

### 1. Bind to `$PORT` on `0.0.0.0`

Render assigns our container a port at runtime and exposes it as
the environment variable `PORT`. The container must bind to that
port on `0.0.0.0` (all interfaces), not `127.0.0.1`. If we bind to
localhost or to a hardcoded port, Render's health check fails and
the deploy is marked unhealthy.

Concretely our start command becomes:

```
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Two deliberate differences from the local dev command in `CLAUDE.md`:

- **No `--reload`.** Reload watches the filesystem for changes,
  which is pointless in a container built from an immutable image
  and wastes CPU.
- **Explicit `--host 0.0.0.0`.** Uvicorn's default is `127.0.0.1`,
  which is invisible from outside the container.

### 2. Build must be reproducible and non-interactive

The build command runs on a fresh Render build machine with no
`uv` preinstalled. We therefore need to install `uv` first, then
let it install locked dependencies:

```
pip install uv && uv sync --locked
```

`--locked` fails the build if `pyproject.toml` and `uv.lock` have
drifted, which is exactly the signal we want in a deploy pipeline
(same reasoning as the CI workflow from TODO-006).

## SQLite on Render free tier — known caveat, accepted

The app uses `sqlite:///./todos.db` (see `app/database.py:6`).
Render's free web-service tier has an **ephemeral filesystem**: the
disk is wiped every time the service restarts, redeploys, or gets
recycled for inactivity. That means tasks created through the
deployed UI will disappear on the next deploy or idle-restart.

You've explicitly accepted this for this ticket — the goal is
"the app is reachable and the CRUD flow works end-to-end", not
"data persists across restarts". Durable storage is its own
concern and belongs in a separate ticket (Postgres add-on or a
Render persistent disk).

Nothing in the code needs to change for this trade-off; we're just
naming it here so nobody is surprised later.

## Static files — a risk to check in Step 03

`app/main.py` mounts static assets with relative paths:

- `StaticFiles(directory="static")` — line 14
- `FileResponse("static/index.html")` — line 19

These resolve against the **current working directory** of the
uvicorn process, not the location of `main.py`. On Render the
working directory is the repo root (`/opt/render/project/src`),
so these relative paths *should* resolve correctly — but this is
an assumption worth verifying, not asserting. Step 03 confirms it
(and converts to absolute paths if Render's working directory
turns out to differ from our expectation).

Not doing it now keeps this step scoped to "decide the deployment
shape".

## Python version

`pyproject.toml` requires `>=3.13` and `.python-version` pins to
`3.13`. Render supports 3.13 on its Python runtime. We'll pin it
explicitly in `render.yaml` via `PYTHON_VERSION` to avoid depending
on whatever default Render happens to ship.

## What will change across this ticket

| File | Purpose | Step |
| --- | --- | --- |
| `docs/TODO-007/STEP_01_explanation.md` | This file | 01 |
| `render.yaml` | Blueprint Render reads to build + run | 02 |
| (maybe) `app/main.py` | Absolute paths for static dir, *only if* Step 03 proves it's needed | 03 |
| — | Push, connect Render service, deploy, smoke-test | 04 |

## Branch strategy

`feature/TODO-007-deployment` is cut from the current `main` (which
already includes the TODO-006 CI merge). All step commits land on
this branch. Commit prefix: `TODO-007:`.

## Exit criteria for Step 01

- [x] Branch `feature/TODO-007-deployment` exists and is checked
      out.
- [x] This explanation document exists under `docs/TODO-007/`.
- [ ] You have read it and approved moving to Step 02 (write
      `render.yaml`).

No Python, no YAML, no commits yet.
