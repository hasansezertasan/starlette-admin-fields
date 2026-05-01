from unittest.mock import MagicMock

from starlette_admin._types import RequestAction
from starlette_admin_fields import BootstrapShowPasswordField


def test_defaults() -> None:
    f = BootstrapShowPasswordField(name="pw")
    assert f.class_ == "field-bootstrap-show-password form-control"
    assert f.placement == "after"
    assert f.size == "md"
    assert f.eye_class == "fa"
    assert f.eye_open_class == "fa-eye"
    assert f.eye_close_class == "fa-eye-slash"
    assert f.eye_class_position_inside is False


def test_input_params_includes_data_attrs() -> None:
    f = BootstrapShowPasswordField(name="pw")
    rendered = f.input_params()
    for token in (
        'data-toggle="password"',
        'data-placement="after"',
        'data-size="md"',
        'data-eye-class="fa"',
        'data-eye-open-class="fa-eye"',
        'data-eye-close-class="fa-eye-slash"',
    ):
        assert token in rendered


def test_input_params_reflects_overrides() -> None:
    f = BootstrapShowPasswordField(
        name="pw",
        placement="before",
        size="lg",
        eye_class="material-icons",
    )
    rendered = f.input_params()
    assert 'data-placement="before"' in rendered
    assert 'data-size="lg"' in rendered
    assert 'data-eye-class="material-icons"' in rendered


def test_additional_js_links_only_on_form_action() -> None:
    f = BootstrapShowPasswordField(name="pw", version="1.2.1")
    request = MagicMock()
    form_links = f.additional_js_links(request, RequestAction.EDIT)
    assert len(form_links) == 1
    assert "bootstrap-show-password@1.2.1" in form_links[0]
    assert f.additional_js_links(request, RequestAction.LIST) == []
    assert f.additional_js_links(request, RequestAction.DETAIL) == []


def test_custom_version_in_cdn_link() -> None:
    f = BootstrapShowPasswordField(name="pw", version="9.9.9")
    [link] = f.additional_js_links(MagicMock(), RequestAction.CREATE)
    assert "bootstrap-show-password@9.9.9" in link
