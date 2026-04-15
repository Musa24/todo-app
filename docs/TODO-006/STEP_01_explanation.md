# TODO-006 · Step 01 — GitHub Actions CI workflow

## Goal of this step

Wire up a CI pipeline that runs the pytest suite automatically on:

- every push to `main`
- every pull request targeting `main`

After this step, each PR shows a green check (or red X) in GitHub
*before* it's reviewed. No more "works on my machine" as the only
signal.

## Intuition

CI is a feedback loop. We already have the feedback loop locally
(`uv run pytest`); the job of the workflow file is to reproduce that
same loop on a clean, ephemeral machine that nobody has touched.
If the suite passes there, it passes for everyone.

A CI job is basically a shell script with three extra concerns:

1. **Where it runs** — a named `runs-on` runner image (we'll use
   `ubuntu-latest`, the GitHub-hosted Linux runner).
2. **When it runs** — the `on:` triggers (push + pull_request).
3. **How dependencies are obtained deterministically** — we use
   `uv` and the project's `uv.lock`, so the runner installs the
   exact same versions we developed against.

Everything else is setup: checkout the code, get Python, get `uv`,
install, run tests.

## Why a single job, a single workflow file

The ticket asks for one thing: run the tests. Splitting into
multiple jobs (lint, type-check, matrix over Python versions) is
scope creep — `requires-python = ">=3.13"` in `pyproject.toml` and
`.python-version` pinning to `3.13` both say we target one Python
version. A matrix would add complexity for no correctness win right
now.

## Why `astral-sh/setup-uv` instead of `pip install uv`

`astral-sh/setup-uv` is the official action maintained by Astral
(the team that ships `uv`). It:

- installs a pinned `uv` binary from a signed release,
- caches the `uv` download across runs,
- optionally caches the project's dependency downloads using
  `uv.lock` as the cache key.

The alternative — `pip install uv` — would pull from PyPI every
run and miss the lockfile-aware caching. Using the first-party
action is both faster and the documented recipe in the `uv` docs.

## Why `uv sync` and not `uv pip install -e .`

`uv sync` is `uv`'s project-level command. It reads `pyproject.toml`
+ `uv.lock`, creates a `.venv`, and installs the locked versions
including dev dependencies. It's the same thing `uv run` would do
implicitly — running it explicitly makes the CI log easier to read
and lets us cache the result.

## Why `uv run pytest -v` and not `pytest -v`

The global `pytest` binary doesn't exist on a fresh runner. The
project's pytest lives inside the `uv`-managed `.venv` and is
invoked via `uv run pytest`. `-v` is required by the acceptance
criteria and also makes CI logs far more useful when something
fails.

## What the workflow file will contain

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.13"
          enable-cache: true
      - run: uv sync --locked
      - run: uv run pytest -v
```

A few notes on specific choices:

- `actions/checkout@v4` — latest stable major version as of the
  knowledge cutoff; pinning to `@v4` (not `@main`) means the action
  code is frozen unless we bump it deliberately.
- `astral-sh/setup-uv@v5` — latest major; `python-version: "3.13"`
  tells the action to provision Python 3.13 for us *instead of*
  needing a separate `actions/setup-python` step. One action, two
  jobs handled.
- `enable-cache: true` — caches `uv`'s download cache keyed off
  `uv.lock`, so reruns on unchanged dependencies skip the download
  phase entirely.
- `uv sync --locked` — fails loudly if `uv.lock` is out of sync
  with `pyproject.toml`, which is exactly the signal we want in CI.

## Why the file lives at `.github/workflows/ci.yml`

GitHub Actions discovers workflows only under `.github/workflows/`
at the repo root. The filename is free-form; `ci.yml` is
convention. The acceptance criteria pins this path exactly.

## Branch strategy

Cut `feature/TODO-006-ci` from current `main` (already
fast-forwarded after the TODO-005 merge). Push the branch and open
a PR — the PR event itself is what triggers the workflow's first
run, which is how we verify the green check.

## What will NOT change in this step

- No Python code changes.
- No test changes.
- No new dependencies — the workflow only uses GitHub-hosted
  actions and the existing `uv.lock`.

## Exit criteria

- `.github/workflows/ci.yml` exists and validates as YAML.
- Branch `feature/TODO-006-ci` contains one commit prefixed
  `TODO-006:`.
- After push + PR, the Actions tab shows a green check on the
  `test` job.
- `uv run pytest -v` still passes locally (sanity check — the
  workflow should produce the same result).
