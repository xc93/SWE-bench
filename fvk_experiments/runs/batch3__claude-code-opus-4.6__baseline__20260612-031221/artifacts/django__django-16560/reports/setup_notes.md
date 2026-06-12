# Setup Notes

## Environment
- Repo checked out at base commit (truncated history, single `c3b0922 base` commit)
- Created `.venv` with Python 3.11 via `uv venv --python 3.11 .venv`
- Installed Django in editable mode: `uv pip install -e repo/ -p .venv/bin/python`
- Django version confirmed: `5.0.dev20260612041158`

## Verification
- `import django` works from `.venv/bin/python`
- Ran `constraints` test suite: 73 tests passed (4 skipped due to DB feature requirements)
- Test command: `PYTHONPATH=repo .venv/bin/python repo/tests/runtests.py constraints --verbosity=2`
