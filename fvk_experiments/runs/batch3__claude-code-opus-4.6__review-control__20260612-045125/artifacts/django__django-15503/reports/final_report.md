# Review-Control SWE-bench Experiment: django__django-15503

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

`has_key`, `has_keys`, and `has_any_keys` JSONField lookups don't handle numeric string keys on SQLite, MySQL, and Oracle. The root cause is `compile_json_path()` converting numeric strings to array index notation (`[N]`) instead of object key notation (`."N"`). For example, `data__has_key='1111'` generates `$[1111]` (array index) instead of `$."1111"` (object key), causing lookups to fail when the JSON object has numeric string keys.

## v1 Patch

- Files changed: `django/db/models/fields/json.py`
- Behavioral change: In `HasKeyLookup.as_sql()`, simple string RHS keys now use `json.dumps()` for object key notation instead of `compile_json_path()`. `KeyTransformIsNull.as_sqlite()` and `as_oracle()` decoupled from `HasKey` to preserve array index semantics for `key__isnull` lookups.
- Public tests run: `model_fields.test_jsonfield` - 87 tests, all pass (8 skipped)

## v1 Score

FAIL_TO_PASS: 2 / 2
PASS_TO_PASS: 78 / 78
Resolved: true

## Review Artifacts

- review/FINDINGS.md
- review/ITERATION_GUIDANCE.md

## Key Review Findings

1. **Issue A**: `KeyTransformExact.as_oracle()` also creates `HasKey` internally (for `value__key=None` checks). The v1 change to `HasKey.as_sql()` would incorrectly change numeric key navigation on Oracle from array index to object key.
2. **Issue B**: `KeyTransformIsNull.as_oracle()` returns `tuple(params) + tuple(params)` which doubles bind params. Should be `tuple(params)`.
3. **No issues found** with the core fix, SQLite path, or MySQL path.

## v2 Patch

- Files changed: `django/db/models/fields/json.py`
- Behavioral change: Same core fix as v1, plus Oracle-specific correctness improvements.
- Difference from v1: (1) Fixed doubled params in `KeyTransformIsNull.as_oracle()`. (2) Decoupled `KeyTransformExact.as_oracle()` from `HasKey` to preserve array index semantics for key transforms.
- Why this follows from the review: Issue A identified that `KeyTransformExact.as_oracle()` would produce incorrect paths for numeric keys. Issue B identified a params duplication bug.

## v2 Score

FAIL_TO_PASS: 2 / 2
PASS_TO_PASS: 78 / 78
Resolved: true

## Delta

FAIL_TO_PASS delta: 0
PASS_TO_PASS delta: 0
Resolved delta: unchanged

## Did the Review Help?

1. Did v2 improve the bug-revealing tests? No change - both v1 and v2 pass 2/2.
2. Did v2 preserve regressions better or worse than v1? Same - both pass 78/78.
3. Did v2 get a worse total score? No.
4. If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both? N/A - v2 did not get worse.
5. Was the v2 change justified by the review artifacts? Yes - the review correctly identified real bugs (params duplication, HasKey misuse in KeyTransformExact.as_oracle) that were fixed in v2. These are genuine correctness improvements even though they don't affect the evaluator score.
6. Did the review overgeneralize the desired behavior? No - the review correctly identified which changes were safe and which were risky, and recommended conservative changes only.
7. What should be changed in the review process for regression-heavy SWE-bench tasks? The review was appropriately conservative. For this instance, the core fix was simple and correct, so the review focused on identifying secondary issues in related code paths. The "do not change" recommendations (compile_json_path, LHS path, KeyTransform-derived RHS) were all correct and helped avoid unnecessary risk.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
