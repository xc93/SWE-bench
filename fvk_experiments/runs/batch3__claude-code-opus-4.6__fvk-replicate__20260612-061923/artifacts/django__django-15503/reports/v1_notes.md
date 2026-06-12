# v1 Notes

## Problem

`has_key`, `has_keys`, and `has_any_keys` JSONField lookups use `compile_json_path()` for the right-hand side keys. `compile_json_path()` treats any numeric-looking string (e.g., `'1111'`) as an array index, generating `[1111]` instead of `."1111"`. This is correct for JSON path navigation (e.g., `data__0` accessing array index 0), but incorrect for has_key lookups where the value is a key name to check for existence.

## Behavior Change

v1 makes two changes to `django/db/models/fields/json.py`:

1. **`HasKeyLookup.as_sql()`**: For non-KeyTransform RHS values, the key is always treated as an object key name using `json.dumps()`, producing `."1111"` instead of `[1111]`. KeyTransform RHS values still use `compile_json_path()` (preserving array index behavior for navigation).

2. **`KeyTransformIsNull.as_sqlite()` and `KeyTransformIsNull.as_oracle()`**: These methods previously created an internal `HasKey` instance to generate their SQL. Since the `HasKey.as_sql()` now uses object key notation for string keys, this would break `isnull` lookups on array-indexed paths (e.g., `value__d__0__isnull=False` would generate `$."d"."0"` instead of `$."d"[0]`). These methods now build their SQL directly using `compile_json_path()`, bypassing `HasKey` entirely.

## Files Modified

- `django/db/models/fields/json.py` (3 methods changed)

## Public Tests Run

- `model_fields.test_jsonfield.TestQuerying` (65 tests): all pass (8 skipped for unsupported features)
- `model_fields.test_jsonfield` full module (87 tests): all pass (8 skipped)
- Specific has_key tests verified: test_has_key, test_has_key_null_value, test_has_key_deep, test_has_key_list, test_has_keys, test_has_any_keys

## Why v1 Matches the Issue

The issue reports that `data__has_key='1111'` fails to find objects on SQLite (and MySQL/Oracle) because the generated JSON path `$[1111]` checks for array index 1111 instead of object key `"1111"`. v1 ensures has_key lookups always use object key notation (`$."1111"`), matching PostgreSQL behavior.
