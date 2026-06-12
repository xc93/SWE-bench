# Setup Notes

## Environment
- Python 3.9.25 via `uv venv --python 3.9`
- `SETUPTOOLS_SCM_PRETEND_VERSION=3.0` used for truncated history
- pylint installed as editable: version 3.0.0b1
- pytest 8.4.2 installed

## Verification
- Repo HEAD is `2c4c5d8` (truncated history, single "base" commit)
- `import pylint` works, reports version 3.0.0b1
- `tests/config/test_config.py` runs: 16 passed
- `tests/checkers/base/` runs: 8 passed, 1 skipped
