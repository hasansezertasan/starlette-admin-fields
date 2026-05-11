"""Browser render-smoke: each field's widget mounts on the create page."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


def _ckeditor4_locator(page: Page) -> Locator:
    return page.locator("iframe.cke_wysiwyg_frame")


def _ckeditor5_locator(page: Page) -> Locator:
    return page.locator("div.ck-editor__editable")


def _simplemde_locator(page: Page) -> Locator:
    return page.locator("div.CodeMirror")


def _bootstrap_show_password_locator(page: Page) -> Locator:
    # The password input itself; the toggle button mounts adjacent to it.
    return page.locator('input[name="bootstrap_show_password"]')


FIELD_LOCATORS = {
    "ckeditor4": _ckeditor4_locator,
    "ckeditor5": _ckeditor5_locator,
    "simplemde": _simplemde_locator,
    "bootstrap_show_password": _bootstrap_show_password_locator,
}


@pytest.mark.parametrize("field", list(FIELD_LOCATORS))
def test_field_widget_mounts_on_create_page(
    page: Page,
    base_url: str,
    field: str,
) -> None:
    page.goto(f"{base_url}/admin/kitchen-sink/create", wait_until="networkidle")
    locator = FIELD_LOCATORS[field](page)
    locator.first.wait_for(state="visible", timeout=10_000)
    assert locator.count() >= 1, f"widget for field={field!r} did not mount"
