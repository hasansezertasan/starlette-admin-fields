import json
from unittest.mock import MagicMock

from starlette_admin._types import RequestAction
from starlette_admin_fields import SimpleMDEField


def _data_options(rendered: str) -> dict:
    marker = 'data-options="'
    start = rendered.index(marker) + len(marker)
    end = rendered.index('"', start)
    return json.loads(rendered[start:end].replace("&#34;", '"'))


def test_defaults() -> None:
    f = SimpleMDEField(name="body")
    assert f.class_ == "field-simplemde form-control"
    assert f.spell_checker is False
    assert f.status is False
    assert f.autofocus is True
    assert f.hide_icons == []
    assert f.extra_options == {}


def test_input_params_default_options() -> None:
    f = SimpleMDEField(name="body")
    options = _data_options(f.input_params())
    assert options == {
        "placeholder": "",
        "spellChecker": False,
        "status": False,
        "hideIcons": [],
        "autofocus": True,
    }


def test_input_params_with_overrides() -> None:
    f = SimpleMDEField(
        name="body",
        placeholder="Type here…",
        spell_checker=True,
        status=True,
        hide_icons=["guide", "fullscreen"],
        autofocus=False,
    )
    options = _data_options(f.input_params())
    assert options["placeholder"] == "Type here…"
    assert options["spellChecker"] is True
    assert options["status"] is True
    assert options["hideIcons"] == ["guide", "fullscreen"]
    assert options["autofocus"] is False


def test_extra_options_merged() -> None:
    f = SimpleMDEField(name="body", extra_options={"toolbar": ["bold", "italic"]})
    options = _data_options(f.input_params())
    assert options["toolbar"] == ["bold", "italic"]


def test_additional_js_links_form_action() -> None:
    f = SimpleMDEField(name="body", version="1.11.2")
    request = MagicMock()
    request.url_for.return_value = "http://test/admin/statics-saf/js/form-extra.js"
    request.app.state.ROUTE_NAME = "admin"

    form_links = f.additional_js_links(request, RequestAction.EDIT)
    assert len(form_links) == 2
    assert "simplemde@1.11.2/dist/simplemde.min.js" in form_links[0]


def test_additional_js_links_skip_non_form() -> None:
    f = SimpleMDEField(name="body")
    assert f.additional_js_links(MagicMock(), RequestAction.LIST) == []


def test_additional_css_links_form_action() -> None:
    f = SimpleMDEField(name="body", version="1.11.2")
    [link] = f.additional_css_links(MagicMock(), RequestAction.CREATE)
    assert "simplemde@1.11.2/dist/simplemde.min.css" in link


def test_additional_css_links_skip_non_form() -> None:
    f = SimpleMDEField(name="body")
    assert f.additional_css_links(MagicMock(), RequestAction.LIST) == []
