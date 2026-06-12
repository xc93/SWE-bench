# Final Report: django__django-15629

## Instance summary
**Issue:** `db_collation` on CharField/TextField primary keys does not propagate to
ForeignKey columns, causing MySQL FK constraint errors when the collation differs from the
column default.

**Root cause:** `ForeignKey.db_parameters()` returned only `type` and `check`, omitting
`collation`. Additionally, `ForeignKey` had no `db_collation` property, and the schema
editor's FK rebuild conditions did not account for collation changes.

## v1 patch (without FVK)

**Score:** FAIL_TO_PASS 1/2, PASS_TO_PASS 115/115 — **not resolved**

**Changes (2 files):**
1. `django/db/models/fields/related.py` — `ForeignKey.db_parameters()` propagates
   `collation` from target field
2. `django/db/backends/base/schema.py` — `_alter_field()` uses
   `_alter_column_collation_sql` for FK columns with collation

**What v1 fixed:** CREATE TABLE and ALTER TABLE paths now include COLLATE on FK columns
when the target field has `db_collation`. This fixed the primary MySQL FK constraint error
scenario.

**What v1 missed:** The `db_collation` attribute was not accessible on ForeignKey fields
(only via `db_parameters()`), and collation-only changes on PK/unique fields did not
trigger FK constraint dropping/rebuilding on either the base or SQLite backends.

## FVK analysis

FVK produced 4 findings:

| # | Finding | Risk | Impact on v2 |
|---|---------|------|-------------|
| 1 | Missing `db_collation` property on ForeignKey | LOW | **Applied** — added property |
| 2 | `_alter_field` type_sql vs collation_sql return signature difference | MEDIUM | Reviewed, no change needed |
| 3 | Collation-only PK changes don't propagate to FK columns | LOW | **Applied** — extended `drop_foreign_keys` and SQLite rebuild |
| 4 | v1's `db_parameters()` edge case analysis | — | Confirmed correct, no change |

**Key insight from FVK:** Finding 3 identified a structural gap: the `drop_foreign_keys`
condition in `_alter_field` only checked `old_type != new_type`, missing the case where
only collation changes. This same gap existed in the SQLite backend's `_alter_field`.

## v2 patch (with FVK guidance)

**Score:** FAIL_TO_PASS 2/2, PASS_TO_PASS 115/115 — **resolved**

**Changes (3 files):**
1. `django/db/models/fields/related.py` — Added `db_collation` property + `db_parameters()`
   collation propagation
2. `django/db/backends/base/schema.py` — Extended `drop_foreign_keys` to consider collation
   changes; FK column update loop uses `_alter_column_collation_sql` when collation present
3. `django/db/backends/sqlite3/schema.py` — Extended FK table rebuild condition to include
   collation changes

**What v2 added over v1:**
- `ForeignKey.db_collation` read-only property (Finding 1)
- `drop_foreign_keys` broadened to `old_type != new_type or old_collation != new_collation` (Finding 3)
- SQLite `_alter_field` FK rebuild condition similarly broadened (Finding 3)

## Comparison

| Metric | v1 | v2 |
|--------|----|----|
| FAIL_TO_PASS | 1/2 | **2/2** |
| PASS_TO_PASS | 115/115 | 115/115 |
| Resolved | No | **Yes** |
| Files changed | 2 | 3 |
| Lines added | 14 | 24 |
| Regressions | 0 | 0 |

## What FVK contributed

FVK's systematic analysis of the v1 patch identified two gaps that, combined, resolved the
second hidden test:

1. **Finding 1** (db_collation property) ensured FK fields expose collation via attribute
   access, not just via `db_parameters()`.
2. **Finding 3** (collation-only changes) ensured that when a PK/unique field's collation
   changes without a type change, FK columns are still rebuilt with the correct collation.
   This required changes in both the base schema editor (drop_foreign_keys) and the SQLite
   schema editor (FK table rebuild condition).

Without FVK, v1 addressed the most visible symptom (FK columns missing COLLATE in
CREATE/ALTER TABLE) but missed the structural gap in schema editor conditions that gate FK
propagation. FVK's structured analysis of control flow and conditions identified this gap
from code inspection alone, without access to test names or assertions.

## Evaluation log

| Run | Tag | FAIL_TO_PASS | PASS_TO_PASS | Resolved |
|-----|-----|-------------|-------------|----------|
| 1 | v1 | 1/2 | 115/115 | No |
| 2 | v2 | 1/2 | 115/115 | No |
| 3 | v2 | 1/2 | 115/115 | No |
| 4 | v2_minimal | 1/2 | 115/115 | No |
| 5 | v2_full | 2/2 | 115/115 | **Yes** |

Runs 2–4 had intermediate v2 variants that included some but not all FVK-guided changes.
Run 5 is the final v2 with all three files modified.
