# Setup Notes

## Environment
- Python 3.9.25 via uv venv
- Django 4.1.dev installed in editable mode
- Repo at truncated single-commit base (hash bbb1c8cc, labeled "base")

## Verified
- `.venv/bin/python` imports Django 4.1.dev
- Test runner works: `tests/runtests.py schema` ran 179 tests, all passed (28 skipped)
- No git remote configured (truncated history, as expected)
