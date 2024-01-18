from dataclasses import dataclass
from typing import List, Union

from starlette.requests import Request
from starlette_admin._types import RequestAction
from starlette_admin.fields import PasswordField
from starlette_admin.helpers import html_params


@dataclass
class BootstrapShowPasswordField(PasswordField):
    """
    A PasswordField that provides a show/hide password toggle using the
    [Bootstrap Show Password](https://bootstrap-show-password.wenzhixin.net.cn/) library.

    Parameters:
        version: Bootstrap Show Password version
        placement: The placement of show/hide icon, can be 'before' or 'after'.
        message: The tooltip of show/hide icon.
        size: The size of the input group.
        eye_class: Base eye icon class.
        eye_open_class: Open eye icon class.
        eye_close_class: Close eye icon class.
        eye_class_position_inside: Puts the open/close class inside the <i>. Use this option with google material icons.
    """

    class_: str = "field-bootstrap-show-password form-control"
    version: str = "1.2.1"
    placement: str = "after"
    message: Union[str, bool] = "Click here to show/hide password"
    size: str = "md"
    eye_class: str = "fa"
    eye_open_class: str = "fa-eye"
    eye_close_class: str = "fa-eye-slash"
    eye_class_position_inside: bool = False

    def additional_js_links(self, request: Request, action: RequestAction) -> List[str]:
        if action.is_form():
            return [
                f"https://unpkg.com/bootstrap-show-password@{self.version}/dist/bootstrap-show-password.min.js",
            ]
        return []

    def input_params(self) -> str:
        return (
            super().input_params()
            + " "
            + html_params(
                {
                    "data-toggle": "password",
                    "data-placement": self.placement,
                    "data-message": self.message,
                    "data-size": self.size,
                    "data-eye-class": self.eye_class,
                    "data-eye-open-class": self.eye_open_class,
                    "data-eye-close-class": self.eye_close_class,
                    "data-eye-class-position-inside": self.eye_class_position_inside,
                }
            )
        )
