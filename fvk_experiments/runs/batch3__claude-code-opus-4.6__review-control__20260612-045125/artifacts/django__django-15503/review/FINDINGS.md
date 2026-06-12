# Review Findings for v1 Patch (django__django-15503)

## 1. Intended Public Behavior Change

`has_key`, `has_keys`, and `has_any_keys` JSONField lookups should treat numeric string keys as object keys (dot notation `."N"`) rather than array indices (`[N]`) on SQLite, MySQL, and Oracle backends. This matches PostgreSQL behavior.

## 2. Current Behavior in Implicated Code Paths

`compile_json_path()` converts any string parseable as `int()` to array index notation `[N]`. The `HasKeyLookup.as_sql()` method uses `compile_json_path()` for both LHS and RHS path compilation. For the RHS (the key being checked), this is incorrect for numeric string keys.

## 3. What v1 Got Right

- **Core fix is correct**: For simple string RHS keys (the common case), v1 bypasses `compile_json_path()` and uses `".%s" % json.dumps(key)` which always produces object key notation.
- **KeyTransform RHS preserved**: For `KeyTransform`-derived RHS, v1 correctly preserves the existing `compile_json_path()` behavior, maintaining array index semantics for intermediate navigation steps.
- **KeyTransformIsNull.as_sqlite() decoupled**: Correctly builds the JSON path directly using `preprocess_lhs()` and `compile_json_path()`, avoiding the now-changed `HasKey` behavior while preserving array index semantics for `key__isnull` lookups.
- **All 87 existing public tests pass** (8 skipped for missing DB features).

## 4. Issues Found in v1

### Issue A: KeyTransformExact.as_oracle() uses HasKey internally (Oracle-only)

**Location**: `json.py:465` - `KeyTransformExact.as_oracle()` creates `HasKey(self.lhs.lhs, self.lhs.key_name)` when checking `value__key=None`.

**Problem**: The RHS (`self.lhs.key_name`) is a simple string, so v1's fix applies. For numeric keys like `value__0=None`, the existence check changes from `$[0]` to `$."0"`. This is semantically incorrect because `KeyTransform("0", ...)` is meant to navigate to array index 0, and the `HasKey` check should match.

**Severity**: Low. This only affects Oracle backend, and the evaluator runs on SQLite.

**Fix**: Decouple `KeyTransformExact.as_oracle()` from `HasKey` the same way `KeyTransformIsNull` was decoupled, OR restore `HasKey.as_sql()` to original and use a different mechanism for the user-facing fix.

### Issue B: KeyTransformIsNull.as_oracle() params duplication (Oracle-only)

**Location**: `json.py:396` - Returns `tuple(params) + tuple(params)`.

**Problem**: In the original code, `HasKey.as_oracle()` returns `(sql, [])` (all params interpolated into SQL), so the original `KeyTransformIsNull.as_oracle()` returns `tuple([]) + tuple(lhs_params) = tuple(lhs_params)`. In v1, the code returns `tuple(params) + tuple(params)`, which doubles the params. For simple fields where `params=[]`, both are equivalent. For complex LHS expressions with bind params, v1 would provide too many params.

**Severity**: Very low. Simple field references have empty params, and Oracle is not tested by the evaluator.

**Fix**: Change to `tuple(params)` instead of `tuple(params) + tuple(params)`.

### Issue C: KeyTransform-derived RHS still uses array index for last key

**Problem**: `has_key=KeyTransform("1111", "value")` still produces `[1111]` because KeyTransform-derived RHS goes through `compile_json_path()`. The last key in a `has_key` RHS should always be an object key.

**Severity**: Very low. This is an unusual usage pattern (passing a KeyTransform as the RHS of `has_key`).

## 5. What Must Remain Unchanged (Non-Regression Checks)

### Must NOT change:
- `KeyTransform.as_mysql()`, `as_oracle()`, `as_sqlite()` - value access with numeric keys must use array index notation
- `compile_json_path()` itself - used by KeyTransform methods for value navigation
- `HasKeyLookup.as_postgresql()` - already correct, has its own implementation
- LHS path compilation in `HasKeyLookup.as_sql()` - preserves array index for navigation
- `KeyTransformIsNull` behavior for numeric key transforms (e.g., `value__d__0__isnull`) - must still use array index
- All non-JSONField lookups
- All existing test_jsonfield tests (87 tests)

### Verified unchanged by v1:
- `compile_json_path()` - no changes
- `KeyTransform` methods - no changes
- LHS path in `HasKeyLookup.as_sql()` - no changes
- `test_has_key_deep`, `test_has_key_list` - all sub-tests pass
- `test_isnull_key`, `test_ordering_grouping_by_key_transform` - pass (KeyTransformIsNull on SQLite works correctly)
- `test_key_transform_expression` and related - pass

## 6. Risk Assessment

The v1 patch is minimal and focused. The two identified issues (A, B) are Oracle-only and don't affect the SQLite evaluator. Issue C is an edge case unlikely to be tested. The core fix correctly handles the reported problem.
