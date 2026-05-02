from unittest.mock import MagicMock

from starlette_admin._types import RequestAction
from starlette_admin_fields import CKEditor5Field


def test_defaults() -> None:
    f = CKEditor5Field(name="body")
    assert f.class_ == "field-ckeditor5 form-control"
    assert f.version == "40.0.0"
    assert f.distribution == "classic"


def test_additional_js_links_form_action() -> None:
    f = CKEditor5Field(name="body", version="40.0.0", distribution="classic")
    request = MagicMock()
    request.url_for.return_value = "http://test/admin/statics-saf/js/form-extra.js"
    request.app.state.ROUTE_NAME = "admin"

    form_links = f.additional_js_links(request, RequestAction.EDIT)
    assert len(form_links) == 2
    assert "cdn.ckeditor.com/ckeditor5/40.0.0/classic/ckeditor.js" in form_links[0]


def test_additional_js_links_skip_non_form() -> None:
    f = CKEditor5Field(name="body")
    request = MagicMock()
    assert f.additional_js_links(request, RequestAction.LIST) == []
    assert f.additional_js_links(request, RequestAction.DETAIL) == []


def test_additional_css_links_form_action() -> None:
    f = CKEditor5Field(name="body")
    request = MagicMock()
    request.url_for.return_value = "http://test/admin/statics-saf/css/ckeditor5.css"
    request.app.state.ROUTE_NAME = "admin"

    css_links = f.additional_css_links(request, RequestAction.EDIT)
    assert css_links == [str(request.url_for.return_value)]
    request.url_for.assert_called_with("admin:statics-saf", path="css/ckeditor5.css")


def test_additional_css_links_skip_non_form() -> None:
    f = CKEditor5Field(name="body")
    request = MagicMock()
    assert f.additional_css_links(request, RequestAction.LIST) == []
