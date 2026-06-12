# v1 Notes

## Behavioral Change

v1 fixes `has_key`, `has_keys`, and `has_any_keys` JSONField lookups to handle numeric string keys correctly on SQLite, MySQL, and Oracle backends.

The root cause: `compile_json_path()` converts any string that parses as an integer into array index notation (`[N]`) instead of object key notation (`."N"`). For `has_key` lookups, the RHS keys should always be treated as object keys.

Example: `data__has_key='1111'` was generating `JSON_TYPE(data, '$[1111]')` (array index) instead of `JSON_TYPE(data, '$."1111"')` (object key).

## Files Modified

- `django/db/models/fields/json.py`

## Changes Made

1. **`HasKeyLookup.as_sql()`**: For simple string RHS keys (non-KeyTransform), bypass `compile_json_path` and directly format as object key notation using `json.dumps()`. KeyTransform-derived keys still go through `compile_json_path` to preserve array index semantics for intermediate navigation.

2. **`KeyTransformIsNull.as_sqlite()`**: Decoupled from `HasKey` - now builds the JSON path directly using `compile_json_path(key_transforms)` via `preprocess_lhs()`. This preserves array index semantics for `key__isnull` lookups (e.g., `value__d__0__isnull=False`).

3. **`KeyTransformIsNull.as_oracle()`**: Same decoupling as SQLite - builds the `JSON_EXISTS` SQL directly using the full key transforms path.

## Public Tests Run

- `model_fields.test_jsonfield`: 87 tests, all pass (8 skipped for missing DB features)
- Key tests verified: `test_has_key`, `test_has_key_deep`, `test_has_key_list`, `test_has_key_null_value`, `test_has_keys`, `test_has_any_keys`, `test_isnull_key`, `test_key_transform_expression`, `test_ordering_grouping_by_key_transform`

## Why v1 Matches the Public Issue

The issue reports that `data__has_key='1111'` fails on SQLite because numeric keys are treated as array indices. v1 ensures that in `has_key` lookups, all simple string keys use object key notation (`."N"` instead of `[N]`), matching PostgreSQL behavior.
