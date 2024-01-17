import json
from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Any, Dict, List, Union

from starlette.requests import Request
from starlette_admin._types import RequestAction
from starlette_admin.fields import TextAreaField
from starlette_admin.helpers import html_params


@dataclass
class CKEditor4Field(TextAreaField):
    """A field that provides a WYSIWYG editor for long text content using the
     [CKEditor4](https://ckeditor.com/) library.
    This field can be used as an alternative to the [TextAreaField][starlette_admin.fields.TextAreaField]
    to provide a more sophisticated editor for user input.
    Parameters:
        version: CKEditor4 version
        distribution: CKEditor4 distribution
        height: Editor height
        extra_options: Other options to pass to SimpleMDE
    """

    class_: str = "field-ckeditor4 form-control"
    display_template: str = "displays/tinymce.html"
    version: str = "4.22.1"
    distribution: str = "standard"

    height: Union[int, str] = 300
    extra_options: Dict[str, Any] = dc_field(default_factory=dict)
    """For more options, see the [CKEditor 4 API docs](https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_config.html)"""

    def additional_js_links(self, request: Request, action: RequestAction) -> List[str]:
        if action.is_form():
            return [
                f"https://cdn.ckeditor.com/{self.version}/{self.distribution}/ckeditor.js",
                str(request.url_for(f"{request.app.state.ROUTE_NAME}:statics", path="js/form-extra.js")),
            ]
        return []

    def input_params(self) -> str:
        _options = {
            "height": self.height,
            **self.extra_options,
        }
        return super().input_params() + " " + html_params({"data-options": json.dumps(_options)})


@dataclass
class CKEditor5Field(TextAreaField):
    """A field that provides a WYSIWYG editor for long text content using the
     [CKEditor5](https://ckeditor.com/) library.

    This field can be used as an alternative to the [TextAreaField][starlette_admin.fields.TextAreaField]
    to provide a more sophisticated editor for user input.
    """

    class_: str = "field-ckeditor5 form-control"
    display_template: str = "displays/tinymce.html"
    version: str = "40.0.0"
    distribution: str = "classic"

    def additional_js_links(self, request: Request, action: RequestAction) -> List[str]:
        if action.is_form():
            return [
                f"https://cdn.ckeditor.com/ckeditor5/{self.version}/{self.distribution}/ckeditor.js",
                str(request.url_for(f"{request.app.state.ROUTE_NAME}:statics", path="js/form-extra.js")),
            ]
        return []

    def additional_css_links(self, request: Request, action: RequestAction) -> List[str]:
        if action.is_form():
            return [str(request.url_for(f"{request.app.state.ROUTE_NAME}:statics", path="css/ckeditor5.css"))]
        return []


@dataclass
class SimpleMDEField(TextAreaField):
    """A field that provides a Markdown editor for long text content using the
    [SimpleMDE](https://simplemde.com/) library.
    This field can be used as an alternative to the [TextAreaField][starlette_admin.fields.TextAreaField]
    to provide a more sophisticated editor for user input.
    Parameters:
        version: SimpleMDE version
        spell_checker: Enable spell checker
        status: Show status bar at the bottom
        hide_icons: Hide icons from toolbar
        autofocus: Enable autofocus
        extra_options: Other options to pass to SimpleMDE
    """

    class_: str = "field-simplemde form-control"
    display_template: str = "displays/tinymce.html"
    version: str = "1.11.2"
    placeholder: str = ""
    spell_checker: bool = False
    status: bool = False
    hide_icons: List[str] = dc_field(default_factory=list)
    autofocus: bool = True
    extra_options: Dict[str, Any] = dc_field(default_factory=dict)
    """For more options, see the [SimpleMDE](https://simplemde.com/)"""

    def additional_js_links(self, request: Request, action: RequestAction) -> List[str]:
        if action.is_form():
            return [
                f"https://cdn.jsdelivr.net/npm/simplemde@{self.version}/dist/simplemde.min.js",
                str(request.url_for(f"{request.app.state.ROUTE_NAME}:statics", path="js/form-extra.js")),
            ]
        return []

    def additional_css_links(self, request: Request, action: RequestAction) -> List[str]:
        if action.is_form():
            return [
                f"https://cdn.jsdelivr.net/npm/simplemde@{self.version}/dist/simplemde.min.css",
            ]
        return []

    def input_params(self) -> str:
        _options = {
            "placeholder": self.placeholder,
            "spellChecker": self.spell_checker,
            "status": self.status,
            "hideIcons": self.hide_icons,
            "autofocus": self.autofocus,
            **self.extra_options,
        }

        return super().input_params() + " " + html_params({"data-options": json.dumps(_options)})
