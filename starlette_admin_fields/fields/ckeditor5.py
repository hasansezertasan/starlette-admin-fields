from dataclasses import dataclass
from typing import List

from starlette.requests import Request
from starlette_admin._types import RequestAction
from starlette_admin.fields import TextAreaField


@dataclass
class CKEditor5Field(TextAreaField):
    """A field that provides a WYSIWYG editor for long text content using the
    [CKEditor5](https://ckeditor.com/) library.

    This field can be used as an alternative to the TextAreaField to provide
    a more sophisticated editor for user input.
    """

    class_: str = "field-ckeditor5 form-control"
    display_template: str = "displays/tinymce.html"
    version: str = "40.0.0"
    distribution: str = "classic"

    def additional_js_links(self, request: Request, action: RequestAction) -> List[str]:
        if action.is_form():
            return [
                f"https://cdn.ckeditor.com/ckeditor5/{self.version}/{self.distribution}/ckeditor.js",
                str(
                    request.url_for(
                        f"{request.app.state.ROUTE_NAME}:statics-saf",
                        path="js/form-extra.js",
                    )
                ),
            ]
        return []

    def additional_css_links(
        self, request: Request, action: RequestAction
    ) -> List[str]:
        if action.is_form():
            return [
                str(
                    request.url_for(
                        f"{request.app.state.ROUTE_NAME}:statics-saf",
                        path="css/ckeditor5.css",
                    )
                )
            ]
        return []
