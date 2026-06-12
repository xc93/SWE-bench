# Setup Notes

## Repository
- Checked out at single squashed commit `633e446` (base commit for this workspace)
- No remote configured (as expected)

## Virtual Environment
- Created with `uv venv --python 3.9 .venv`
- Installed Django from repo with `uv pip install --python .venv/bin/python -e ./repo`
- Django version confirmed: `4.2.dev20260612034544`

## Test Runner
- Verified with `python tests/runtests.py prefetch_related -v2` — 109 tests pass
- Verified with `python tests/runtests.py prefetch_related.test_prefetch_related_objects -v2` — 11 tests pass
