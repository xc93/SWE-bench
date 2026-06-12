# v2 Notes

## How v2 Differs from v1

v2 takes a fundamentally different approach from v1. Instead of catching errors in the converter loop after the fact, v2 performs an early-return check at the TOP of `__array_ufunc__` before any conversion is attempted.

### The Early-Return Strategy

At the start of `__array_ufunc__`, v2 scans all inputs and outputs. If any input/output:
1. Is NOT an ndarray subclass (`not isinstance(x, np.ndarray)`)
2. BUT defines `__array_ufunc__` (`getattr(x, '__array_ufunc__', None) is not None`)

Then `NotImplemented` is returned immediately, before `converters_and_unit` or the converter loop runs.

This detects "duck types" — objects that participate in numpy's dispatch protocol but are not ndarray subclasses. Such objects should handle the operation themselves via their own `__array_ufunc__`.

### Why This Works Better Than v1's try/except

- **No regressions**: Since no conversion is attempted for duck types, there's no risk of masking legitimate errors (UnitConversionError, TypeError) for recognized types.
- **Covers all error paths**: v1 only caught errors in the converter loop. The converters_and_unit call and check_output call could also fail for duck types. The early-return avoids all of them.
- **Simpler logic**: One check at the top vs. multiple guarded try/except blocks.

### What passes through (no early return)

- `np.ndarray` and subclasses (Quantity, Column) — handled normally
- Scalars (int, float, complex, np.generic) — no `__array_ufunc__` attribute, handled normally
- Lists/tuples — no `__array_ufunc__` attribute, handled normally

## FVK Findings That Motivated the Change

- **SPEC.md**: Identified two error paths (converters_and_unit + converter loop) that both needed handling
- **FINDINGS.md Finding 1**: v1 catches too broadly — UnitConversionError is ValueError subclass, masking real errors
- **FINDINGS.md Finding 2**: v1 misses converters_and_unit errors entirely
- **FINDINGS.md Finding 3**: Duck type detection via `__array_ufunc__` presence — the key insight
- **FINDINGS.md Finding 5**: check_output errors for output duck types — also handled by early-return
- **PROOF_OBLIGATIONS.md**: Defined both bug-fix obligations (O1, O2) and non-regression obligations (R1-R7)

The FVK analysis revealed that the problem was structural: trying to catch errors from multiple call sites while guarding against regressions was inherently fragile. The early-return approach, informed by Finding 3's duck type detection criterion, elegantly addresses all obligations at once.

## Regression Risks v2 Avoids

1. **Quantity + Column**: Column IS ndarray → no early return → normal path
2. **Quantity + ndarray**: ndarray IS ndarray → no early return → normal path
3. **Quantity + scalar**: scalars lack `__array_ufunc__` → no early return → normal path
4. **Quantity + list**: lists lack `__array_ufunc__` → no early return → normal path
5. **Unsupported ufuncs (all-Quantity)**: all Quantity are ndarray → no early return → TypeError raised normally
6. **Unit incompatibility (Quantity + Quantity)**: all ndarray → no early return → UnitConversionError raised normally
