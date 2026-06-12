# SPEC — django__django-15503

## Public Issue

`has_key`, `has_keys`, and `has_any_keys` JSONField lookups don't handle numeric keys on SQLite, MySQL, and Oracle.

## Intended Behavior Change

For `has_key`, `has_keys`, and `has_any_keys` lookups on SQLite, MySQL, and Oracle backends:
- When the RHS key is a plain value (string or integer, not a KeyTransform), it must ALWAYS be treated as a JSON object key name, never as an array index.
- Example: `data__has_key='1111'` must generate `$."1111"` (object key), not `$[1111]` (array index).

## Current (Buggy) Behavior

`compile_json_path()` converts any numeric-looking string to an integer array index:
- `compile_json_path(['1111'], include_root=False)` → `[1111]` (wrong for has_key)
- `compile_json_path(['foo'], include_root=False)` → `."foo"` (correct)

This is correct for `KeyTransform` (navigating JSON structures), but incorrect for has_key (checking key existence in objects).

## Code Paths Affected

1. `HasKeyLookup.as_sql()` (line 175) — called by `as_sqlite`, `as_mysql`, and `as_oracle`
2. `KeyTransformIsNull.as_sqlite()` (line 403) — internally uses `HasKey` for SQL generation
3. `KeyTransformIsNull.as_oracle()` (line 392) — internally uses `HasKey` for SQL generation

## Code Paths That Must NOT Change

1. `compile_json_path()` — shared by `KeyTransform.as_sqlite/mysql/oracle()`. Must keep treating numeric strings as array indices for navigation.
2. `HasKeyLookup.as_postgresql()` — already works correctly; uses different operator-based approach.
3. `KeyTransform.as_sqlite/mysql/oracle()` — navigation through JSON structures. `data__0` must still access array index 0.
4. All other JSON lookups: DataContains, ContainedBy, JSONExact, etc.
5. `HasKeyLookup.as_sql()` with KeyTransform RHS — intermediate path elements may be legitimate array indices.

## Postconditions

For every backend (SQLite, MySQL, Oracle):
- `data__has_key='foo'` → path fragment `."foo"` (object key)
- `data__has_key='1111'` → path fragment `."1111"` (object key, NOT `[1111]`)
- `data__has_key=0` → path fragment `."0"` (object key, since json.dumps(0) wrapped in str)
- `data__has_keys=['1', '2', 'abc']` → fragments `."1"`, `."2"`, `."abc"`
- `data__has_any_keys=['1', 'abc']` → fragments `."1"`, `."abc"`
- `data__has_key=KeyTransform("b", KeyTransform(1, "value"))` → path `[1]."b"` (KeyTransform path preserved)
- `value__d__0__isnull=False` → path `$."d"[0]` (navigation, NOT `$."d"."0"`)
