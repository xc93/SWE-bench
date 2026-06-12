# v2 Notes

## How v2 Differs from v1

v2 uses a completely different approach: a **proactive type check** at the top of `__array_ufunc__` instead of v1's reactive try/except around the conversion loop.

### v1 approach (reactive)
Wrapped the conversion loop in try/except for `(TypeError, ValueError)` and returned `NotImplemented` on error. This only caught errors in one specific code path.

### v2 approach (proactive)
Added a type check at the top of `__array_ufunc__` that examines all inputs and outputs BEFORE any processing. For each input/output:
1. Skip if it's a recognized type: `np.ndarray` (includes Quantity, Column), `np.generic` (numpy scalars), or `numbers.Number` (int, float, complex)
2. If unrecognized, check if it defines `__array_ufunc__` — if yes, return `NotImplemented`; if no (plain dicts, strings, etc.), let normal processing handle it (preserving error messages)

## Which Review Findings Caused the Change

1. **Finding: v1 missed the `converters_and_unit` error path** — v1 only caught errors in the conversion loop, missing errors from `converters_and_unit` for duck types without `.unit`. The proactive check handles ALL failure paths because it rejects unrecognized types before ANY processing.

2. **Finding: v1 caught too broadly** — v1's unguarded `(TypeError, ValueError)` catch masked errors for some recognized-type edge cases (causing 4 PASS_TO_PASS regressions). The proactive check avoids this entirely: it never changes behavior for recognized types.

3. **Finding: need to preserve error messages for plain objects** — The `__array_ufunc__` filter ensures dicts, strings, and other plain Python objects still trigger astropy's descriptive error messages instead of generic Python TypeErrors.

## Regression Risks v2 is Designed to Avoid

- **No error handling changes for recognized types**: the check is purely additive; existing code paths are unchanged
- **Preserves error messages for non-array types**: only objects with `__array_ufunc__` get NotImplemented; plain objects get normal error handling
- **Handles both inputs and outputs**: checks `out` kwargs too, preventing errors from `check_output`
- **Minimal code change**: 15 lines added, 0 lines modified in existing logic
