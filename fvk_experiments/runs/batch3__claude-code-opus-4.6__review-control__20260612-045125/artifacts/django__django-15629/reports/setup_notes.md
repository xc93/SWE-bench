# Setup Notes

## Environment

- Python 3.9.25 via uv
- Django 4.1.dev installed in editable mode from `repo/`
- Created `.venv/` using `uv venv --python 3.9`
- Installed pip/setuptools/wheel via `uv pip install`
- Installed Django with `pip install -e repo` and `SETUPTOOLS_SCM_PRETEND_VERSION=4.1`

## Verification

- `repo/` HEAD is at `45841312baa7a27eb94e3e03e7e2d84e998d0336` (commit message "base", representing the base state)
- `.venv/bin/python -c "import django; print(django.__version__)"` outputs `4.1.dev20260612060454`
- Test runner works: `runtests.py schema.tests.SchemaTests.test_alter` passes (1 test, OK)
- Full schema suite: 179 tests, 28 skipped, all OK
- Full migrations suite: 657 tests, 1 skipped, all OK
- Full model_fields suite: 430 tests, 55 skipped, all OK
