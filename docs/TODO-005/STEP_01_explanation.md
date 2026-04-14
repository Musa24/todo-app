# TODO-005 · Step 01 — Branch + serve static assets from FastAPI

## Goal of this step

Teach the FastAPI app to serve the frontend. After this step:

- Visiting `http://localhost:8000/` returns the contents of
  `static/index.html` (which is currently empty — that's fine).
- Visiting `http://localhost:8000/static/<anything>` serves files
  directly from the `static/` directory.

No UI work yet. This step is pure backend plumbing so that Step 02
can focus exclusively on the HTML/CSS.

## Intuition

Two distinct mechanisms are needed, and it's worth understanding why
we don't just use one:

1. **The `/static` mount** is for *any* static asset — CSS files,
   JS files, images, fonts. FastAPI's `StaticFiles` (from starlette)
   walks the filesystem relative to the `directory=` argument and
   serves whatever it finds with correct content-type headers and
   proper caching behavior. We mount it under `/static` so these URLs
   can never accidentally collide with API routes.

2. **The root `/` route** is different. We don't want
   `http://localhost:8000/` to 404 or to list a directory — we want
   it to return the app's entry page. We could have accomplished
   this by mounting `StaticFiles(directory="static", html=True)` at
   `/`, which would auto-serve `index.html` on root — but that
   *also* captures every unmatched path, which would shadow future
   API routes if we're not careful. An explicit `GET /` returning
   `FileResponse("static/index.html")` is narrower and clearer.

## Why `FileResponse` and not `HTMLResponse(open(...).read())`?

`FileResponse` streams the file from disk on each request, sets
`Content-Type: text/html` based on the extension, and handles
`ETag` / `Last-Modified` headers. It's the right tool for "serve
this file." Reading the file into memory and wrapping it in
`HTMLResponse` would be wasteful and would bypass FastAPI's file
handling niceties.

## Why not put the mount and the route in a separate router?

Routers are great when route grouping becomes a maintenance
concern. Right now we have ~5 routes in `app/main.py`. Adding one
more route and one `mount` keeps the file well under the 200-line
soft limit in CLAUDE.md. Splitting it prematurely would hurt
readability without any upside.

## What will change in `app/main.py`

Additions (not replacements):

```python
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# after `app = FastAPI()`:
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    return FileResponse("static/index.html")
```

- `include_in_schema=False` keeps the root page out of the
  auto-generated OpenAPI docs — it's not part of the JSON API.
- The mount goes **after** `app = FastAPI()` but its order relative
  to other route decorators doesn't matter: FastAPI matches explicit
  routes before falling through to mounts. The `/tasks` endpoints
  remain reachable.

## Why existing tests should still pass

- No test touches `/` or `/static/*` — they all hit `/tasks`.
- `TestClient` initializes the app the same way a real server does,
  so the mount is evaluated, but no test exercises it.
- The mount *does* require `static/` to exist at import time, and it
  does (contains an empty `index.html`). If `static/` were missing,
  `StaticFiles` would raise on startup.

We'll verify by re-running `uv run pytest -v` after the edit — the
suite must remain 10 green.

## Branch strategy

Cut `feature/TODO-005-frontend` from current `main` (which was
fast-forwarded after the TODO-004 merge). This way the branch is a
clean diff of TODO-005's work, no baggage from TODO-004.

## What will NOT change in this step

- `static/index.html` stays untouched (empty).
- No new dependencies — `StaticFiles` and `FileResponse` ship with
  FastAPI/starlette.
- No test changes.
- No new tests either — serving a file at `/` is trivial starlette
  behavior and the acceptance criteria don't require a test for it.

## Exit criteria

- Branch: `git branch --show-current` → `feature/TODO-005-frontend`.
- `uv run pytest -v` → 10 passed (unchanged).
- `uv run uvicorn app.main:app --reload` starts without errors
  (verified quickly, not left running).
- Visiting `/` returns the current empty `index.html` (a blank
  page with 200 OK).
