# Setup Notes

## Environment
- Python 3.11.15 via uv venv
- Django installed in editable mode from repo/
- SETUPTOOLS_SCM_PRETEND_VERSION=5.0 used for install

## Verification
- Repo checked out at base commit (truncated history, local head 92fbc958206e64a61146f01e97be1e964dfcbde6)
- `import django` works, version reports 5.0.dev
- Test runner works: `python tests/runtests.py constraints --verbosity=0` runs 73 tests, 4 skipped, all pass
