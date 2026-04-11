# Step 2: app/models.py — The Task Model

## What we're about to write

A single class `Task` that maps to a `tasks` table in SQLite. It inherits from the `Base` class we created in Step 1.

## Part-by-part breakdown

### 1. The class and table name

```python
class Task(Base):
    __tablename__ = "tasks"
```

- Inheriting from `Base` registers this model with SQLAlchemy's metadata. That's how `Base.metadata.create_all()` (which we'll call in main.py) knows to create this table.
- `__tablename__` is a special SQLAlchemy attribute — it sets the actual SQL table name. Without it, SQLAlchemy would try to infer one, but being explicit is clearer.

### 2. The `id` column

```python
id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
```

- `Mapped[int]` — this is SQLAlchemy 2.0 style. It combines a Python type hint with the column definition. Your IDE and type checker know this is an `int`.
- `primary_key=True` — every table needs a primary key. SQLite auto-increments integer primary keys by default, so we don't need to specify `autoincrement`.
- `index=True` — creates a database index for fast lookups. Primary keys are indexed automatically in most databases, but being explicit doesn't hurt.

### 3. The `title` column

```python
title: Mapped[str] = mapped_column(String, nullable=False)
```

- `nullable=False` — the database will reject any insert that doesn't include a title. This is a database-level constraint, not just a Python check. Even if someone bypasses our API and writes SQL directly, the constraint holds.

### 4. The `description` column

```python
description: Mapped[str | None] = mapped_column(String, nullable=True)
```

- `Mapped[str | None]` — the type hint tells Python this can be `None`.
- `nullable=True` — the database allows this column to be empty. Not every task needs a description.

### 5. The `completed` column

```python
completed: Mapped[bool] = mapped_column(Boolean, default=False)
```

- `default=False` — when you create a `Task()` without specifying `completed`, SQLAlchemy inserts `False`. This is a Python-side default (SQLAlchemy sets it before sending the INSERT to the DB).

### 6. The `created_at` column

```python
created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

- `server_default=func.now()` — this is a **database-side** default. The SQL itself contains `DEFAULT CURRENT_TIMESTAMP`. The database generates the value, not Python.
- Why server-side? If you have multiple app servers, each might have slightly different clocks. The database clock is the single source of truth.

### 7. The `updated_at` column

```python
updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

- Same `server_default` as `created_at` — gets set when the row is first inserted.
- `onupdate=func.now()` — this is the key difference. Every time SQLAlchemy issues an UPDATE statement for this row, it automatically sets `updated_at` to the current time. You never have to remember to update it manually in your route handlers.

## Why `Mapped[]` + `mapped_column()` instead of plain `Column()`?

SQLAlchemy 2.0 introduced this style. The old way (`id = Column(Integer, ...)`) still works but gives you no type information. With `Mapped[int]`, your editor knows `task.id` is an `int`, gives you autocomplete, and catches type errors. It's the recommended approach going forward.

## How this connects to Step 1

- We import `Base` from `database.py` — that's the registry.
- When `Task(Base)` is defined, SQLAlchemy adds `tasks` to `Base.metadata.tables`.
- Later in `main.py`, calling `Base.metadata.create_all(engine)` will read this metadata and create the table.
