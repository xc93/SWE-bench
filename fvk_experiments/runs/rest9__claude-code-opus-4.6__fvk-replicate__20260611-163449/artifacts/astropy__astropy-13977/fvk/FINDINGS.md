# FINDINGS

## Finding 1: v1 catches too broadly at converter application

**Evidence**: v1 catches `(ValueError, TypeError)` unconditionally in the converter loop. Since `UnitConversionError` is a subclass of `ValueError`, any `UnitConversionError` raised during converter application is also caught. For recognized input types (ndarray, scalars), errors should propagate, not return NotImplemented.

**Impact**: PASS_TO_PASS regressions (4/322). Tests that expect specific errors for operations on recognized types now get NotImplemented-triggered TypeError instead.

**Fix**: Add a guard: only return NotImplemented if the failing input is NOT an ndarray. For ndarray inputs, re-raise the error.

## Finding 2: v1 doesn't handle errors from converters_and_unit

**Evidence**: `converters_and_unit()` at line 643 can raise `TypeError` (from `can_have_arbitrary_unit` at line 208) when a duck type without `.unit` is passed alongside a non-dimensionless Quantity. This happens BEFORE the converter loop, so v1's catch doesn't handle it.

**Example**: `Quantity(1, u.m) + DuckTypeWithout_unit()` → `can_have_arbitrary_unit(duck_type)` raises TypeError → propagates as TypeError.

**Impact**: 8 FAIL_TO_PASS tests unfixed.

**Fix**: Wrap `converters_and_unit` call in try/except, but only return NotImplemented if a duck type (non-ndarray with `__array_ufunc__`) is among the inputs.

## Finding 3: Duck type detection via __array_ufunc__

**Evidence**: The hint suggests checking `isinstance(io, (Quantity, ndarray, Column))`. But the try/except approach is preferred to avoid slowing the common case. The key distinguisher is: does the input have `__array_ufunc__` but is NOT an ndarray subclass? Such inputs are duck types that can potentially handle the operation themselves.

- Lists/tuples: no `__array_ufunc__` → errors should propagate
- Duck types (DuckArray): has `__array_ufunc__`, not ndarray → return NotImplemented
- Quantity/Column: has `__array_ufunc__`, IS ndarray → errors should propagate
- ndarray: IS ndarray → errors should propagate

## Finding 4: UnitConversionError for duck types without .unit

**Evidence**: When a duck type lacks `.unit`, `converters_and_unit` assigns unit=None. For non-dimensionless ufuncs, the helper returns converter=False. `can_have_arbitrary_unit(duck_type)` may return False (not all zeros), triggering `UnitConversionError` at line 200. This is NOT a TypeError, so a separate catch is needed — but since `UnitConversionError` extends `ValueError`, catching `ValueError` handles it.

The guard must distinguish this from real unit errors (e.g., `Quantity(1, u.m) + Quantity(1, u.s)`). The guard: check if a non-ndarray with `__array_ufunc__` is present.

## Finding 5: check_output errors for output duck types

**Evidence**: `check_output()` at line 652 can raise `TypeError` or `UnitTypeError` for non-Quantity outputs. If `out` is a duck type, these errors should also return NotImplemented. However, output duck types are likely a less common scenario.

## Finding 6: getattr(input_, "value", input_) behavior

**Evidence**: For duck types, `getattr(input_, "value", input_)` returns:
- DuckArray without .value → the DuckArray itself (not ndarray → triggers catch)
- DuckArray with .value returning ndarray → the ndarray (works with converter)
- Column.value → ndarray (works correctly)
- Quantity.value → ndarray (works correctly)

After this extraction, the isinstance(input_, np.ndarray) check correctly distinguishes handled from unhandled types.
