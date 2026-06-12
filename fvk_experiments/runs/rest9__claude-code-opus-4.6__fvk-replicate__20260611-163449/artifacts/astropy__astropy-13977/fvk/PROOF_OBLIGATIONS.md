# PROOF OBLIGATIONS

## Bug-fix obligations (what must change)

### O1: Converter application must return NotImplemented for unrecognized inputs
- **Location**: `quantity.py` line 670, inside the converter loop
- **Current**: raises ValueError/TypeError unconditionally
- **Required**: return NotImplemented when the failing input is not an ndarray
- **Guard**: `not isinstance(input_, np.ndarray)` after `getattr(input_, "value", input_)`

### O2: converters_and_unit errors must return NotImplemented for duck types
- **Location**: `quantity.py` line 643, call to `converters_and_unit`
- **Current**: TypeError/ValueError propagates unconditionally
- **Required**: return NotImplemented when the error is caused by a duck type input
- **Guard**: check if any input has `__array_ufunc__` but is not an ndarray subclass

## Non-regression obligations (what must NOT change)

### R1: UnitConversionError between Quantities must still raise
- **Example**: `Quantity(1, u.m) + Quantity(1, u.s)` → UnitConversionError
- **Guard**: all inputs are ndarray → re-raise

### R2: TypeError for unsupported ufuncs with Quantities must still raise
- **Example**: `np.logical_or(Quantity(1), Quantity(2))` → TypeError
- **Guard**: all inputs are ndarray → re-raise

### R3: UnitConversionError for non-Quantity non-duck-type inputs must still raise
- **Example**: `Quantity(1, u.m) + [1, 2, 3]` → UnitConversionError
- **Guard**: list has no `__array_ufunc__` → re-raise

### R4: Quantity + Column operations must continue to work
- **Evidence**: Column is an ndarray subclass; Column.value returns ndarray
- **Guard**: isinstance(Column, np.ndarray) is True → normal path

### R5: Quantity + ndarray operations must continue to work
- **Evidence**: ndarray passes _condition_arg; isinstance check → normal path

### R6: Quantity + scalar operations must continue to work
- **Evidence**: int/float/complex pass _condition_arg; isinstance check → normal path

### R7: converter errors for ndarray inputs must still raise
- **Example**: converter fails on structured/object dtype arrays
- **Guard**: isinstance(input_, np.ndarray) → re-raise
