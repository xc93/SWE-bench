# SWE-bench Baseline: django__django-16560

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=232&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-16560
- Base commit: 51c9bb7cd16081133af4f0ab6d06572660309730
- Base commit URL: https://github.com/django/django/commit/51c9bb7cd16081133af4f0ab6d06572660309730
- Version: 5.0
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

The issue requests the ability to customize the `code` attribute of `ValidationError` raised by `BaseConstraint.validate`. Currently, users can customize the `violation_error_message` but not the error code. To set a custom code, users must subclass the constraint and override `validate` to catch and re-raise the `ValidationError` with a custom code. The proposal is to add a `violation_error_code` parameter to `BaseConstraint`, mirroring the existing mechanism for validators.

## Patch

- Files changed: `django/db/models/constraints.py`
- Behavioral change:
  - Added `violation_error_code` parameter to `BaseConstraint.__init__`, `CheckConstraint.__init__`, and `UniqueConstraint.__init__`
  - Added `get_violation_error_code()` method to `BaseConstraint`
  - All `ValidationError` raises in `CheckConstraint.validate` and `UniqueConstraint.validate` now pass `code=self.get_violation_error_code()`
  - `violation_error_code` is included in `deconstruct()` when non-None
  - `violation_error_code` is included in `__eq__` comparisons for `CheckConstraint` and `UniqueConstraint`
  - The `clone()` method automatically supports `violation_error_code` via `deconstruct()`
  - Default value is `None`, preserving full backward compatibility
- Public tests run: 73 tests in `constraints.tests` (all pass, 4 skipped for DB features)
- Why this matches the public issue statement: The issue asks for a `violation_error_code` parameter on `BaseConstraint` analogous to `violation_error_message`, to allow customizing the `code` attribute of `ValidationError` raised during constraint validation. This patch adds exactly that capability across all constraint classes.
