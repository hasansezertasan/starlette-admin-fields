"""Browser render-smoke: each field's widget mounts on the create page."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.e2e.app import KITCHEN_SINK_BASE

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
    page.goto(f"{base_url}{KITCHEN_SINK_BASE}/create", wait_until="load")
    locator = FIELD_LOCATORS[field](page)
    try:
        locator.first.wait_for(state="visible", timeout=10_000)
    except PlaywrightTimeoutError as exc:
        raise AssertionError(
            f"widget for field={field!r} did not become visible within 10s"
        ) from exc


def test_bootstrap_show_password_wraps_input(page: Page, base_url: str) -> None:
    """The bootstrap-show-password library wraps the input and injects a toggle button.

    The actual click behaviour belongs to the third-party JS library and varies
    across Bootstrap/jQuery versions — we verify only that our field triggers
    the library initialisation by emitting the right markup and attributes.
    The data-attribute correctness is covered by
    ``test_bootstrap_show_password_data_attributes``.
    """
    page.goto(f"{base_url}{KITCHEN_SINK_BASE}/create", wait_until="load")

    password_input = page.locator('input[name="bootstrap_show_password"]')
    password_input.wait_for(state="visible", timeout=10_000)

    page.wait_for_function(
        """() => {
            const input = document.querySelector('input[name="bootstrap_show_password"]');
            if (!input) return false;
            const group = input.closest('.input-group');
            return group !== null && group.querySelector('button') !== null;
        }""",
        timeout=10_000,
    )

    assert password_input.get_attribute("type") == "password", (
        "password input should start with type=password"
    )


def test_bootstrap_show_password_data_attributes(page: Page, base_url: str) -> None:
    """data-toggle and data-size must be present on the password input."""
    page.goto(f"{base_url}{KITCHEN_SINK_BASE}/create", wait_until="load")
    pwd = page.locator('input[name="bootstrap_show_password"]')
    pwd.wait_for(state="visible", timeout=10_000)
    assert pwd.get_attribute("data-toggle") == "password", (
        "data-toggle='password' missing — bootstrap-show-password library will not activate"
    )
    assert pwd.get_attribute("data-size") == "md", (
        "data-size='md' missing — field was configured with size='md'"
    )


def test_rich_field_data_options_present(page: Page, base_url: str) -> None:
    """Each rich-text textarea must carry a valid JSON data-options attribute."""
    page.goto(f"{base_url}{KITCHEN_SINK_BASE}/create", wait_until="load")
    for field_name in ("ckeditor4", "simplemde"):
        raw = page.locator(f'textarea[name="{field_name}"]').get_attribute(
            "data-options"
        )
        assert raw is not None, f"{field_name}: data-options attribute missing"
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"{field_name}: data-options is not valid JSON: {raw!r}"
            ) from exc
