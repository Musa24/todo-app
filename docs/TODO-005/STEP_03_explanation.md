# TODO-005 · Step 03 — Vanilla JavaScript: fetch + DOM

## Goal of this step

Make the UI actually work. After this step:

- The page fetches `GET /tasks` on load and renders every task.
- Submitting the form POSTs a new task and re-renders.
- Clicking the checkbox toggles `completed` via PUT.
- Clicking Edit swaps the spans for inputs; Save PUTs the changes;
  Cancel discards them.
- Clicking Delete DELETEs the task.
- Every action ends with a fresh render — no manual page refresh.

## Design choices (and why)

### 1. Re-render the whole list after every mutation

Instead of carefully patching a single `<li>` in place after each
API call, we call `loadTasks()` after every mutation. That function
clears `#task-list` and rebuilds it from the latest `GET /tasks`
response.

**Why this design:**

- **Single source of truth.** The DOM is always a direct function
  of the API response. No drift possible.
- **Fewer bugs.** Optimistic in-place patching requires handling
  rollback on failure, stale ids, checkbox state flicker, and
  edit-mode preservation. Re-rendering sidesteps all of it.
- **Cost is negligible.** For ~10–100 todos, a full GET + DOM
  rebuild is a few milliseconds and one network round-trip. For a
  learning project with no perf requirement, that's free.

This is the same tradeoff React made at its core (re-render,
reconcile), just without the reconciler.

**The one concession:** the "currently being edited" task is a UI
state that doesn't exist on the server. If we re-render while an
edit is in-flight, we'd wipe the inputs. So edit mode lives in the
DOM of that specific `<li>` and we only re-render after Save or
Cancel, not while editing.

### 2. A tiny `api()` helper, not a client library

```js
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (res.status === 204) return null;
  return res.json();
}
```

- Centralises `Content-Type` and error handling so each call site
  stays one line.
- Throws on non-2xx so callers can `catch` if they want.
- Returns `null` on 204 (our DELETE response) to avoid a JSON parse
  on an empty body.

No libraries, no axios — `fetch` is enough.

### 3. Build DOM nodes, don't string-template

We'll use `document.createElement(...)` and `.textContent = ...`
rather than `innerHTML = \`<li>${task.title}...\``.

**Why:** `innerHTML` with interpolated task fields is an XSS vector
— a task titled `<img src=x onerror=alert(1)>` would execute. Even
though this is a local-only app, it's a bad habit to normalize.
`textContent` and `createElement` are immune by construction and
only marginally more verbose.

### 4. Event delegation vs per-element listeners

Two options for the per-task buttons:

- **Per-element:** attach listeners when building each `<li>`.
  Simple, obvious, works.
- **Delegation:** one listener on `#task-list` that inspects
  `event.target`. Scales better, survives re-renders more
  cleanly.

We'll use per-element listeners. We re-render the whole list, so
we rebuild the listeners too — the delegation win doesn't apply.
And per-element is easier to read when you're learning.

### 5. Script lives at the end of `<body>`

We already placed `<script>` just before `</body>` in Step 02, so
by the time the script runs the DOM is fully parsed. No
`DOMContentLoaded` listener needed — we can call `loadTasks()` at
the top level.

### 6. IIFE wrapper or top-level?

We'll write the JS at top level inside `<script>`. No IIFE, no
module. The `<script>` tag is not `type="module"` and that's
deliberate — modules introduce CORS behavior for static file serving
that complicates local dev for zero benefit here.

All identifiers go on the global scope. For ~100 lines of code
that's fine.

## The five behaviors, precisely

### Load on open

```
loadTasks()  →  fetch('/tasks')  →  render
```

Called once at script bottom. Called again after every mutation.

### Create

`#create-form` submit handler:
1. `event.preventDefault()`.
2. Read `#title-input.value` and `#description-input.value`.
3. `api('/tasks', { method: 'POST', body: JSON.stringify({...}) })`.
4. Reset the form (clear inputs).
5. `loadTasks()`.

### Toggle complete

Checkbox `change` handler:
1. Read the new checked state.
2. `api('/tasks/{id}', { method: 'PUT', body: JSON.stringify({ completed }) })`.
3. `loadTasks()`.

### Edit

Edit button `click` handler:
1. Replace the title `<span>` with an `<input>` containing the
   current title.
2. Replace the description `<span>` with an `<input>` containing
   the current description.
3. Replace the Edit button with Save + Cancel buttons. Delete
   button and checkbox stay hidden or disabled during edit to
   avoid confusing state.
4. Save → PUT the new values and re-render.
5. Cancel → re-render (discarding input changes).

Edit mode is a per-`<li>` ephemeral state. We build it directly
from the click handler; no separate "edit state" variable lives
outside the DOM.

### Delete

Delete button `click` handler:
1. `api('/tasks/{id}', { method: 'DELETE' })`.
2. `loadTasks()`.

No confirmation dialog — the ticket doesn't require one and
`window.confirm()` is ugly. Users can always recreate.

## What we will NOT do

- No optimistic UI / no debouncing / no loading spinners.
- No error toast UI — errors go to `console.error`. Good enough
  for a learning app.
- No keyboard shortcut niceties.
- No undo.
- No sort or filter controls.
- No separate `.js` file.

## Exit criteria

Manual browser verification:

- Load page: list renders (empty or existing tasks, per DB state).
- Add a task: appears in list without refresh.
- Toggle checkbox: title + description get line-through styling.
- Click Edit on a task, change the title, click Save: the change
  persists after re-render.
- Click Edit, change fields, click Cancel: row reverts.
- Click Delete: row disappears.
- Reload the page: state matches the database (confirms every
  action actually hit the API, not just the local DOM).
- Browser console shows no errors.

Automated:

- `uv run pytest -v` → 10 passed (no app-code change in this step,
  still a sanity check).
