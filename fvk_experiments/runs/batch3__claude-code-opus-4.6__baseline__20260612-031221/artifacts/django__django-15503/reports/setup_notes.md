# Setup Notes

## Environment

- Python 3.9.25 via uv
- Django 4.1.dev installed from repo in editable mode
- SQLite backend for testing

## Verification

- `repo/` is checked out at the base commit (3214b2e, grafted)
- `.venv/bin/python` imports django 4.1.dev
- Test runner works: `python tests/runtests.py model_fields.test_jsonfield --parallel 1` runs 87 tests (79 pass, 8 skipped for SQLite-unsupported features)
