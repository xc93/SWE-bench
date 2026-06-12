# Setup Notes

## Environment

- Repository checked out at commit `27cc880` (squashed base commit labeled "base", corresponding to `694cf458f16b8d340a3195244196980b2dec34fd`)
- Django version: 4.1.dev
- Python: 3.9.25 via uv venv
- Installed Django in editable mode with `uv pip install -e repo/`

## Verification

- `git rev-parse HEAD` returns `27cc880382d90c4f9b2df8a35583c4aa755404ee`
- `.venv/bin/python -c "import django; print(django.__version__)"` returns `4.1.dev20260612033838`
- Test runner works: ran `schema.tests.SchemaTests.test_db_collation_charfield` successfully
- Full schema test suite: 179 tests, all pass (28 skipped for SQLite)
- Full migration test suite: 657 tests, all pass (1 skipped)
- Full invalid_models tests: 272 tests, all pass (13 skipped)
