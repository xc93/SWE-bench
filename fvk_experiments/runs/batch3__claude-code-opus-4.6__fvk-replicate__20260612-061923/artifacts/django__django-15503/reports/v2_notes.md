# v2 Notes

## How v2 Differs from v1

v2 makes exactly one change from v1: in `HasKeyLookup.as_sql()`, the non-KeyTransform RHS path construction changes from `json.dumps(key)` to `json.dumps(str(key))`.

This wraps the key in `str()` before JSON serialization to ensure consistent quoted notation even when the key is passed as a Python integer (e.g., `has_key=0`).

## Which FVK Finding Caused the Change

Finding 4 in `fvk/FINDINGS.md` identified that `json.dumps(0)` produces `"0"` (unquoted), making the path `$.0`, while `json.dumps(str(0))` produces `'"0"'`, making the path `$."0"` (quoted). While both are functionally equivalent in SQLite/MySQL/Oracle JSON path syntax, the quoted form is more explicit and defensive.

## Regression Risks v2 Avoids

1. `str()` is a no-op on strings, so no change for the common case (`has_key='foo'`, `has_key='1111'`)
2. `json.dumps(str(int))` always produces a quoted string, ensuring consistent path format
3. No change to KeyTransform RHS behavior (still uses `compile_json_path`)
4. No change to `KeyTransformIsNull` (already decoupled from HasKey in v1)
5. No change to LHS path compilation, `compile_json_path`, or any other code path

## Public Tests Run

- `model_fields.test_jsonfield` full module: 87 tests, all pass (8 skipped)
