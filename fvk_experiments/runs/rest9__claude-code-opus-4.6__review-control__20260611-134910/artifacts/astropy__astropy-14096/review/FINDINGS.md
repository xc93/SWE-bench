# Review Findings for v1 Patch

## 1. Intended Public Behavior Change

When a subclassed `SkyCoord` has a property whose getter internally raises `AttributeError`, the error message should identify the real missing attribute rather than misleadingly claiming the property itself doesn't exist.

## 2. Current Behavior in Implicated Code Paths

`SkyCoord.__getattr__` is a fallback attribute handler. Python calls it when normal attribute lookup fails. The issue: when a property raises `AttributeError` internally, Python treats this as "attribute not found" and calls `__getattr__`. The `__getattr__` method then raises a *new* `AttributeError` blaming the property name, hiding the real cause.

Code path: `__getattr__` checks (in order): frame name aliases → frame_attributes → frame object attributes → transformable frames → raises generic error.

## 3. Version Implications

This issue exists in 5.1 and is unrelated to frame-specific version changes. The fix is orthogonal to frame or coordinate system changes.

## 4-7. What Must Remain Unchanged

### Regular SkyCoord attribute access
- `c.ra`, `c.dec`, `c.galactic` etc. must continue working through the existing `__getattr__` machinery.
- Frame transformations (`c.galactic`, `c.fk5`, etc.) must still work.
- Frame attributes (`obstime`, `equinox`, etc.) must still resolve correctly.
- Private attribute access (`_sky_coord_frame` etc.) must not be affected.

### Error messages for genuinely missing attributes
- `c.nonexistent` on base `SkyCoord` must still raise `AttributeError` with clear message.

### Init-time behavior
- The `"_sky_coord_frame" in self.__dict__` guard must still protect init-time lookups.

### __setattr__ and __delattr__
- Must not be affected by changes to `__getattr__`.

### Properties that work correctly
- A subclass property that does NOT raise `AttributeError` must continue returning its value normally. Such properties never trigger `__getattr__`.

### Properties raising non-AttributeError exceptions
- A property raising `ValueError`, `TypeError`, etc. must propagate that exception directly. These are not caught by Python's attribute lookup, so `__getattr__` is never called. Not affected by this patch.

## 8. What v1 Gets Right

- **Correct placement**: The descriptor check is placed at the end, after all SkyCoord-specific lookups. This ensures existing behavior is preserved for frame attributes, frame names, and transformation targets.
- **Correct MRO iteration**: Iterates through `type(self).__mro__` to find the descriptor, matching Python's own attribute resolution order.
- **Correct descriptor detection**: `hasattr(dsc, "__get__")` correctly identifies data and non-data descriptors (properties, classmethods, etc.).
- **Correct `break`**: Stops at the first match in MRO, matching Python's own resolution semantics.
- **Minimal change**: Only 10 lines added, no existing lines modified.
- **No regressions**: All 426 existing tests pass.

## 9. What v1 Might Be Missing or Overgeneralizing

### Minor concern: comment accuracy
The comment says "defined on the class" but the MRO iteration checks all classes in the hierarchy. This is correct behavior but the comment could be slightly more precise.

### Non-concern: init-time descriptor re-invocation
During init (before `_sky_coord_frame` is set), if a subclass property raises `AttributeError`, the new code would re-invoke it. This changes the error message from "no attribute 'prop'" to the real underlying error. This is actually *more* informative, not a regression.

### Non-concern: infinite recursion
Traced through the flow carefully. No infinite recursion occurs because:
1. A property's `__get__` raising `AttributeError` propagates from within `__getattr__` without triggering another `__getattr__` call for the same attribute.
2. The descriptor check finds attributes in the MRO; it doesn't re-enter `__getattr__` for the same attribute name.

### Non-concern: SkyCoord's own properties
SkyCoord properties (`frame`, `representation_type`, `shape`, etc.) all work correctly and never trigger `__getattr__` under normal usage.

## 10. Minimal Changes Justified for v2

The v1 patch is correct and minimal. The only justified change would be a minor comment wording improvement. **No behavioral changes are justified** given that v1 passes all tests.

## 11. Changes Forbidden Because They Risk Regressions

- Do NOT change the order of checks within `__getattr__` (frame name → frame_attributes → frame object → transformable → descriptor → error).
- Do NOT modify the `"_sky_coord_frame" in self.__dict__` guard.
- Do NOT change `__setattr__` or `__delattr__`.
- Do NOT add additional exception handling (try/except) around existing frame lookups.
- Do NOT change the final `AttributeError` message format for genuinely missing attributes.
- Do NOT switch to `super().__getattribute__()` approach (subtly different semantics for non-descriptor class attributes).
