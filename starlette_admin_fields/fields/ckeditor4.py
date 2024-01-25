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

    This field can be used as an alternative to the TextAreaField to provide
    a more sophisticated editor for user input.

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
                str(
                    request.url_for(
                        f"{request.app.state.ROUTE_NAME}:statics-saf",
                        path="js/form-extra.js",
                    )
                ),
            ]
        return []

    def input_params(self) -> str:
        _options = {
            "height": self.height,
            **self.extra_options,
        }
        return (
            super().input_params()
            + " "
            + html_params({"data-options": json.dumps(_options)})
        )
