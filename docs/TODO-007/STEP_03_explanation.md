# TODO-007 · Step 03 — De-risking static-file paths

## Goal of this step

Decide whether to leave `app/main.py`'s relative static paths
alone, or preemptively convert them to absolute paths anchored on
`__file__`. Ship the smallest code change (possibly none) that
makes the Render deploy reliable.

Still **no code in this step** — just the decision and the
rationale. Code, if any, lands in Step 03b.

## The two lines under scrutiny

`app/main.py`:

```python
app.mount("/static", StaticFiles(directory="static"), name="static")  # line 14

@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    return FileResponse("static/index.html")                          # line 19
```

Both strings are **relative paths**. `StaticFiles` and
`FileResponse` resolve them against whatever the process's current
working directory happens to be at request time.

## What is Render's CWD actually?

I checked Render's official docs
([deploy-fastapi](https://render.com/docs/deploy-fastapi),
[troubleshooting-python-deploys](https://render.com/docs/troubleshooting-python-deploys))
and community threads. Findings:

- Render clones the repo to `/opt/render/project/src` (confirmed
  by community posts referencing that absolute path).
- Every Render Python example in their docs uses **relative
  module/file references** in the start command
  (`uvicorn main:app`, `gunicorn app:app`, etc.), which only work
  if the start command runs with CWD at the repo root. This is the
  de-facto contract.
- But Render's docs do **not** explicitly promise "your start
  command runs with CWD = repo root" as a typed guarantee. It's
  convention-by-inference.

So: the status quo probably works. "Probably" is a bad word for a
deploy step you only want to do once.

## Two options

### Option A — Trust the convention, ship no code change

Pros:
- Zero code delta; nothing to regress.
- Matches every Render example in the wild.

Cons:
- Relies on a convention Render doesn't actually document as
  stable. A future change to how Render invokes the process
  (uncommon but not impossible) would break us.
- If it *does* break on deploy, the failure mode is a 404 at `/`
  with no useful stack trace — which is annoying to debug live.
- Our **tests** run via pytest with CWD at the repo root too, so
  tests pass even if Render were different — the test suite can't
  catch this class of bug.

### Option B — Anchor paths to `__file__` (recommended)

Change the two lines to derive their path from the location of
`main.py` itself:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
```

- `Path(__file__)` is the absolute path to `app/main.py`.
- `.resolve().parent.parent` climbs `app/` → repo root.
- `STATIC_DIR` is a single computed constant used in both places.

Pros:
- CWD-independent. Works on Render, in CI, in pytest, and under
  any future process manager regardless of how it was invoked.
- Same number of logical operations, three extra physical lines.
- Makes the assumption *explicit* — a reader sees the layout the
  code assumes.

Cons:
- Introduces two lines of derived constants where there used to
  be string literals. Marginal increase in indirection.
- Very slightly tighter coupling to the repo layout (`app/` must
  be one level below the static dir) — but that's already true
  today, just implicit.

## Recommendation

**Option B.** The cost is three lines; the payoff is eliminating
a silent-on-CI / loud-on-Render failure mode. The Explain-then-Code
workflow we're following is explicitly about avoiding "oh no, the
deploy broke in a way tests didn't catch" moments, and this is
one of those.

## What Step 03b will look like if you approve Option B

Single edit to `app/main.py`:

- Add `from pathlib import Path` to the imports.
- Add two module-level constants (`BASE_DIR`, `STATIC_DIR`) below
  the existing imports / above the `Base.metadata.create_all` call.
- Change the `StaticFiles(directory="static")` argument to
  `STATIC_DIR`.
- Change the `FileResponse("static/index.html")` argument to
  `STATIC_DIR / "index.html"` (FastAPI's `FileResponse` accepts
  `PathLike`, so this works without `str(...)`).

Nothing else moves. No test changes needed — the existing tests
hit `/` and `/tasks/...` with CWD at repo root, and the new code
works from any CWD, so they stay green.

## If you pick Option A instead

Step 03 ends right here. We proceed to chunk 4 (commit, push,
connect Render, deploy, smoke-test) with `app/main.py` untouched.
If the deploy 404s at `/`, we'd roll back to the Option-B patch as
a fix-forward — which is fine, just noisier than doing it now.

## Exit criteria for Step 03

- [x] This explanation exists.
- [ ] You've picked Option A (ship no code) or Option B (tiny
      patch in Step 03b).
- [ ] If Option B: the patch lands and all existing tests
      (`uv run pytest -v`) still pass locally.

No code changes yet. No commits yet.
