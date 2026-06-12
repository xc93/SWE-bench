# Setup Notes

## Environment

- Repo checked out at truncated history (commit `39eb15f`), representing the base state for django__django-16263.
- Created `.venv` using `uv venv --python 3.11` and installed Django + deps with `uv pip install -p .venv/bin/python -e ./repo`.
- Verified `django` imports correctly and version is `4.2.dev*`.

## Test Runner

- Tests run from `repo/tests/` using `../../.venv/bin/python runtests.py <module> --parallel=1`.
- Confirmed test runner works with `aggregation.tests.AggregateTestCase.test_count`.

## Tested Suites (all passing)

- aggregation (116 tests)
- aggregation_regress (69 tests)
- annotations (82 tests)
- queries (504 tests)
- expressions (192 tests)
- expressions_window (59 tests)
- ordering (53 tests)
- lookup (70 tests)
- prefetch_related (89 tests)
- select_related (45 tests)
- queryset_pickle (39 tests)
- db_functions (344 tests)
- extra_regress, model_regress, basic, delete, update, get_earliest_or_latest, distinct_on_fields
