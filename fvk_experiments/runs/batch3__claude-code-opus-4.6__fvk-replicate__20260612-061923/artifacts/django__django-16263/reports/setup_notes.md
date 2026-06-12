# Phase 0: Setup Notes

- Repo checked out at base commit (truncated history, local HEAD 148d8c1)
- Created `.venv/` with Python 3.11.15 via `uv venv --python 3.11`
- Installed Django in editable mode: `pip install -e repo/`
- Django version: 4.2.dev
- Test runner verified: `runtests.py aggregation.tests.AggregateTestCase.test_count` passes
