from jinja2 import PackageLoader
from starlette_admin import BaseAdmin
from starlette_admin_fields import StarletteAdminFields
from starlette_admin_fields.base import PACKAGE_NAME, STATICS_ROUTE_NAME


def _package_loaders(admin: BaseAdmin) -> list[PackageLoader]:
    loader = admin.templates.env.loader
    inner = getattr(loader, "loaders", [])
    return [item for item in inner if isinstance(item, PackageLoader)]


def _saf_loaders(admin: BaseAdmin) -> list[PackageLoader]:
    return [ldr for ldr in _package_loaders(admin) if ldr.package_name == PACKAGE_NAME]


def _saf_static_routes(admin: BaseAdmin) -> list:
    return [r for r in admin.routes if getattr(r, "name", "") == STATICS_ROUTE_NAME]


def test_package_loader_registered() -> None:
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    assert len(_saf_loaders(admin)) == 1


def test_package_loader_resolves_templates_directory() -> None:
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    [ldr] = _saf_loaders(admin)
    assert ldr.package_path == "templates"


def test_init_admin_is_idempotent_on_routes() -> None:
    """Repeat calls must not duplicate the static mount."""
    admin = BaseAdmin()
    saf = StarletteAdminFields()
    saf.init_admin(admin)
    saf.init_admin(admin)
    saf.init_admin(admin)
    assert len(_saf_static_routes(admin)) == 1


def test_init_admin_is_idempotent_on_template_loader() -> None:
    """Repeat calls must not duplicate the package template loader."""
    admin = BaseAdmin()
    saf = StarletteAdminFields()
    saf.init_admin(admin)
    saf.init_admin(admin)
    assert len(_saf_loaders(admin)) == 1


def test_two_instances_share_single_registration() -> None:
    """Two SAF instances on one admin must still register only one mount."""
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    StarletteAdminFields(admin)
    assert len(_saf_static_routes(admin)) == 1


def test_init_admin_idempotent_across_constructor_and_method() -> None:
    """Constructor-init then explicit init_admin call must not duplicate either side."""
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    deferred = StarletteAdminFields()
    deferred.init_admin(admin)
    assert len(_saf_static_routes(admin)) == 1
    assert len(_saf_loaders(admin)) == 1
