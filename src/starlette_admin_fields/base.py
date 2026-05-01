from jinja2 import PackageLoader
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette_admin import BaseAdmin

PACKAGE_NAME = "starlette_admin_fields"
STATICS_ROUTE_NAME = "statics-saf"


class StarletteAdminFields:
    """
    Starlette Admin Fields.

    !!! note
        This class is just a placeholder for the documentation.
    """

    def __init__(self, admin: BaseAdmin | None = None) -> None:
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

        Idempotent: repeat calls on the same admin do not duplicate the
        package template loader nor remount the static-files route.

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
        loaders = admin.templates.env.loader.loaders  # type: ignore[union-attr]
        already_loaded = any(
            isinstance(loader, PackageLoader) and loader.package_name == PACKAGE_NAME
            for loader in loaders
        )
        if not already_loaded:
            loaders.append(PackageLoader(PACKAGE_NAME, "templates"))

        already_mounted = any(
            getattr(route, "name", None) == STATICS_ROUTE_NAME for route in admin.routes
        )
        if not already_mounted:
            admin.routes.append(
                Mount(
                    "/statics-saf",
                    app=StaticFiles(packages=[(PACKAGE_NAME, "statics")]),
                    name=STATICS_ROUTE_NAME,
                )
            )
