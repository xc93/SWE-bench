# Setup Notes

## Environment

- Python 3.9.25 via `uv venv --python 3.9`
- Installed pylint in editable mode with `SETUPTOOLS_SCM_PRETEND_VERSION=2.9`
- pylint version: 2.9.0-dev1
- astroid version: 2.6.6

## Verification

- Repo checked out at squashed commit `e53f975` (base state for pylint-dev__pylint-4551)
- `.venv/bin/python` imports pylint successfully
- All 23 existing pyreverse tests pass:
  - `tests/unittest_pyreverse_writer.py` (6 tests)
  - `tests/unittest_pyreverse_inspector.py` (8 tests)
  - `tests/unittest_pyreverse_diadefs.py` (9 tests)
