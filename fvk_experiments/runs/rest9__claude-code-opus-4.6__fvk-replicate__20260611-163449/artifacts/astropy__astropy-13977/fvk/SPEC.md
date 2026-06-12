# SPEC: Quantity.__array_ufunc__() NotImplemented for incompatible inputs

## Intended Behavior Change

When `Quantity.__array_ufunc__()` is called with inputs it cannot handle (duck types that are not ndarray subclasses, Quantity subclasses, or recognized scalar types), it should return `NotImplemented` instead of raising `ValueError` or `TypeError`. This allows Python's operator dispatch to fall back to the other operand's reflected method (e.g., `__radd__`).

## Current Behavior (base code)

`__array_ufunc__` processes ALL inputs through converters without type checking. When an input cannot be converted (e.g., a duck type without numeric `.value`), `_condition_arg()` in `core.py` raises `ValueError`. This prevents Python from trying the other operand's reflected operator.

## Error Paths That Must Return NotImplemented

1. **Converter application (line 670)**: `converter(input_)` calls `_condition_arg(val)` which raises `ValueError` for non-numeric types
2. **converters_and_unit (line 643)**: `can_have_arbitrary_unit(duck_type)` raises `TypeError` when the duck type doesn't support comparison/isfinite

## Behavior That Must Remain Unchanged

1. `UnitConversionError` between two Quantities with incompatible units must still be raised
2. `TypeError` for unsupported ufuncs (np.logical_or on Quantities) must still be raised  
3. `UnitConversionError` for non-Quantity inputs (e.g., lists) to non-dimensionless Quantities must still be raised
4. Quantity + ndarray, Quantity + scalar, Quantity + Column operations must continue to work
5. All converter behavior for recognized types (ndarray, np.generic, int, float, complex) must be preserved

## Key Constraint: UnitConversionError inherits from ValueError

`UnitConversionError(UnitsError(ValueError))` — catching `ValueError` also catches `UnitConversionError`. The catch must be conditional to avoid masking real unit errors.
