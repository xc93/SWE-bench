# Final Report: astropy__astropy-13977

## Instance Summary

**Issue**: `Quantity.__array_ufunc__()` raises `ValueError` when inputs are incompatible duck types, instead of returning `NotImplemented` to allow Python's operator dispatch to fall back to the other operand's reflected method.

**Root cause**: In `__array_ufunc__`, all inputs are processed through unit converters without type checking. When a duck type (e.g., a custom `NDArrayOperatorsMixin` subclass) cannot be converted by `_condition_arg()`, a `ValueError` is raised. This prevents the duck type's own `__array_ufunc__` from handling the operation.

## v1 Patch

**Approach**: Wrapped the converter application loop in `try/except (ValueError, TypeError)` that returns `NotImplemented` on any conversion failure.

**Score**: FAIL_TO_PASS 12/20, PASS_TO_PASS 318/322 — **not resolved**

**Why it fell short**:
- Missed errors from `converters_and_unit()` (8 FAIL_TO_PASS remaining) — duck types can trigger `TypeError` from `can_have_arbitrary_unit()` or `UnitConversionError` from the False-converter block, both before the converter loop runs.
- Caught too broadly (4 PASS_TO_PASS regressions) — since `UnitConversionError` extends `ValueError`, the unconditional catch masked legitimate unit errors between recognized types (e.g., `Quantity(m) + Quantity(s)`).

## FVK Analysis

The Formal Verification Kit produced four artifacts:

1. **SPEC.md**: Defined the intended behavior change and identified two error paths (converters_and_unit at line 643, converter loop at line 670), plus the critical constraint that `UnitConversionError(UnitsError(ValueError))`.

2. **FINDINGS.md**: Six findings, most important:
   - Finding 1: v1 catches too broadly (UnitConversionError is ValueError subclass)
   - Finding 2: v1 misses converters_and_unit errors
   - Finding 3: Duck type detection criterion — `__array_ufunc__` present but not ndarray subclass

3. **PROOF_OBLIGATIONS.md**: Two bug-fix obligations (O1: converter loop, O2: converters_and_unit) and seven non-regression obligations (R1-R7: unit errors, unsupported ufuncs, Column/ndarray/scalar operations).

4. **ITERATION_GUIDANCE.md**: Prescribed specific changes — guarded try/except at both error sites.

## v2 Patch

**Approach**: Early-return at the top of `__array_ufunc__`. Before any conversion, scan all inputs and outputs: if any has `__array_ufunc__` defined but is NOT an ndarray subclass, return `NotImplemented` immediately.

**Score**: FAIL_TO_PASS 20/20, PASS_TO_PASS 322/322 — **resolved**

**Why it succeeded**: The early-return avoids all error paths entirely for duck types — no conversion is attempted, so there's no risk of masking legitimate errors. Recognized types (ndarray, Quantity, Column, scalars, lists) all pass through to the normal path unchanged.

## v1 vs v2 Comparison

| Metric         | v1         | v2          | Delta   |
|----------------|------------|-------------|---------|
| FAIL_TO_PASS   | 12/20      | 20/20       | +8      |
| PASS_TO_PASS   | 318/322    | 322/322     | +4      |
| Resolved        | false      | true        | +1      |
| Lines changed  | 9          | 15          | +6      |
| Files modified | 1          | 1           | 0       |

## FVK Contribution

The FVK analysis was decisive in moving from v1 to v2:

1. **Identified the structural problem**: v1's try/except approach had to simultaneously (a) catch errors for duck types and (b) not catch errors for recognized types. With `UnitConversionError` extending `ValueError`, this was inherently fragile.

2. **Provided the detection criterion**: Finding 3 established that `__array_ufunc__` presence + not-ndarray is the correct distinguisher for duck types. This criterion is both necessary and sufficient.

3. **Mapped all error paths**: The SPEC and FINDINGS identified that errors could come from `converters_and_unit`, the converter loop, and `check_output` — too many sites for targeted catch blocks.

4. **Motivated the architectural shift**: The combination of multiple error paths and the UnitConversionError inheritance constraint made it clear that catching errors reactively was the wrong approach. The early-return strategy, checking types proactively, was the natural solution.

Without FVK, the v1 try/except approach would have required multiple iterations of adding guards and discovering new error paths. FVK mapped the full problem space in one pass, enabling a clean solution.

## v2 Patch Content

```diff
diff --git a/astropy/units/quantity.py b/astropy/units/quantity.py
index b98abfa..4ef73ec 100644
--- a/astropy/units/quantity.py
+++ b/astropy/units/quantity.py
@@ -636,13 +636,28 @@ class Quantity(np.ndarray):
         result : `~astropy.units.Quantity`
             Results of the ufunc, with the unit set properly.
         """
+        # If any input or output is not something Quantity can handle —
+        # i.e., it defines __array_ufunc__ but is not an ndarray (sub)class —
+        # return NotImplemented so the other type gets a chance.
+        out = kwargs.get("out", None)
+        for inp in inputs:
+            if (not isinstance(inp, np.ndarray)
+                    and getattr(inp, '__array_ufunc__', None) is not None):
+                return NotImplemented
+        if out is not None:
+            out_args = out if isinstance(out, tuple) else (out,)
+            for out_ in out_args:
+                if out_ is not None:
+                    if (not isinstance(out_, np.ndarray)
+                            and getattr(out_, '__array_ufunc__', None) is not None):
+                        return NotImplemented
+
         # Determine required conversion functions -- to bring the unit of the
         # input to that expected (e.g., radian for np.sin), or to get
         # consistent units between two inputs (e.g., in np.add) --
         # and the unit of the result (or tuple of units for nout > 1).
         converters, unit = converters_and_unit(function, method, *inputs)

-        out = kwargs.get("out", None)
         # Avoid loop back by turning any Quantity output into array views.
         if out is not None:
             # If pre-allocated output is used, check it is suitable.
```
