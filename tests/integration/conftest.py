import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from starlette_admin import BaseAdmin
from starlette_admin_fields import StarletteAdminFields


@pytest.fixture()
def admin() -> BaseAdmin:
    instance = BaseAdmin()
    StarletteAdminFields(instance)
    return instance


@pytest.fixture()
def client(admin: BaseAdmin) -> TestClient:
    app = Starlette()
    admin.mount_to(app)
    return TestClient(app)
