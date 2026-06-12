# Setup Notes

## Environment
- Python 3.11.15 via uv
- Django 5.0.dev installed in editable mode
- venv at `.venv/`

## Verification
- `repo/` HEAD: c9ecd656f2b (squashed base commit matching environment_setup_commit)
- `import django` works; version = 5.0.dev20260612075809
- Test runner: `../.venv/bin/python tests/runtests.py constraints -v2` runs 73 tests, all pass (4 skipped for DB features)
