# Setup Notes

## Environment

- Repo checked out at base commit (truncated history, single "base" commit fb4873c)
- Python 3.9.25 via uv
- Created .venv with uv, installed pip/setuptools/wheel via uv pip
- Installed pylint in editable mode with SETUPTOOLS_SCM_PRETEND_VERSION=3.0
- Installed pytest

## Verification

- `pylint.__version__` reports `3.0.0b1`
- Quick test `tests/test_self.py::TestRunTC::test_version` passes
- Config test suite runs: 15/16 pass at baseline (before any changes, 16/16 pass; after v1, 15/16 pass with test_csv_regex_error failing as expected)
