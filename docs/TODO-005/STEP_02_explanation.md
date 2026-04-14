# TODO-005 · Step 02 — HTML structure + CSS

## Goal of this step

Build the static skeleton of the UI: the markup the user will see
and the styling that makes it readable. After this step:

- `static/index.html` is a complete, valid HTML document.
- Opening `http://localhost:8000/` renders a heading, a "create
  task" form, and a (currently empty) task list, all readably
  styled.
- No JavaScript runs yet — the form will not submit usefully and
  the list will stay empty. That's expected; behavior comes in
  Step 03.

## Why split structure from behavior

When something looks broken in a UI, the first question is "is the
markup wrong, the CSS wrong, or the JS wrong?" If we ship the markup
+ CSS first and visually verify it, then any breakage after Step 03
is by elimination a JavaScript issue. This shortens debugging cycles
considerably for very little upfront cost.

## Why a single self-contained `index.html`

The acceptance criteria ask for `static/index.html` and call out
"plain HTML, CSS, and vanilla JavaScript. No frameworks." Splitting
into separate `.css` and `.js` files would be reasonable on a larger
project but adds friction here:

- More HTTP requests on page load.
- More files to keep in sync.
- The `/static` mount works the same way for any number of files,
  but for ~150 lines total there's nothing to organize.

If the file grows past ~300 lines later we can split. For now,
inline `<style>` and inline `<script>` is the simplest thing that
satisfies the requirements.

## The HTML structure

Top to bottom, the document will contain:

1. `<!doctype html>` and a normal `<html>/<head>/<body>` skeleton.
2. `<head>`: `<meta charset>`, `<meta viewport>` (so it's not tiny
   on a phone), `<title>Todos</title>`, and the inline `<style>`.
3. `<body>`:
   - `<main class="container">` wrapper for centering and
     max-width.
   - `<h1>Todos</h1>`.
   - `<form id="create-form">` with:
     - `<input id="title-input" name="title" required>` for the
       title (HTML5 `required` gives us a free client-side check
       for the empty case before we even hit the API).
     - `<input id="description-input" name="description">` for the
       description.
     - `<button type="submit">Add</button>`.
   - `<ul id="task-list"></ul>` — empty container the JS will
     populate.
   - An empty `<script></script>` at the end of `<body>` so the
     DOM is fully parsed before JS runs (no `DOMContentLoaded`
     listener needed).

The `id` attributes are deliberate: the JS in Step 03 needs stable
hooks to find these elements without a query-selector zoo.

### Why `<ul>` and not `<div>`s

Each task is conceptually a list item, so `<ul><li>` is the
semantic fit. Screen readers announce list length and position,
which beats a wall of generic `<div>`s.

### Per-task `<li>` shape (JS will produce this in Step 03)

Mentioned here because the CSS styles it:

```html
<li class="task" data-id="{id}">
  <input type="checkbox" class="task-toggle">
  <span class="task-title">…</span>
  <span class="task-description">…</span>
  <button class="task-edit">Edit</button>
  <button class="task-delete">Delete</button>
</li>
```

The CSS in this step targets these classes so that when Step 03
generates them, the styling is already in place.

## The CSS

Goals:

- Readable, not pretty.
- No layout libraries, no resets — just enough to make the page
  not look broken.
- Visual distinction for completed tasks (faded text + line-through)
  via a `.task.completed` modifier class.

Roughly:

```css
body { font-family: system-ui, sans-serif; margin: 0;
       background: #f6f7f9; color: #222; }
.container { max-width: 640px; margin: 2rem auto; padding: 1rem; }
h1 { margin-top: 0; }
form { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
form input { flex: 1; padding: 0.5rem; }
form button { padding: 0.5rem 1rem; cursor: pointer; }
ul { list-style: none; padding: 0; margin: 0; }
.task { display: flex; align-items: center; gap: 0.5rem;
        padding: 0.5rem; border-bottom: 1px solid #e0e0e0; }
.task-title { font-weight: 600; }
.task-description { color: #666; flex: 1; }
.task.completed .task-title,
.task.completed .task-description {
  text-decoration: line-through; opacity: 0.6;
}
button { background: #fff; border: 1px solid #ccc;
         border-radius: 4px; padding: 0.25rem 0.5rem;
         cursor: pointer; }
button:hover { background: #f0f0f0; }
```

`system-ui` font keeps it native-looking on every OS without
shipping a webfont.

`flex` on `.task` puts checkbox + title + description + buttons in
one row that wraps gracefully if the description is long.

## What this step does NOT do

- No JavaScript logic. The `<script>` tag exists and is empty.
- No fetch calls, no DOM construction, no event listeners.
- No backend changes.
- No `static/index.css` or `static/app.js` files — everything stays
  in `index.html`.

## Exit criteria

- `static/index.html` is a valid HTML document with `<form>`,
  `<ul id="task-list">`, inline `<style>`, and an empty `<script>`.
- `uv run uvicorn app.main:app --reload`, then `curl
  http://localhost:8000/` returns a non-empty HTML body containing
  `<form id="create-form"`.
- Manually opening the page in a browser shows: a heading, the
  form, and an empty list area, with sensible spacing and fonts.
- No console errors in the browser dev tools.
- `uv run pytest -v` still passes (sanity check — this step doesn't
  touch app code, so this is just paranoia).
