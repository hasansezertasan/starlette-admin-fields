import json
from unittest.mock import MagicMock

from starlette_admin._types import RequestAction
from starlette_admin_fields import CKEditor4Field


def _data_options(rendered: str) -> dict:
    """Extract and parse the data-options JSON blob from rendered input_params."""
    marker = 'data-options="'
    start = rendered.index(marker) + len(marker)
    end = rendered.index('"', start)
    return json.loads(rendered[start:end].replace("&#34;", '"'))


def test_defaults() -> None:
    f = CKEditor4Field(name="body")
    assert f.class_ == "field-ckeditor4 form-control"
    assert f.distribution == "standard"
    assert f.height == 300
    assert f.extra_options == {}


def test_input_params_includes_height() -> None:
    f = CKEditor4Field(name="body")
    options = _data_options(f.input_params())
    assert options == {"height": 300}


def test_extra_options_merged() -> None:
    f = CKEditor4Field(
        name="body",
        height=500,
        extra_options={"toolbar": "Basic", "language": "en"},
    )
    options = _data_options(f.input_params())
    assert options == {"height": 500, "toolbar": "Basic", "language": "en"}


def test_extra_options_overrides_height() -> None:
    """`extra_options` is unpacked AFTER `height`, so a key in extra_options wins.

    Documents current behavior — flip this test if the merge order changes.
    """
    f = CKEditor4Field(name="body", height=400, extra_options={"height": 999})
    options = _data_options(f.input_params())
    assert options["height"] == 999


def test_additional_js_links_only_on_form_action() -> None:
    f = CKEditor4Field(name="body", version="4.22.1")
    request = MagicMock()
    request.url_for.return_value = "http://test/admin/statics-saf/js/form-extra.js"
    request.app.state.ROUTE_NAME = "admin"

    form_links = f.additional_js_links(request, RequestAction.EDIT)
    assert len(form_links) == 2
    assert "cdn.ckeditor.com/4.22.1/standard/ckeditor.js" in form_links[0]

    assert f.additional_js_links(request, RequestAction.LIST) == []
