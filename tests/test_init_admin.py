from starlette.applications import Starlette
from starlette_admin import BaseAdmin
from starlette_admin_fields import StarletteAdminFields


def test_init_admin() -> None:
    app = Starlette()
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    admin.mount_to(app)
