# E2E Tests for starlette-admin-fields — Design

**Status:** Approved (design phase)
**Date:** 2026-05-11
**Owner:** hasansezertasan

## Goal

Add end-to-end tests that exercise the four fields (`BootstrapShowPasswordField`, `CKEditor4Field`, `CKEditor5Field`, `SimpleMDEField`) through both a backend HTTP round-trip and a real browser, so that JS-template regressions and form-processing regressions are caught before release.

## Non-Goals

- Cross-browser matrix (Chromium only).
- Cross-OS matrix (Linux only in CI).
- Reusing `examples/kitchensink` directly — example app drifts with docs and tests need a stable contract.
- Visual regression / screenshot diffing.

## Approach

Hybrid: parametrized HTTP round-trip for full backend coverage of all four fields, plus minimal Playwright browser tests for JS-render verification and one full submit flow.

## Layout

```
tests/
  e2e/
    __init__.py
    app.py
    conftest.py
    test_http_roundtrip.py
    test_browser_render.py
    test_browser_submit.py
```

`tests/e2e/app.py` — dedicated kitchensink-mirror Starlette app. Always uses in-memory SQLite. Mounts `StarletteAdminFields(admin)` and one `KitchenSinkView` with all four fields plus an `IntegerField` for `id`. Exposes module-level `app` for uvicorn import and a factory `make_app()` for the TestClient fixture (fresh engine per call).

## Backend HTTP round-trip — `test_http_roundtrip.py`

Single parametrized test, table-driven over the four fields.

```python
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("bootstrap_show_password", "s3cret!"),
        ("ckeditor4", "<p>hello</p>"),
        ("ckeditor5", "<p>world</p>"),
        ("simplemde", "# heading"),
    ],
)
def test_create_then_detail_roundtrips_value(client, field, value): ...
```

- Uses `starlette.testclient.TestClient` against an app built by `make_app()` from `tests/e2e/app.py` (fresh in-memory SQLite per test — full isolation).
- POSTs create form with the parametrized field's value plus minimal valid values for the other three required fields.
- Asserts on the persisted row via the test-owned SQLAlchemy engine — robust across detail-view rendering quirks (e.g. password masking, HTML escaping in rich-text fields).

A second assertion verifies the detail-view GET returns 200, to catch detail-template rendering regressions without coupling to exact HTML.

## Browser render-smoke — `test_browser_render.py`

Parametrized over the four fields. Each case:

1. `page.goto(f"{base_url}/admin/kitchen-sink/create")`.
2. Wait for the field-specific selector (Playwright locator auto-wait — no `time.sleep`):
   - `CKEditor4Field` → `iframe.cke_wysiwyg_frame`
   - `CKEditor5Field` → `div.ck-editor__editable`
   - `SimpleMDEField` → `div.CodeMirror`
   - `BootstrapShowPasswordField` → `button.input-group-text` plus `input[type=password]`
3. Assert `locator.count() == 1` and `locator.is_visible()`.

No submission. Goal: catch static-asset, template-loader, and JS-init regressions cheaply.

## Browser full-flow — `test_browser_submit.py`

Single test against `SimpleMDEField` (chosen because asserting plain-markdown persisted text is the most robust across browser versions).

1. Goto create page.
2. Fill the other three required fields via locators.
3. Type into SimpleMDE's CodeMirror textarea (`textarea.CodeMirror` or `.CodeMirror` evaluator).
4. Click Save.
5. Wait for redirect to the list view.
6. Click into detail of the new row.
7. Assert the typed markdown source is present in the page (SimpleMDE stores raw markdown, so the source text appears unescaped in detail HTML).

## Fixtures — `tests/e2e/conftest.py`

```python
@pytest.fixture(scope="session")
def free_port() -> int: ...
@pytest.fixture(scope="session")
def uvicorn_server(free_port) -> str:
    # subprocess.Popen(["uvicorn", "tests.e2e.app:app", "--port", str(free_port)])
    # poll http://127.0.0.1:{port}/admin/ until 200, timeout 10s
    yield f"http://127.0.0.1:{free_port}"
    # terminate; kill on timeout
@pytest.fixture
def base_url(uvicorn_server) -> str: return uvicorn_server
@pytest.fixture
def client() -> TestClient: ...   # in-process TestClient over fresh make_app()
```

Browser tests don't need DB inspection — render-smoke checks selectors only, full-flow asserts via the rendered detail view. Subprocess state leaks across browser tests are avoided by using unique field values per test (UUID-suffixed strings) so assertions can't collide with prior rows.

`pytest_collection_modifyitems` adds `@pytest.mark.e2e` to every test under `tests/e2e/`.

## Dependencies and configuration

`pyproject.toml`:

```toml
[dependency-groups]
e2e = [
  "pytest-playwright>=0.5.0",
  "sqlalchemy>=2.0",
  "uvicorn>=0.46",
]
dev = [
  # ...existing...
  {include-group = "e2e"},
]

[tool.pytest.ini_options]
markers = ["e2e: end-to-end tests (browser + subprocess)"]
```

Coverage: `tests/e2e/app.py` will not be measured by the subprocess uvicorn run. Add it to `[tool.coverage.run].omit` or accept that the library's own source already hits 99% via unit/integration tests.

Local commands:

```console
uv sync --group e2e
uv run playwright install --with-deps chromium
uv run pytest tests/e2e
```

## CI

New job in `.github/workflows/ci.yml`:

```yaml
e2e:
  runs-on: ubuntu-latest
  needs: [test]
  steps:
    - uses: actions/checkout@v6
    - uses: astral-sh/setup-uv@v4
      with: { enable-cache: true }
    - run: uv sync --group e2e
    - run: uv run playwright install --with-deps chromium
    - run: uv run pytest tests/e2e -v
    - if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: playwright-trace
        path: test-results/
```

- Python 3.13.
- Runs only when unit/integration job is green (`needs: [test]`).
- Playwright traces uploaded on failure.
- Future optimisation: cache `~/.cache/ms-playwright` keyed on `pytest-playwright` version if install time becomes a bottleneck.

## Risks and mitigations

- **Browser flake** — limit browser tests to four render-smoke cases plus one submit. Use Playwright auto-wait locators only; no fixed sleeps.
- **CDN-loaded JS** (CKEditor4 loads from CDN) — render-smoke selectors must wait for editor mount; if the CDN is unreachable in CI, the test will time out clearly. Document that CI runners need outbound HTTPS.
- **Subprocess teardown** — `terminate()` first, `kill()` after a short timeout, asserted by polling the port.
- **Cross-test state in subprocess DB** — uvicorn boots once per session over in-memory SQLite, so rows accumulate. Mitigated by uniquely-keyed payloads (UUID-suffixed values) in browser tests; no truncate fixture needed.

## Out of scope (future)

- Visual regression tests.
- Cross-browser matrix.
- Replacing `examples/kitchensink` with the e2e app (kept separate by design).
