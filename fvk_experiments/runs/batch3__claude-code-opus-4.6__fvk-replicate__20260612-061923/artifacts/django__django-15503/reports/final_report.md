# FVK SWE-bench Experiment: django__django-15503

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=194&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-15503
- Base commit: 859a87d873ce7152af73ab851653b4e1c3ffea4c
- Base commit URL: https://github.com/django/django/commit/859a87d873ce7152af73ab851653b4e1c3ffea4c
- Version: 4.1
- Difficulty: 1-4 hours

## Evaluator Shape

- FAIL_TO_PASS: 2
- PASS_TO_PASS: 78
- Official resolved condition: 2/2 FAIL_TO_PASS and 78/78 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

`has_key`, `has_keys`, and `has_any_keys` JSONField lookups don't handle numeric keys on SQLite, MySQL, and Oracle. The `compile_json_path()` function treats numeric-looking string keys (e.g., `'1111'`) as array indices (`[1111]`) instead of object keys (`."1111"`). This is correct for JSON navigation (`KeyTransform`) but incorrect for key existence checks (`has_key`).

## v1 Patch

- Files changed: `django/db/models/fields/json.py`
- Behavioral change: (1) `HasKeyLookup.as_sql()` now uses `json.dumps(key)` for non-KeyTransform RHS, always producing object key notation. (2) `KeyTransformIsNull.as_sqlite()` and `KeyTransformIsNull.as_oracle()` build SQL directly using `compile_json_path()` instead of going through `HasKey`, avoiding regression from the as_sql change.
- Public tests run: `model_fields.test_jsonfield` (87 tests, all pass)

## v1 Score

FAIL_TO_PASS: 2 / 2
PASS_TO_PASS: 78 / 78
Resolved: true

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

1. **Finding 4 (edge case):** `json.dumps(key)` when key is a Python integer produces unquoted notation (`.0` vs `."0"`). While functionally equivalent, `json.dumps(str(key))` is more defensive.
2. **Finding 3 (regression prevention):** Confirmed that decoupling `KeyTransformIsNull` from `HasKey` was necessary and correct.
3. **Finding 2 (preservation):** Confirmed that KeyTransform RHS behavior (with `compile_json_path`) is correctly preserved.
4. **13 proof obligations identified:** 2 bug-fix obligations and 11 non-regression obligations, all satisfied by v1.

## v2 Patch

- Files changed: `django/db/models/fields/json.py` (same file as v1)
- Behavioral change: Same as v1, plus `str(key)` wrapper before `json.dumps()` for integer key robustness
- Difference from v1: One line change: `json.dumps(key)` → `json.dumps(str(key))`
- Why this follows from FVK: Finding 4 identified the integer key edge case; ITERATION_GUIDANCE recommended wrapping in `str()` for defensive robustness

## v2 Score

FAIL_TO_PASS: 2 / 2
PASS_TO_PASS: 78 / 78
Resolved: true

## Delta

FAIL_TO_PASS delta: 0 (2 - 2)
PASS_TO_PASS delta: 0 (78 - 78)
Resolved delta: unchanged (both resolved)

## Did FVK Help?

1. **Did v2 improve the bug-revealing tests?** No change — both v1 and v2 pass 2/2.
2. **Did v2 preserve regressions better or worse than v1?** Same — both pass 78/78.
3. **Did v2 get a worse total score?** No — identical scores.
4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — v2 did not get worse.
5. **Was the v2 change justified by the FVK artifacts?** Yes — Finding 4 identified a genuine (though low-risk) edge case with integer keys.
6. **Did FVK overgeneralize the desired behavior?** No — FVK correctly identified that v1 was already sufficient and recommended only a minimal defensive change.
7. **What should be changed in the FVK process for regression-heavy SWE-bench tasks?** The FVK process worked well here. For tasks with many regression tests, the explicit proof obligations document (PROOF_OBLIGATIONS.md) effectively cataloged what must not change. The key insight was identifying the `KeyTransformIsNull` → `HasKey` internal coupling as a regression vector, which was already addressed in v1.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
