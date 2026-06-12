# Setup Notes

## Environment

- Python 3.11.15 via uv venv
- Django 4.2.dev installed in editable mode from repo/
- Base commit: cb3983a (truncated history; corresponds to f387d024fc75569d2a4a338bfda76cc2f328f627)

## Verification

- `git rev-parse HEAD` → cb3983a4f33504f91a0e7d6b391809b334f721d3 (single "base" commit due to truncated history)
- `import django; print(django.__version__)` → 4.2.dev20260612062530
- Test runner: `./runtests.py prefetch_related.tests.PrefetchRelatedTests.test_m2m_then_m2m` → OK

## Steps

1. Created venv: `uv venv --python 3.11 .venv`
2. Installed pip: `.venv/bin/python -m ensurepip`
3. Upgraded: `.venv/bin/python -m pip install -U pip setuptools wheel`
4. Installed Django: `.venv/bin/pip install -e repo/`
