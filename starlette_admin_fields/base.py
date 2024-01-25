from jinja2 import PackageLoader
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette_admin import BaseAdmin


def extend_admin(admin: BaseAdmin) -> None:
    """
    Extend admin with extra templates and statics.

    Parameters:
        admin: The admin instance.

    !!! usage
        ```python
        from starlette_admin_fields import extend_admin

        extend_admin(admin)
        ```
    """
    admin.templates.env.loader.loaders.append(  # type: ignore
        PackageLoader("starlette_admin_fields", "templates")
    )
    admin.routes.append(
        Mount(
            "/statics-saf",
            app=StaticFiles(packages=[("starlette_admin_fields", "statics")]),
            name="statics-saf",
        )
    )
