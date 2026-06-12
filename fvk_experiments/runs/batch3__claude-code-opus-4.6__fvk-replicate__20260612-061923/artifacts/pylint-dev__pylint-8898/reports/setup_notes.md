# Setup Notes

- Created venv with Python 3.9 via `uv venv --python 3.9 .venv`
- Installed pip via `ensurepip`, then upgraded pip/setuptools/wheel
- Installed pylint in editable mode with `SETUPTOOLS_SCM_PRETEND_VERSION=3.0`
- Installed pytest
- Verified `pylint.__version__` = `3.0.0b1`
- Verified test runner: `pytest repo/tests/config/test_config.py` — 16 passed
- Repo HEAD is `f36dc7e` (truncated history, original base commit `1f8c4d9eb185c16a2c1d881c054f015e1c2eb334`)
