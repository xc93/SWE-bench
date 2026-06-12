# Setup Notes

## Environment

- Workspace: `/home/xc/.cache/fvk-workspaces/batch3__claude-code-opus-4.6__review-control__20260612-045125/django__django-16631`
- Repository: Django at base commit `9b224579875e30203d079cc2fee83b116d98eb78`
- Python: 3.11 virtualenv at `venv/`
- SWE-bench instance: `django__django-16631`
- Issue: "SECRET_KEY_FALLBACKS is not used for sessions"

## Setup Steps

1. Created workspace directories: `patches/`, `reports/`, `review/`
2. Built virtualenv with `python3 -m venv venv && pip install -e ./repo`
3. Verified Django test runner: `python tests/runtests.py --settings=test_sqlite auth_tests.test_basic`
4. Confirmed evaluator baseline: FAIL_TO_PASS 0/1, PASS_TO_PASS 12/12

## Evaluator Shape

- FAIL_TO_PASS: 1 test (hidden test added by test_patch to `auth_tests.test_basic`)
- PASS_TO_PASS: 12 tests (existing tests in `auth_tests.test_basic`)
- Parser: `django`
- Test command: `./tests/runtests.py --verbosity 2 --settings=test_sqlite --parallel 1 auth_tests.test_basic`
