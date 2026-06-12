# Review-Control SWE-bench Experiment: django__django-16560

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

## Evaluator Shape

- FAIL_TO_PASS: 8
- PASS_TO_PASS: 66
- Official resolved condition: 8/8 FAIL_TO_PASS and 66/66 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

The issue requests the ability to customize the `code` attribute of `ValidationError` raised by `BaseConstraint.validate()`. Currently, `violation_error_message` can be customized but not the error code. The hint confirms adding a `violation_error_code` parameter, following the same pattern as Django validators.

## v1 Patch

- Files changed: `django/db/models/constraints.py`
- Behavioral change: Added `violation_error_code` parameter to `BaseConstraint`, `CheckConstraint`, and `UniqueConstraint`. Passes it as `code=` to `ValidationError` in `validate()` methods. Included in `deconstruct()` and `__eq__()`.
- Public tests run: 73 constraint tests (all pass, 4 skipped for DB features)

## v1 Score

FAIL_TO_PASS: 6 / 8
PASS_TO_PASS: 66 / 66
Resolved: false

## Review Artifacts

- review/FINDINGS.md
- review/ITERATION_GUIDANCE.md

## Key Review Findings

1. **ExclusionConstraint missed entirely**: `django/contrib/postgres/constraints.py` contains `ExclusionConstraint(BaseConstraint)` which was not updated in v1. Its `__init__`, `validate()`, and `__eq__` methods all needed `violation_error_code` support.
2. **`__repr__` methods not updated**: All three constraint classes (`CheckConstraint`, `UniqueConstraint`, `ExclusionConstraint`) conditionally include `violation_error_message` in their `__repr__` output but v1 did not add the same for `violation_error_code`.

## v2 Patch

- Files changed: `django/db/models/constraints.py`, `django/contrib/postgres/constraints.py`
- Behavioral change: v1 changes plus `ExclusionConstraint` support and `__repr__` updates across all three constraint classes
- Difference from v1: Added `violation_error_code` to `ExclusionConstraint.__init__`, `validate()`, `__eq__()`, and `__repr__()`. Added `violation_error_code` to `CheckConstraint.__repr__()` and `UniqueConstraint.__repr__()`.
- Why this follows from the review: The review identified both gaps by systematically checking all `BaseConstraint` subclasses and all methods that reference `violation_error_message`.

## v2 Score

FAIL_TO_PASS: 8 / 8
PASS_TO_PASS: 66 / 66
Resolved: true

## Delta

FAIL_TO_PASS delta: +2 (6 -> 8)
PASS_TO_PASS delta: 0 (66 -> 66)
Resolved delta: improved (false -> true)

## Did the Review Help?

1. Did v2 improve the bug-revealing tests? **Yes**, from 6/8 to 8/8.
2. Did v2 preserve regressions better or worse than v1? **Same** - 66/66 both times.
3. Did v2 get a worse total score? **No**, v2 improved from not-resolved to resolved.
4. If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both? **N/A** - v2 improved.
5. Was the v2 change justified by the review artifacts? **Yes** - the review identified both missing subclass coverage (ExclusionConstraint) and missing `__repr__` updates as the gaps.
6. Did the review overgeneralize the desired behavior? **No** - all changes were minimal and directly paralleled the existing `violation_error_message` pattern.
7. What should be changed in the review process for regression-heavy SWE-bench tasks? The review correctly identified a missing subclass by searching the codebase, but initially underweighted `__repr__` as "unlikely to be tested." A more systematic review checklist that enumerates every method touching the parallel attribute (`violation_error_message`) would have caught both gaps in one pass.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
