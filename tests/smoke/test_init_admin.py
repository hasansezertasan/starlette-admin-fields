from starlette.applications import Starlette
from starlette_admin import BaseAdmin
from starlette_admin_fields import StarletteAdminFields


def test_init_admin() -> None:
    app = Starlette()
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    admin.mount_to(app)


def test_init_admin_deferred() -> None:
    app = Starlette()
    admin = BaseAdmin()
    saf = StarletteAdminFields()
    saf.init_admin(admin)
    admin.mount_to(app)
