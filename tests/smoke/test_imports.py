from starlette_admin.fields import PasswordField, TextAreaField
from starlette_admin_fields import (
    BootstrapShowPasswordField,
    CKEditor4Field,
    CKEditor5Field,
    SimpleMDEField,
    StarletteAdminFields,
)


def test_public_api_exposes_main_class() -> None:
    assert StarletteAdminFields.__name__ == "StarletteAdminFields"


def test_password_field_inherits_password() -> None:
    assert issubclass(BootstrapShowPasswordField, PasswordField)


def test_editor_fields_inherit_textarea() -> None:
    for cls in (CKEditor4Field, CKEditor5Field, SimpleMDEField):
        assert issubclass(cls, TextAreaField)
