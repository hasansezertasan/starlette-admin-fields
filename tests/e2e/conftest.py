"""E2E test fixtures: subprocess uvicorn, TestClient, auto-marker."""

from __future__ import annotations

import contextlib
import socket
import subprocess
import sys
import time
from typing import TYPE_CHECKING

import httpx
import pytest
from starlette.testclient import TestClient

from tests.e2e.app import make_app

if TYPE_CHECKING:
    from collections.abc import Iterator

    from sqlalchemy.engine import Engine
    from starlette.applications import Starlette


SERVER_READY_TIMEOUT_S = 15.0
SERVER_POLL_INTERVAL_S = 0.2
SERVER_SHUTDOWN_TIMEOUT_S = 5.0


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Auto-mark every test under ``tests/e2e/`` with ``@pytest.mark.e2e``."""
    e2e_marker = pytest.mark.e2e
    for item in items:
        if "tests/e2e/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(e2e_marker)


@pytest.fixture(scope="session")
def free_port() -> int:
    """Bind to port 0 then release it — race-safe enough for local + CI."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="session")
def uvicorn_server(free_port: int) -> Iterator[str]:
    """Boot ``tests.e2e.app:app`` under uvicorn in a subprocess.

    Yields the base URL. Tears down with terminate → kill.
    """
    proc = subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-m",
            "uvicorn",
            "tests.e2e.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(free_port),
            "--log-level",
            "warning",
        ],
    )

    base_url = f"http://127.0.0.1:{free_port}"
    deadline = time.monotonic() + SERVER_READY_TIMEOUT_S
    while time.monotonic() < deadline:
        try:
            response = httpx.get(f"{base_url}/admin/", timeout=1.0)
        except httpx.HTTPError:
            time.sleep(SERVER_POLL_INTERVAL_S)
            continue
        if response.status_code < 500:
            break
        time.sleep(SERVER_POLL_INTERVAL_S)
    else:
        proc.kill()
        proc.wait()
        msg = f"uvicorn did not become ready at {base_url} within {SERVER_READY_TIMEOUT_S}s"
        raise RuntimeError(msg)

    try:
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=SERVER_SHUTDOWN_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@pytest.fixture
def base_url(uvicorn_server: str) -> str:
    """Alias used by pytest-playwright's ``page.goto`` callers."""
    return uvicorn_server


@pytest.fixture
def app_and_engine() -> tuple[Starlette, Engine]:
    """Fresh in-process app + engine pair for HTTP round-trip tests."""
    return make_app()


@pytest.fixture
def client(
    app_and_engine: tuple[Starlette, Engine],
) -> Iterator[TestClient]:
    """In-process TestClient backed by a fresh in-memory SQLite engine."""
    starlette_app, _engine = app_and_engine
    with TestClient(starlette_app) as test_client:
        yield test_client
