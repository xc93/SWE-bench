# ITERATION GUIDANCE — django__django-15503

## v1 Assessment

v1 scores 2/2 FAIL_TO_PASS and 78/78 PASS_TO_PASS (fully resolved). The patch is correct and minimal.

## What v1 Got Right

1. Only changes `HasKeyLookup.as_sql()` RHS compilation for non-KeyTransform keys
2. Preserves KeyTransform RHS behavior (compile_json_path with array indices)
3. Decouples `KeyTransformIsNull` from `HasKey` to avoid regression from the RHS change
4. Does not modify `compile_json_path()`, avoiding risk to KeyTransform navigation
5. Does not affect PostgreSQL behavior (as_postgresql has its own path)

## What v1 Might Miss

### Edge case: integer keys in has_key
`has_key=0` (integer, not string) passes through `json.dumps(0)` → `"0"` (unquoted in JSON), resulting in path `$.0`. While this works in practice, `json.dumps(str(0))` → `'"0"'` would produce `$."0"` (quoted), which is more explicit. However, `HasKeys.get_prep_lookup()` already converts to strings, so only `HasKey` (not `HasKeys`/`HasAnyKeys`) is affected.

**Risk:** Very low. `$.0` and `$."0"` are equivalent in SQLite, MySQL, and Oracle JSON path syntax.

## Recommended v2 Changes

Since v1 is fully resolved, v2 should be conservative:

1. **Consider**: wrapping the key in `str()` before `json.dumps()` for robustness with integer keys: `json.dumps(str(key))` instead of `json.dumps(key)`. This makes the path always use quoted notation.

2. **Do NOT**:
   - Modify `compile_json_path()` — it's shared and correct for navigation
   - Add parameters to `compile_json_path()` — unnecessary complexity
   - Change `as_postgresql()` — already correct
   - Change any other lookup classes — unrelated to the issue

## Forbidden Changes

- Any change to `compile_json_path()` function body
- Any change to `KeyTransform.as_sqlite/mysql/oracle()` methods
- Any change to `HasKeyLookup.as_postgresql()`
- Any change to `DataContains`, `ContainedBy`, or other non-has_key lookups
- Any change that would affect the LHS path compilation in `HasKeyLookup.as_sql()`

## Risk Assessment

v1 is already fully resolved. The only risk in v2 is introducing a regression. The recommended change (wrapping key in str()) is extremely low-risk but could be unnecessary. If v1 is sufficient, v2 should be identical or nearly identical to avoid any regression risk.
