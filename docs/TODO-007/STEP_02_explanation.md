# TODO-007 · Step 02 — The `render.yaml` blueprint

## Goal of this step

Decide, line by line, what goes into `render.yaml`, and *why*. When
this doc is approved, writing the file itself becomes a mechanical
translation with nothing left to debate.

Still **no code in this step** — the explanation lands first, the
YAML lands in the next chunk.

## What a Render Blueprint is

`render.yaml` is Render's Infrastructure-as-Code format. Placed at
the repo root, it's auto-discovered when you create a new service
via "Blueprint" in Render's UI. Render parses it, provisions the
services it declares, and re-reads it on every subsequent push —
so any later change to build/start commands is just a commit, not
a dashboard click.

Reference: https://render.com/docs/blueprint-spec

## The file we will write

```yaml
services:
  - type: web
    name: todos-app
    runtime: python
    plan: free
    buildCommand: pip install uv && uv sync --locked
    startCommand: uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.13"
```

That's the whole file. Nine declarative lines. Everything below
justifies one of those lines.

## Line-by-line rationale

### `services:` — top-level list

A blueprint can declare multiple services (web, worker, cron,
static site, database). We have exactly one. The list form is
required even for a single entry.

### `type: web`

A "web service" in Render's taxonomy is a long-running HTTP server
that Render fronts with its load balancer and TLS terminator. That
matches FastAPI/uvicorn exactly. Other types (`worker`, `cron`,
`pserv`, `static`) don't fit: we do accept inbound HTTP, we're not
a background job, we're not a pure static site (the backend has
live routes).

### `name: todos-app`

Human-readable service name, also the subdomain prefix of the
default URL (`todos-app.onrender.com` or similar — Render may add
a hash suffix if the name is taken globally). No functional impact
beyond identity.

### `runtime: python`

Tells Render to use its Python native runtime — a pre-built image
with Python + build toolchain, rather than asking us to ship a
`Dockerfile`. Simpler, faster, and sufficient because our only
system dependency is Python itself. If we ever needed non-Python
binaries (ffmpeg, etc.) we'd switch to `runtime: docker`.

### `plan: free`

Acceptance criteria explicitly says Render's free tier. Declaring
it in the blueprint prevents accidental upgrade-by-click.

Known trade-offs of `free`:
- Instance sleeps after ~15 min of inactivity; first request after
  idle takes ~30s to wake (cold start).
- Ephemeral disk (the SQLite caveat we already accepted).
- No custom domains without upgrade — the `*.onrender.com` URL is
  what we'll share.

### `buildCommand: pip install uv && uv sync --locked`

Two statements, chained with `&&` so a failure in either aborts
the build:

1. `pip install uv` — Render's Python runtime ships with `pip`
   but not `uv`. We bootstrap `uv` into the ambient Python. This
   is the one place in the whole stack where we touch `pip`; the
   moment `uv` exists, `pip` is out of the picture.

2. `uv sync --locked` — installs the exact dependency versions
   from `uv.lock`. `--locked` makes the build *fail loudly* if
   `pyproject.toml` and `uv.lock` have drifted, which is the same
   reproducibility guarantee CI (TODO-006) already enforces.

We don't use `uv venv` explicitly because `uv sync` creates the
`.venv` for us. We don't pass `--no-dev` because:
- Dev deps for this project are only `httpx` (listed again under
  main deps anyway) and `pytest`, weighing maybe 10 MB total.
- If we later add deployment-only deps, we can revisit and split
  groups then.

### `startCommand: uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

The runtime command, dissected:

- `uv run` — invokes the command inside the project's managed
  venv created by `uv sync`. This matches our local dev pattern
  and `CLAUDE.md`'s "always `uv run`, never bare `python3`" rule.
- `uvicorn app.main:app` — same module:attribute we use locally.
- `--host 0.0.0.0` — binds on all interfaces so Render's proxy
  can reach us (uvicorn defaults to `127.0.0.1`, which Render
  cannot see).
- `--port $PORT` — binds to the port Render injected via env var.
  Hardcoding any port (8000, 80, whatever) breaks the deploy.
- **No `--reload`** — pointless in a container built from an
  immutable artifact, and its filesystem watcher burns CPU on a
  free-tier instance.
- **No `--workers N`** — free tier has limited memory; a single
  worker is the right default. Scaling workers is a tuning task,
  not a deploy task.

### `envVars:` → `PYTHON_VERSION: "3.13"`

Render reads `PYTHON_VERSION` to pick the Python runtime. The
string form `"3.13"` is intentional — YAML would otherwise parse
`3.13` as the float `3.13` (which, confusingly, serializes back as
`3.13` but is a type mismatch Render's parser could reject on a
future schema tightening). Quoted string is defensive and costs
nothing.

This matches `.python-version` and `requires-python = ">=3.13"`
in `pyproject.toml`, so local, CI, and prod all run the same
Python minor version.

## What this blueprint deliberately does NOT contain

- **`healthCheckPath`** — Render's default is `/`, which our app
  serves (`static/index.html`). Adding it is redundant. We can add
  it later if we introduce a dedicated `/healthz` route.
- **Database service** — we're on ephemeral SQLite by explicit
  decision. No `type: pserv` Postgres entry.
- **`preDeployCommand`** — nothing to migrate; SQLite tables are
  created in-process by `Base.metadata.create_all` at startup.
- **Secrets / env vars beyond `PYTHON_VERSION`** — the app reads
  no secrets. `DATABASE_URL` is hardcoded to the relative SQLite
  path, and we're not changing that in this ticket.
- **`autoDeploy: false`** — the default is `true` (deploy on push
  to the connected branch). That's what we want once the service
  is connected; flipping it off would be surprising behaviour.

Every one of these is a conscious *not-doing*, not a gap.

## Connection to Step 03

Step 03 verifies the static-files assumption: that uvicorn on
Render runs with CWD = repo root, making `StaticFiles(directory=
"static")` and `FileResponse("static/index.html")` resolve. If that
assumption holds, Step 03 ships no code change. If it doesn't,
Step 03 converts both to absolute paths derived from `__file__`.
Either way, the decision stays *out* of the `render.yaml`.

## Exit criteria for Step 02

- [x] This explanation exists.
- [ ] You've reviewed the proposed `render.yaml` contents above
      and either approved them or asked for edits.
- [ ] On approval, Step 02b writes `render.yaml` at the repo root
      exactly as shown, and nothing else.

No YAML on disk yet. No commits yet.
