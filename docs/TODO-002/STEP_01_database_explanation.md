# Step 1: app/database.py — Database Connection

## What we're about to write

A file that sets up the connection between our Python app and a SQLite database. It has 4 parts.

## Part-by-part breakdown

### 1. The Engine

```python
engine = create_engine("sqlite:///./todos.db", connect_args={"check_same_thread": False})
```

- `create_engine` is SQLAlchemy's starting point. You give it a URL, it gives you back an object that can open connections to that database.
- `sqlite:///./todos.db` means: use SQLite, store data in a file called `todos.db` in the current directory.
- `check_same_thread: False` — SQLite by default only allows the thread that created a connection to use it. FastAPI handles requests across multiple threads, so we disable this check. SQLAlchemy's connection pooling handles thread safety for us.

### 2. The Session Factory

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

- A **session** is a temporary workspace. You open one, make changes (insert/update/delete rows), then commit or rollback.
- `sessionmaker` creates a factory. Every time you call `SessionLocal()`, you get a new session.
- `autocommit=False` — changes are NOT saved automatically. You must call `db.commit()` explicitly. This gives you control over when changes become permanent.
- `autoflush=False` — SQLAlchemy won't send pending changes to the database until you explicitly commit. This avoids surprise queries mid-operation.
- `bind=engine` — tells every session created by this factory to use our SQLite engine.

### 3. The Base Class

```python
Base = declarative_base()
```

- Returns a class that our models will inherit from.
- When a model like `Task` inherits from `Base`, SQLAlchemy registers it internally. Later, when we call `Base.metadata.create_all()`, SQLAlchemy loops through all registered models and creates their tables.
- Think of `Base` as a registry — it keeps track of every model in our app.

### 4. The `get_db()` Dependency

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- This is a **generator function** (because of `yield`). FastAPI's dependency injection system uses it to provide a database session to route handlers.
- **How the lifecycle works:**
  1. FastAPI receives a request
  2. It calls `get_db()`, which creates a new session and `yield`s it
  3. The route handler receives the session, does its work
  4. After the response is sent (or if an error occurs), the `finally` block runs and closes the session
- **Why `try/finally`?** — If the route handler crashes, we still need to close the session. Without `finally`, a crash would leak an open database connection. Over time, leaked connections exhaust the pool and the app stops working.

## Why this file comes first

Models need `Base` to inherit from. `main.py` needs `engine` to create tables. Route handlers (future ticket) need `get_db()`. Everything starts here.
