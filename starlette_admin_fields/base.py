from jinja2 import PackageLoader
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette_admin import BaseAdmin


def extend_admin(admin: BaseAdmin) -> None:
    """
    Extend admin with extra templates and statics.

    Parameters:
        admin: The admin instance.

    Usage:
        ```python
        from starlette_admin_fields import extend_admin

        extend_admin(admin)
        ```
    """
    # Validate templates
    admin.templates.env.loader.loaders.append(
        PackageLoader("starlette_admin_fields", "templates")
    )
    # Validate statics by navigating to /admin/statics-saf/js/form-extra.js
    admin.routes.append(
        Mount(
            "/statics-saf",
            app=StaticFiles(packages=[("starlette_admin_fields", "statics")]),
            name="statics-saf",
        )
    )
