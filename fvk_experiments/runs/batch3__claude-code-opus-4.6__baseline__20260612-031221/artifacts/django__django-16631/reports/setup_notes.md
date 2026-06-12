# Setup Notes

## Environment
- Python 3.11.15 via uv venv
- Django 5.0.dev installed editable from repo/
- SETUPTOOLS_SCM_PRETEND_VERSION=5.0 used due to truncated history

## Verification
- Repo checked out at base commit (truncated history, hash a4469213c16e8de7254b04cd3450f9b260dc57fa labeled "base")
- `import django` works, version 5.0.dev20260612041754
- Auth tests pass: 606 tests OK (10 skipped)
