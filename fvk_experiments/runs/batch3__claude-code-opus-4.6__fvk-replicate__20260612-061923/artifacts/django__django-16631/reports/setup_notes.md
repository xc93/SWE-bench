# Setup Notes

- Repo checked out at truncated base commit (single "base" commit, equivalent to 9b224579875e30203d079cc2fee83b116d98eb78)
- Created .venv with Python 3.11 via uv
- Installed Django in dev mode via `uv pip install -e repo`
- Django version: 5.0.dev
- Test runner works: `python tests/runtests.py auth_tests.test_tokens --settings=test_sqlite` runs 11 tests OK
- Full auth_tests suite: 606 tests OK (10 skipped)
