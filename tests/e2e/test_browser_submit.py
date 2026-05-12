"""Browser full flow: create a row via the form and verify it renders in detail."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import httpx

from tests.e2e.app import KITCHEN_SINK_BASE

if TYPE_CHECKING:
    from playwright.sync_api import Page


def test_simplemde_round_trips_through_browser(page: Page, base_url: str) -> None:
    simplemde_marker = f"e2e-simplemde-{uuid.uuid4().hex[:8]}"
    ck4_marker = f"e2e-ck4-{uuid.uuid4().hex[:8]}"
    ck5_marker = f"e2e-ck5-{uuid.uuid4().hex[:8]}"
    markdown_body = f"# {simplemde_marker}\n\nbody line"

    page.goto(f"{base_url}{KITCHEN_SINK_BASE}/create", wait_until="load")

    page.locator('input[name="bootstrap_show_password"]').fill("p4ssword!")

    # Wait for CKEditor5 instance to be attached before driving it.
    page.wait_for_function(
        "document.querySelector('.ck-editor__editable')"
        " && document.querySelector('.ck-editor__editable').ckeditorInstance"
        " !== undefined",
        timeout=10_000,
    )
    # Wait for CKEditor4 instance to be registered.
    page.wait_for_function(
        "window.CKEDITOR && window.CKEDITOR.instances"
        " && window.CKEDITOR.instances['ckeditor4']",
        timeout=10_000,
    )
    # Wait for SimpleMDE CodeMirror handle.
    page.wait_for_function(
        "document.querySelector('.CodeMirror')"
        " && document.querySelector('.CodeMirror').CodeMirror !== undefined",
        timeout=10_000,
    )

    # Drive each rich editor through its own JS API so a failure is isolated
    # to one editor rather than a combined evaluate call with an opaque stack.
    page.evaluate(
        "([body]) => CKEDITOR.instances['ckeditor4'].setData('<p>' + body + '</p>')",
        [ck4_marker],
    )
    page.evaluate(
        "([body]) => document.querySelector('.ck-editor__editable')"
        ".ckeditorInstance.setData('<p>' + body + '</p>')",
        [ck5_marker],
    )
    page.evaluate(
        "([body]) => document.querySelector('.CodeMirror').CodeMirror.setValue(body)",
        [markdown_body],
    )

    # starlette-admin's create page exposes three submit buttons:
    #   * name="_add_another"      -> redirects back to /create
    #   * name="_continue_editing" -> redirects to /edit/<id>
    #   * <no name>                -> the plain "Save" that redirects to /list
    # Pick the unnamed one explicitly so the test lands on the list page.
    page.locator('button[type="submit"]:not([name])').click()
    try:
        page.wait_for_url(f"{base_url}{KITCHEN_SINK_BASE}/list*", timeout=10_000)
    except Exception as _exc:
        current_url = page.url
        page_text = page.inner_text("body")[:500]
        raise AssertionError(
            f"form submit did not redirect to list. "
            f"current_url={current_url!r}. page snippet: {page_text!r}"
        ) from _exc

    # Navigate to the detail of the row we just created.  Use the unique
    # SimpleMDE marker to locate the correct table row — this is robust when
    # the DB contains more than one row (e.g. if a second submit test is added).
    page.locator(
        f'tr:has-text("{simplemde_marker}") a[href*="{KITCHEN_SINK_BASE}/detail/"]'
    ).click()
    # Wait for each marker to appear in the DOM directly rather than using
    # networkidle + page.content() — JS-rendered detail content may arrive
    # after the network goes idle, causing intermittent assertion failures.
    page.wait_for_selector(f"text={simplemde_marker}", timeout=10_000)
    page.wait_for_selector(f"text={ck4_marker}", timeout=10_000)
    page.wait_for_selector(f"text={ck5_marker}", timeout=10_000)


def test_editors_prepopulate_on_edit_page(page: Page, base_url: str) -> None:
    marker = f"e2e-editpop-{uuid.uuid4().hex[:8]}"

    # Create the row directly via HTTP — no need to drive the create form twice.
    create_resp = httpx.post(
        f"{base_url}{KITCHEN_SINK_BASE}/create",
        data={
            "bootstrap_show_password": "p4ssword!",
            "ckeditor4": f"<p>{marker}</p>",
            "ckeditor5": f"<p>{marker}</p>",
            "simplemde": f"# {marker}",
        },
        follow_redirects=False,
    )
    assert create_resp.status_code in (302, 303), (
        f"create failed: {create_resp.status_code}"
    )

    # Navigate to the list page, locate the row by its marker, click Edit.
    page.goto(f"{base_url}{KITCHEN_SINK_BASE}/list", wait_until="load")
    page.locator(
        f'tr:has-text("{marker}") a[href*="{KITCHEN_SINK_BASE}/edit/"]'
    ).click()

    # Wait for all rich-text editors to initialise on the edit page.
    page.wait_for_function(
        "window.CKEDITOR && window.CKEDITOR.instances"
        " && window.CKEDITOR.instances['ckeditor4']",
        timeout=10_000,
    )
    page.wait_for_function(
        "document.querySelector('.ck-editor__editable')"
        " && document.querySelector('.ck-editor__editable').ckeditorInstance !== undefined",
        timeout=10_000,
    )
    page.wait_for_function(
        "document.querySelector('.CodeMirror')"
        " && document.querySelector('.CodeMirror').CodeMirror !== undefined",
        timeout=10_000,
    )

    ck4_content = page.evaluate("() => CKEDITOR.instances['ckeditor4'].getData()")
    ck5_content = page.evaluate(
        "() => document.querySelector('.ck-editor__editable').ckeditorInstance.getData()"
    )
    simplemde_content = page.evaluate(
        "() => document.querySelector('.CodeMirror').CodeMirror.getValue()"
    )

    assert marker in ck4_content, (
        f"CKEditor4 not pre-populated on edit page: {ck4_content!r}"
    )
    assert marker in ck5_content, (
        f"CKEditor5 not pre-populated on edit page: {ck5_content!r}"
    )
    assert marker in simplemde_content, (
        f"SimpleMDE not pre-populated on edit page: {simplemde_content!r}"
    )
