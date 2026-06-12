# Setup Notes

## Environment

- Python 3.9.25 via `uv venv`
- pylint 2.9.0-dev1 installed in editable mode via `uv pip install -e repo/`
- pytest 8.4.2 installed for running tests
- SETUPTOOLS_SCM_PRETEND_VERSION=2.9 used during install (truncated git history lacks tags)

## Verification

- `repo/` is checked out at base commit (hash `7203089ce146f3284baf8247f07b2d01396ce44b`, truncated from `99589b08de8c5a2c6cc61e13a37420a868c80599`)
- `.venv/bin/python` imports pylint successfully, version 2.9.0-dev1
- Test runner works: `pytest repo/tests/test_numversion.py` — 11 passed
- All pyreverse tests pass: `pytest repo/tests/unittest_pyreverse_inspector.py repo/tests/unittest_pyreverse_writer.py repo/tests/unittest_pyreverse_diadefs.py` — 23 passed
