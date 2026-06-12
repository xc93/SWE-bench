# Setup Notes

## Environment

- Python 3.9.25 via uv
- Django 4.1.dev (editable install from repo/)
- SQLite backend for testing

## Verification

- Repo checked out at local HEAD 05ef59166b (squashed base commit)
- `import django` works, version 4.1.dev20260612072043
- Django test runner works: `runtests.py model_fields.test_jsonfield --settings=test_sqlite` runs 87 tests, all pass (8 skipped)
