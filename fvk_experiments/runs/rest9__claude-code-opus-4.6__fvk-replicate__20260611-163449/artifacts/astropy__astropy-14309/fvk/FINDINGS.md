# FINDINGS — astropy__astropy-14309

## Finding 1 — IndexError when args is empty (the reported bug)

**Severity**: crash (IndexError)
**Location**: `astropy/io/fits/connect.py:72`

**Input**: `identify_format("write", Table, "bububu.ecsv", None, [], {})`
**Observed**: `IndexError: tuple index out of range` at `args[0]`
**Expected**: Return `False` (the input is not FITS)

**Root cause**: The `is_fits()` function unconditionally accesses `args[0]` on the fallthrough path when `filepath` doesn't have a FITS extension. When `args` is empty, this crashes.

**v1 fix**: `return bool(args) and isinstance(args[0], ...)` — correct and minimal.

## Finding 2 — Same pattern in votable/connect.py (out of scope)

**Severity**: potential crash (same pattern)
**Location**: `astropy/io/votable/connect.py:42`

```python
return isinstance(args[0], (VOTableFile, VOTable))
```

This has the same unguarded `args[0]` access pattern. However, it is guarded by `origin == "read"`, which reduces the exposure. When `origin == "write"`, the function returns `False` before reaching this line.

**Recommendation**: Note for future fix but do NOT include in this patch. The public issue is specifically about `is_fits`, and fixing unrelated code paths risks regressions.

## Finding 3 — The fix is consistent with the registry's API contract

**Location**: `astropy/io/registry/base.py:232-233`

The API documentation says: "One or both of `path` or `fileobj` may be `None`. If they are both `None`, the identifier will need to work from `args[0]`."

This implies `args[0]` may exist, not that it always does. The identifier must handle the case where args is empty gracefully by returning `False`.

v1's `bool(args)` guard is the correct minimal implementation of this contract.

## Finding 4 — No behavioral change for valid inputs

The v1 fix is a strict guard addition. For all previously working call patterns (where `args` is non-empty), the behavior is identical:
- `bool(args)` evaluates to `True`
- `isinstance(args[0], ...)` is evaluated as before

The only behavioral change is for the previously-crashing case (empty args), which now correctly returns `False`.
