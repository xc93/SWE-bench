# FINDINGS — django__django-15503

## Finding 1 — v1 correctly fixes has_key RHS for plain values

**Evidence:** In `HasKeyLookup.as_sql()`, v1 changes the non-KeyTransform RHS branch from `compile_json_path(rhs_key_transforms, include_root=False)` to `.%s % json.dumps(key)`.

**Classification:** Correct fix for the reported bug.

**Verification:** `json.dumps('1111')` → `'"1111"'`, so `.%s` → `."1111"`. For non-numeric keys like `'foo'`, `json.dumps('foo')` → `'"foo"'`, so `."foo"`. Both are correct JSON path notation for object key access.

## Finding 2 — v1 correctly preserves KeyTransform RHS behavior

**Evidence:** When `isinstance(key, KeyTransform)` is True, v1 still uses `compile_json_path(rhs_key_transforms, include_root=False)`. This preserves the existing behavior for `F()` expressions and nested KeyTransform paths where intermediate elements may be legitimate array indices.

**Classification:** Correct preservation of existing behavior.

**Test coverage:** `test_has_key_list`, `test_has_key_deep` cover this path with `KeyTransform(1, ...)` and `F("value__1__b")`.

## Finding 3 — v1 correctly decouples KeyTransformIsNull from HasKey

**Evidence:** `KeyTransformIsNull.as_sqlite()` and `KeyTransformIsNull.as_oracle()` previously created `HasKey` instances internally. Since v1 changes how `HasKey.as_sql()` handles plain string keys, the old `KeyTransformIsNull` code would break: `value__d__0__isnull=False` would generate `$."d"."0"` instead of `$."d"[0]`.

v1 fixes this by making `KeyTransformIsNull` build its SQL directly using `preprocess_lhs()` + `compile_json_path()`, bypassing `HasKey` entirely.

**Classification:** Correct regression prevention.

**Verification:** The direct path uses `compile_json_path(key_transforms)` which correctly treats `"0"` as array index `[0]` for navigation purposes.

## Finding 4 — Edge case: `json.dumps(key)` when key is an integer

**Evidence:** For `has_key`, `prepare_rhs = False`, so `self.rhs` could be an integer (e.g., `has_key=0`). In v1, `json.dumps(0)` produces `"0"` (no quotes), making the path `.0` instead of `."0"`.

**Classification:** Potential edge case concern.

**Analysis:** In practice, `has_key` is typically called with string keys. When called with an integer, `json.dumps(0)` → `"0"`, and the path becomes `$.0` which in JSON path syntax is equivalent to `$."0"` (unquoted key access). SQLite's `JSON_TYPE` function accepts both forms. However, for robustness, wrapping in `str()` first (`json.dumps(str(key))`) would be safer.

**Risk assessment:** Low. The `has_keys` and `has_any_keys` already convert to strings via `get_prep_lookup`. Only `has_key` with an integer literal is affected, and JSON path `.0` works in practice.

## Finding 5 — No MySQL-specific KeyTransformIsNull issue

**Evidence:** `KeyTransformIsNull` has `as_sqlite` and `as_oracle` methods but no `as_mysql`. On MySQL, `KeyTransformIsNull` falls through to the default `IsNull` behavior (from `lookups.IsNull`), which does NOT use `HasKey` internally.

**Classification:** No action needed. MySQL is not affected by the `KeyTransformIsNull` decoupling change.

## Finding 6 — v1 does not modify compile_json_path

**Evidence:** `compile_json_path()` is unchanged. It is shared between `KeyTransform` (for navigation) and other callers. Keeping it unchanged avoids any risk of breaking JSON path navigation.

**Classification:** Correct architectural choice.

## Proof-derived Finding — No spec-difficulty signal

The fix maps cleanly to a simple rule: has_key lookups should always use object key notation for the RHS. There is no awkward case split or unclear edge case. This is a clean specification with a straightforward implementation.
