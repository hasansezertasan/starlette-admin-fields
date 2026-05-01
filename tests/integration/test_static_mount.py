import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    ("path", "content_type_fragment", "body_marker"),
    [
        ("/admin/statics-saf/js/form-extra.js", "javascript", b"function"),
        ("/admin/statics-saf/css/ckeditor5.css", "text/css", b"{"),
    ],
)
def test_static_assets_served(
    client: TestClient,
    path: str,
    content_type_fragment: str,
    body_marker: bytes,
) -> None:
    response = client.get(path)
    assert response.status_code == 200
    assert content_type_fragment in response.headers["content-type"].lower()
    assert body_marker in response.content


def test_unknown_static_asset_returns_404(client: TestClient) -> None:
    response = client.get("/admin/statics-saf/does-not-exist.js")
    assert response.status_code == 404


def test_static_route_registered_by_name(client: TestClient) -> None:
    """The mounted Starlette route must be discoverable by the documented name."""
    statics_routes = [
        route
        for route in client.app.routes  # type: ignore[attr-defined]
        if getattr(route, "name", None) == "admin"
    ]
    assert statics_routes, "admin must be mounted on the host app"
