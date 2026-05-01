from jinja2 import PackageLoader
from starlette_admin import BaseAdmin
from starlette_admin_fields import StarletteAdminFields


def _package_loaders(admin: BaseAdmin) -> list[PackageLoader]:
    loader = admin.templates.env.loader
    inner = getattr(loader, "loaders", [])
    return [item for item in inner if isinstance(item, PackageLoader)]


def test_package_loader_registered() -> None:
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    matching = [
        ldr
        for ldr in _package_loaders(admin)
        if ldr.package_name == "starlette_admin_fields"
    ]
    assert len(matching) == 1


def test_package_loader_resolves_templates_directory() -> None:
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    [ldr] = [
        ldr
        for ldr in _package_loaders(admin)
        if ldr.package_name == "starlette_admin_fields"
    ]
    assert ldr.package_path == "templates"


def test_init_admin_is_idempotent_on_routes() -> None:
    """Repeat calls must not duplicate the static mount."""
    admin = BaseAdmin()
    saf = StarletteAdminFields()
    saf.init_admin(admin)
    saf.init_admin(admin)
    saf.init_admin(admin)
    statics = [r for r in admin.routes if getattr(r, "name", "") == "statics-saf"]
    assert len(statics) == 1


def test_init_admin_is_idempotent_on_template_loader() -> None:
    """Repeat calls must not duplicate the package template loader."""
    admin = BaseAdmin()
    saf = StarletteAdminFields()
    saf.init_admin(admin)
    saf.init_admin(admin)
    matching = [
        ldr
        for ldr in _package_loaders(admin)
        if ldr.package_name == "starlette_admin_fields"
    ]
    assert len(matching) == 1


def test_two_instances_share_single_registration() -> None:
    """Two SAF instances on one admin must still register only one mount."""
    admin = BaseAdmin()
    StarletteAdminFields(admin)
    StarletteAdminFields(admin)
    statics = [r for r in admin.routes if getattr(r, "name", "") == "statics-saf"]
    assert len(statics) == 1
