"""Browser full flow: create a row via the form and verify it renders in detail."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from tests.e2e.app import KITCHEN_SINK_BASE

if TYPE_CHECKING:
    from playwright.sync_api import Page


def test_simplemde_round_trips_through_browser(page: Page, base_url: str) -> None:
    unique_marker = f"e2e-simplemde-{uuid.uuid4().hex[:8]}"
    markdown_body = f"# {unique_marker}\n\nbody line"

    page.goto(f"{base_url}{KITCHEN_SINK_BASE}/create", wait_until="networkidle")

    page.locator('input[name="bootstrap_show_password"]').fill("p4ssword!")

    # The three rich editors sync to their hidden <textarea name="..."> only on
    # form submit, and they overwrite any value we set directly on the textarea.
    # So drive each one through its own JS API:
    # - CKEditor4: `CKEDITOR.instances['<name>'].setData(...)`
    # - CKEditor5: the editable DIV exposes its editor at `.ckeditorInstance`
    # - SimpleMDE: wraps CodeMirror; the `.CodeMirror` DOM node exposes the
    #   underlying instance at `.CodeMirror`.
    page.evaluate(
        """(simplemdeBody) => {
            CKEDITOR.instances['ckeditor4'].setData('<p>ck4 body</p>');
            const ck5Editable = document.querySelector('.ck-editor__editable');
            ck5Editable.ckeditorInstance.setData('<p>ck5 body</p>');
            const cmEl = document.querySelector('.CodeMirror');
            cmEl.CodeMirror.setValue(simplemdeBody);
        }""",
        markdown_body,
    )

    # starlette-admin's create page exposes three submit buttons:
    #   * name="_add_another"      -> redirects back to /create
    #   * name="_continue_editing" -> redirects to /edit/<id>
    #   * <no name>                -> the plain "Save" that redirects to /list
    # Pick the unnamed one explicitly so the test lands on the list page.
    page.locator('button[type="submit"]:not([name])').click()
    page.wait_for_url(f"{base_url}{KITCHEN_SINK_BASE}/list*", timeout=10_000)

    # Open the detail of the new row. The list renders a row action that links
    # to `/admin/kitchen-sink/detail/<id>`; clicking the first such link is
    # sufficient because the uvicorn subprocess starts with a clean DB.
    page.locator(f'a[href*="{KITCHEN_SINK_BASE}/detail/"]').first.click()
    page.wait_for_load_state("networkidle")
    assert unique_marker in page.content(), (
        "submitted markdown body did not appear in detail view"
    )
