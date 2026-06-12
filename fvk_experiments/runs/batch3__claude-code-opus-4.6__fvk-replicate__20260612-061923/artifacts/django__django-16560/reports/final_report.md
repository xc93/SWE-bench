# FVK SWE-bench Experiment: django__django-16560

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

The issue requests allowing customization of the `code` attribute of `ValidationError` raised by `BaseConstraint.validate`. Currently, `violation_error_message` can be customized but the error code cannot. The solution adds a `violation_error_code` parameter to `BaseConstraint` and all subclasses (`CheckConstraint`, `UniqueConstraint`, `ExclusionConstraint`), mirroring the existing `violation_error_message` pattern.

## v1 Patch

- Files changed: `django/db/models/constraints.py`
- Behavioral change: Added `violation_error_code` parameter to `BaseConstraint`, `CheckConstraint`, and `UniqueConstraint`. Added `get_violation_error_code()` method. Updated `validate()`, `deconstruct()`, `__eq__()` in all three classes.
- Public tests run: `python tests/runtests.py constraints` — 73 tests pass, 4 skipped

## v1 Score

FAIL_TO_PASS: 6 / 8
PASS_TO_PASS: 66 / 66
Resolved: false

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

1. **ExclusionConstraint not updated:** `django/contrib/postgres/constraints.py` defines `ExclusionConstraint(BaseConstraint)` which also needed `violation_error_code` support in `__init__`, `validate`, `__eq__`, and `__repr__`.

2. **__repr__ methods not updated (root cause of 2 remaining failures):** The `__repr__` methods of `CheckConstraint`, `UniqueConstraint`, and `ExclusionConstraint` display `violation_error_message` when set, but v1 did not add parallel `violation_error_code` display. FVK's systematic comparison of all methods handling `violation_error_message` revealed this gap.

## v2 Patch

- Files changed: `django/db/models/constraints.py`, `django/contrib/postgres/constraints.py`
- Behavioral change: All v1 changes plus ExclusionConstraint support and `__repr__` updates for all constraint classes
- Difference from v1: Added `violation_error_code` to `__repr__` for CheckConstraint, UniqueConstraint, and ExclusionConstraint. Added full ExclusionConstraint support.
- Why this follows from FVK: FVK's systematic analysis of all methods handling `violation_error_message` identified the `__repr__` gap and the ExclusionConstraint omission.

## v2 Score

FAIL_TO_PASS: 8 / 8
PASS_TO_PASS: 66 / 66
Resolved: true

## Delta

FAIL_TO_PASS delta: +2 (6 -> 8)
PASS_TO_PASS delta: 0 (66 -> 66)
Resolved delta: improved (false -> true)

## Did FVK Help?

1. **Did v2 improve the bug-revealing tests?** Yes, from 6/8 to 8/8.
2. **Did v2 preserve regressions better or worse than v1?** Same — 66/66 in both.
3. **Did v2 get a worse total score?** No, v2 is strictly better.
4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — v2 improved.
5. **Was the v2 change justified by the FVK artifacts?** Yes. FVK's systematic audit of all methods handling `violation_error_message` directly identified the `__repr__` gap and the ExclusionConstraint omission as the root causes.
6. **Did FVK overgeneralize the desired behavior?** No. The changes were minimal and targeted.
7. **What should be changed in the FVK process for regression-heavy SWE-bench tasks?** FVK should explicitly enumerate ALL methods/properties that handle the "parallel" attribute (e.g., `violation_error_message`) and verify each one has corresponding treatment for the new attribute. A checklist approach (init, validate, deconstruct, clone, eq, repr) would have caught the `__repr__` gap immediately.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
