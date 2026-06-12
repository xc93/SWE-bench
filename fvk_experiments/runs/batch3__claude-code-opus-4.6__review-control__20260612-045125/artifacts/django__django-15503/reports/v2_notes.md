# v2 Notes

## How v2 Differs from v1

v2 makes two additional correctness fixes on top of v1's core change:

### Change 1: Fix KeyTransformIsNull.as_oracle() params (Review Issue B)

Changed `tuple(params) + tuple(params)` to `tuple(params)` in the isnull=True return path. The original code returned `tuple([]) + tuple(lhs_params)` because `HasKey.as_oracle()` interpolates all params into SQL (returning empty params). Since v1's rewrite builds the SQL directly, `params` already represents the bind params correctly and should not be doubled.

### Change 2: Decouple KeyTransformExact.as_oracle() from HasKey (Review Issue A)

`KeyTransformExact.as_oracle()` previously created `HasKey(self.lhs.lhs, self.lhs.key_name)` to check key existence when comparing with NULL. Since v1 changed `HasKey.as_sql()` to always use object key notation for simple string keys, this internal usage would incorrectly change numeric key navigation (e.g., `value__0=None`) from array index `$[0]` to object key `$."0"` on Oracle.

v2 builds the `JSON_EXISTS` SQL directly using `preprocess_lhs()` and `compile_json_path()`, preserving array index semantics for key transforms.

## Which Review Findings Caused the Change

- Issue A (KeyTransformExact.as_oracle() compatibility) -> Change 2
- Issue B (params duplication) -> Change 1

## Regression Risks v2 Is Designed to Avoid

- All changes are in Oracle-only code paths, so SQLite and MySQL behavior is identical to v1
- The core has_key fix (in `HasKeyLookup.as_sql()`) is unchanged from v1
- The `KeyTransformIsNull.as_sqlite()` fix is unchanged from v1
- All 87 existing public tests continue to pass
