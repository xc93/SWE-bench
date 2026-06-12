# Setup Notes

## Environment
- Python: 3.11.15 (via uv)
- Django: 4.2.dev (editable install from repo/)
- Repo checked out at local HEAD 1d7b9b3 (squashed from base commit f387d024)

## Steps
1. Created .venv with `uv venv --python 3.11`
2. Bootstrapped pip with `ensurepip`
3. Installed Django in editable mode from repo/
4. Verified `import django` works
5. Ran prefetch_related test suite: 109 tests, all OK
