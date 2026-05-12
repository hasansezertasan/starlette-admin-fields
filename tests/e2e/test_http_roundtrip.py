"""HTTP round-trip e2e: create row via admin POST, assert persisted + detail 200."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from tests.e2e.app import KITCHEN_SINK_BASE, KitchenSink

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from starlette.applications import Starlette
    from starlette.testclient import TestClient


DEFAULTS: dict[str, str] = {
    "bootstrap_show_password": "p4ssword!",
    "ckeditor4": "<p>ck4 default</p>",
    "ckeditor5": "<p>ck5 default</p>",
    "simplemde": "# default",
}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("bootstrap_show_password", "s3cret-roundtrip"),
        ("ckeditor4", "<p>hello ck4</p>"),
        ("ckeditor5", "<p>hello ck5</p>"),
        ("simplemde", "# heading roundtrip"),
    ],
)
def test_create_then_persists_and_detail_renders(
    client: TestClient,
    app_and_engine: tuple[Starlette, Engine],
    field: str,
    value: str,
) -> None:
    _starlette_app, engine = app_and_engine

    payload = dict(DEFAULTS)
    payload[field] = value

    create_response = client.post(
        f"{KITCHEN_SINK_BASE}/create",
        data=payload,
        follow_redirects=False,
    )
    # starlette-admin redirects on successful create (302/303).
    assert create_response.status_code in (302, 303), (
        f"create failed: status={create_response.status_code} "
        f"body={create_response.text[:500]!r}"
    )

    with engine.connect() as conn:
        rows = conn.execute(select(KitchenSink)).all()
    assert len(rows) == 1, f"expected exactly 1 row, got {len(rows)}"
    persisted = rows[0]
    assert getattr(persisted, field) == value, (
        f"field={field!r} expected={value!r} got={getattr(persisted, field)!r}"
    )

    detail_response = client.get(f"{KITCHEN_SINK_BASE}/detail/{persisted.id}")
    assert detail_response.status_code == 200, (
        f"detail view failed: status={detail_response.status_code}"
    )
