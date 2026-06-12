# Setup Notes

## Environment

- Python 3.9.25 via uv venv
- Django 4.1.dev installed in editable mode
- SQLite backend (default for tests)

## Verification

- `repo/` checked out at base commit `e0b6cceb2f4e231bba5947c5a7c5a2416307f7e6` (truncated history, mapped to `859a87d873ce7152af73ab851653b4e1c3ffea4c`)
- Django imports successfully: version `4.1.dev20260612054539`
- Test runner works: `tests/runtests.py model_fields.test_jsonfield` runs 87 tests, OK (8 skipped)
