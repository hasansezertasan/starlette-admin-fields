"""Module-level Starlette app for the uvicorn subprocess fixture.

Kept separate from app.py so importing app.py (for KitchenSink, KITCHEN_SINK_BASE,
make_app) does not trigger a side-effectful engine creation at import time.
"""

from __future__ import annotations

from tests.e2e.app import make_app

app, _engine = make_app()
# _engine is kept at module scope intentionally: it owns the in-memory SQLite
# connection pool.  Losing the last reference would destroy the database and
# break all subsequent requests served by this process.
