# Review-Control SWE-bench Experiment: django__django-15629

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=201&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-15629
- Base commit: 694cf458f16b8d340a3195244196980b2dec34fd
- Base commit URL: https://github.com/django/django/commit/694cf458f16b8d340a3195244196980b2dec34fd
- Version: 4.1
- Difficulty: 1-4 hours

## Evaluator Shape

- FAIL_TO_PASS: 2
- PASS_TO_PASS: 115
- Official resolved condition: 2/2 FAIL_TO_PASS and 115/115 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

When a CharField/TextField primary key has `db_collation` set, foreign key columns referencing that PK are not created with the same collation. This causes MySQL foreign key constraint errors because the collation of the FK column must match the PK column. The issue requires propagating `db_collation` from primary key fields to their referencing foreign key fields, both during column creation and when the PK's collation is altered.

## v1 Patch

- Files changed: `django/db/models/fields/related.py`
- Behavioral change: Added `db_collation` property to ForeignKey that proxies target field's db_collation, and updated `db_parameters()` to include the collation in its return dict. This handles FK column creation with correct collation.
- Public tests run: schema (179 OK), migrations (657 OK), model_fields (430 OK)

## v1 Score

FAIL_TO_PASS: 1 / 2
PASS_TO_PASS: 115 / 115
Resolved: false

## Review Artifacts

- review/FINDINGS.md
- review/ITERATION_GUIDANCE.md

## Key Review Findings

1. **Base schema editor `_alter_field` misses collation changes**: The `drop_foreign_keys` condition only checks `old_type != new_type`, so collation-only changes on a PK don't trigger FK column updates. The `rels_to_update` loop also only calls `_alter_column_type_sql`, not `_alter_column_collation_sql`.

2. **SQLite backend overrides `_alter_field` entirely**: The SQLite `_alter_field` at line 425 has its own FK rebuild logic that also only checks `old_type != new_type`. Since the evaluator runs on SQLite, changes to the base `_alter_field` are insufficient — the SQLite override must also be fixed.

Finding #2 was discovered during the iterative review process when the initial v2 (with only base schema editor changes) still scored 1/2.

## v2 Patch

- Files changed: `django/db/models/fields/related.py`, `django/db/backends/base/schema.py`, `django/db/backends/sqlite3/schema.py`
- Behavioral change: In addition to v1's FK collation property, v2 ensures that when a PK's collation changes, all FK columns referencing it are also updated — both in the base schema editor (for MySQL, PostgreSQL, Oracle) and the SQLite backend (which has its own table-rebuild logic).
- Difference from v1: Added collation-change awareness to `drop_foreign_keys` condition and `rels_to_update` loop in base schema editor, and to the related-table rebuild condition in SQLite's `_alter_field`.
- Why this follows from the review: The review identified that v1 only handled FK column creation but not FK column alteration when the PK's collation changes, and that the SQLite backend needed a separate fix.

## v2 Score

FAIL_TO_PASS: 2 / 2
PASS_TO_PASS: 115 / 115
Resolved: true

## Delta

FAIL_TO_PASS delta: +1
PASS_TO_PASS delta: 0
Resolved delta: improved (false → true)

## Did the Review Help?

1. **Did v2 improve the bug-revealing tests?** Yes. v2 went from 1/2 to 2/2 FAIL_TO_PASS.

2. **Did v2 preserve regressions better or worse than v1?** Same. Both v1 and v2 score 115/115 PASS_TO_PASS.

3. **Did v2 get a worse total score?** No. v2 is strictly better.

4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — v2 improved.

5. **Was the v2 change justified by the review artifacts?** Yes. The review correctly identified that `_alter_field` in the schema editor needed collation-change awareness. The SQLite backend fix was discovered during the iterative process when the initial schema editor changes weren't sufficient.

6. **Did the review overgeneralize the desired behavior?** No. The review correctly scoped changes to the minimum needed: collation propagation for FK columns in both creation and alteration paths.

7. **What should be changed in the review process for regression-heavy SWE-bench tasks?** The initial review missed the SQLite backend override — a pattern where the backend completely replaces the base class method. For Django tasks, the review should explicitly check all backend-specific overrides of the modified methods (SQLite, MySQL, PostgreSQL, Oracle) to ensure the fix covers all code paths. A checklist of "which backends override this method?" would have caught the SQLite issue earlier.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
