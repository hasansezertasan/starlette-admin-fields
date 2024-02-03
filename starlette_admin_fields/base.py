from typing import Optional

from jinja2 import PackageLoader
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette_admin import BaseAdmin


class StarletteAdminFields:
    """
    Starlette Admin Fields.

    !!! note
        This class is just a placeholder for the documentation.
    """

    def __init__(self, admin: Optional[BaseAdmin] = None) -> None:
        """
        Initialize Starlette Admin Fields.

        Parameters:
            admin: The admin instance.

        !!! usage
            ```python
            from starlette_admin import BaseAdmin
            from starlette_admin_fields import StarletteAdminFields

            admin = BaseAdmin()
            saf = StarletteAdminFields(admin)
            ```
        """
        if admin is not None:
            self.init_admin(admin)

    def init_admin(self, admin: BaseAdmin) -> None:
        """
        Initialize admin with extra templates and statics.

        Parameters:
            admin: The admin instance.

        !!! usage
            ```python
            from starlette_admin import BaseAdmin
            from starlette_admin_fields import StarletteAdminFields

            admin = BaseAdmin()
            saf = StarletteAdminFields()
            saf.init_admin(admin)
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
