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
        ("bootstrap_show_password", "p4$$w0rd!@#$%^*()"),
        ("ckeditor4", "<p>hello ck4</p>"),
        ("ckeditor4", "<p>a &amp; b &lt;em&gt;</p>"),
        ("ckeditor5", "<p>hello ck5</p>"),
        ("simplemde", "# heading roundtrip"),
        ("simplemde", "# heading\n\ncontent with 'single' and \"double\" quotes"),
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
    assert len(rows) == 1, (
        f"expected exactly 1 row (fresh in-memory DB per test), got {len(rows)}. "
        "If app_and_engine fixture scope changes to session, update this assertion."
    )
    persisted = rows[0]
    assert getattr(persisted, field) == value, (
        f"field={field!r} expected={value!r} got={getattr(persisted, field)!r}"
    )

    detail_response = client.get(f"{KITCHEN_SINK_BASE}/detail/{persisted.id}")
    assert detail_response.status_code == 200, (
        f"detail view failed: status={detail_response.status_code}"
    )
    assert value in detail_response.text, (
        f"field={field!r} value={value!r} not found in detail response body"
    )


def test_edit_persists_and_detail_renders(
    client: TestClient,
    app_and_engine: tuple[Starlette, Engine],
) -> None:
    _app, engine = app_and_engine

    create_resp = client.post(
        f"{KITCHEN_SINK_BASE}/create",
        data=DEFAULTS,
        follow_redirects=False,
    )
    assert create_resp.status_code in (302, 303), (
        f"create failed: {create_resp.status_code} {create_resp.text[:200]!r}"
    )

    with engine.connect() as conn:
        rows = conn.execute(select(KitchenSink)).all()
    assert len(rows) == 1
    row_id = rows[0].id

    updated_value = "<p>updated via edit</p>"
    payload = dict(DEFAULTS)
    payload["ckeditor4"] = updated_value

    edit_resp = client.post(
        f"{KITCHEN_SINK_BASE}/edit/{row_id}",
        data=payload,
        follow_redirects=False,
    )
    assert edit_resp.status_code in (302, 303), (
        f"edit failed: status={edit_resp.status_code} body={edit_resp.text[:500]!r}"
    )

    with engine.connect() as conn:
        rows = conn.execute(select(KitchenSink)).all()
    assert len(rows) == 1, "edit must not create a new row"
    assert rows[0].ckeditor4 == updated_value, (
        f"edit did not persist: expected={updated_value!r} got={rows[0].ckeditor4!r}"
    )

    detail_resp = client.get(f"{KITCHEN_SINK_BASE}/detail/{row_id}")
    assert detail_resp.status_code == 200
    assert updated_value in detail_resp.text, "updated value not found in detail view"
