# Iteration Guidance for v2

## Assessment

v1 scores 2/2 FAIL_TO_PASS and 78/78 PASS_TO_PASS. The core fix is correct and complete for the common case. The issues found are all in Oracle-only code paths not tested by the evaluator.

## Recommended Changes for v2

### Change 1: Fix KeyTransformIsNull.as_oracle() params (Issue B)

**What**: Change `tuple(params) + tuple(params)` to `tuple(params)` on line 396.

**Why**: The doubled params is a bug for complex LHS expressions. Even though it doesn't affect the evaluator, it's a correctness fix with zero regression risk.

**Risk**: None. Only changes Oracle path, and the fix is strictly more correct.

### Change 2: Fix KeyTransformExact.as_oracle() HasKey usage (Issue A)

**What**: Decouple `KeyTransformExact.as_oracle()` from `HasKey` the same way `KeyTransformIsNull` was decoupled. Build the `JSON_EXISTS` SQL directly using `preprocess_lhs()` and `compile_json_path()`.

**Why**: Currently, the v1 change to `HasKey.as_sql()` affects this internal usage, changing numeric keys from array index to object key notation. This mismatch could cause incorrect results for `value__0=None` on Oracle.

**Risk**: Low. Only changes Oracle path. Must verify that the replacement produces identical SQL for non-numeric keys.

## Changes NOT Recommended for v2

### Do NOT fix KeyTransform-derived RHS (Issue C)

**Why**: Changing the last key in a KeyTransform-derived RHS to always use object key notation could break navigation through arrays. E.g., `has_key=KeyTransform("f", KeyTransform("1", KeyTransform("d", "value")))` needs `[1]` for intermediate navigation. Forcing the last key to object key notation would require splitting the path compilation, which is complex and risks regressions.

### Do NOT modify compile_json_path()

**Why**: `compile_json_path()` is used by `KeyTransform` methods for value access, where array index semantics are correct. Adding parameters to it risks confusion about when to use which mode.

### Do NOT change LHS path compilation

**Why**: The LHS path in `HasKeyLookup.as_sql()` represents navigation to a nested JSON location. Array index semantics are correct here (e.g., `value__d__1__has_key="f"` needs `$."d"[1]`).

## Conservative Approach

Given that v1 already scores perfectly, v2 should make only the smallest correctness improvements (Changes 1 and 2). Any broader changes risk breaking the passing regression tests with no scoring benefit.
