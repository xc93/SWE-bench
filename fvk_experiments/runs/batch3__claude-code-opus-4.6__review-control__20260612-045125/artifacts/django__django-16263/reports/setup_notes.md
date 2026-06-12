# Setup Notes

- Repo checked out at `e384ffa` (squashed base commit per workspace manifest; original base is `321ecb40f4da842926e1bc07e11df4aabe53ca4b`)
- Created `.venv/` with Python 3.11 via `uv venv`
- Installed Django in editable mode: `pip install -e .` from `repo/`
- Verified `import django` works: version `4.2.dev20260612063944`
- Verified test runner works: `runtests.py aggregation.tests.AggregateTestCase.test_count` passes
