# SPEC — astropy__astropy-13236

## Intended Behavior Change

When a structured `np.ndarray` (i.e., `len(data.dtype) > 1`) is added to an `astropy.table.Table`, it should be stored as a `Column` object, NOT auto-transformed into an `NdarrayMixin`.

### Precondition
- `data` is a numpy ndarray with structured dtype (`len(data.dtype) > 1`)
- `data` is not already a `Column` instance
- `data` is not already a valid mixin column

### Postcondition (new behavior)
- `data` is stored as `Column` (or `MaskedColumn` for masked tables)
- `isinstance(t[colname], Column)` is True
- `isinstance(t[colname], NdarrayMixin)` is False
- Data values are preserved exactly

### Postcondition (old behavior, to be removed)
- `data` was auto-converted via `data.view(NdarrayMixin)`
- `isinstance(t[colname], NdarrayMixin)` was True

## What Must NOT Change

1. **Explicit NdarrayMixin inputs**: If the user explicitly passes `data.view(NdarrayMixin)` or constructs an `NdarrayMixin` directly, it should continue to be stored as a mixin column.
2. **Regular (non-structured) ndarrays**: Non-structured arrays should continue to be added as `Column` objects (no change needed here — they already are).
3. **Column inputs**: `Column` instances should be handled identically.
4. **MaskedColumn/MaskedArray inputs**: Masked data handling should be unchanged.
5. **Other mixin columns**: SkyCoord, Time, Quantity, EarthLocation, etc. should be handled identically.
6. **Record arrays (np.recarray)**: These are ndarray subclasses with structured dtype. They should now be added as `Column` rather than `NdarrayMixin`, same as plain structured ndarrays.
7. **Table construction from structured ndarray (`_init_from_ndarray`)**: When a whole structured array is passed to `Table()` as the data argument, it decomposes into individual columns — this path is separate and unaffected.
8. **Serialization paths**: The `serialize.py` reference to `NdarrayMixin` is for I/O handling and remains valid for any existing NdarrayMixin columns.

## Scope of Change

Exactly one code path: the `_convert_data_to_col` method in `Table`, specifically the block:

```python
# Structured ndarray gets viewed as a mixin unless already a valid
# mixin class
if (not isinstance(data, Column) and not data_is_mixin
        and isinstance(data, np.ndarray) and len(data.dtype) > 1):
    data = data.view(NdarrayMixin)
    data_is_mixin = True
```

This block should be deleted entirely.
