# PROOF OBLIGATIONS — astropy__astropy-13236

## Bug-Fix Obligations (FAIL_TO_PASS)

### O1: Structured ndarray added to Table should become Column
- **Input**: `np.array([(1, 'a'), (2, 'b')], dtype='<i4,U1')` added to `Table`
- **Expected**: `isinstance(t['col'], Column)` is True
- **Expected**: `isinstance(t['col'], NdarrayMixin)` is False
- **Status**: Satisfied by v1

### O2: Structured ndarray data values preserved
- **Input**: Structured array with named/unnamed fields
- **Expected**: All field values accessible and unchanged after adding to Table
- **Status**: Satisfied by v1

## Non-Regression Obligations (PASS_TO_PASS)

### R1: Explicit NdarrayMixin columns still work
- **Input**: `data.view(NdarrayMixin)` or `NdarrayMixin(data)` added to Table
- **Expected**: Stored as mixin, not downgraded to Column
- **Verified**: Yes — `_is_mixin_for_table` returns True before the removed block

### R2: Regular (non-structured) ndarrays unchanged
- **Input**: `np.array([1, 2, 3])` added to Table
- **Expected**: Stored as Column (was already Column before)
- **Verified**: Yes — the removed block only triggered for `len(data.dtype) > 1`

### R3: Column inputs unchanged
- **Input**: `Column(data)` added to Table
- **Expected**: Handled by the `isinstance(data, Column)` branch
- **Verified**: Yes — the removed block checked `not isinstance(data, Column)`

### R4: MaskedColumn/MaskedArray inputs unchanged
- **Input**: `MaskedColumn` or `np.ma.MaskedArray` added to Table
- **Expected**: Handled by existing masked column logic
- **Verified**: Yes — MaskedArray has its own branch; MaskedColumn is a Column subclass

### R5: Other mixin columns unchanged
- **Input**: SkyCoord, Time, Quantity, EarthLocation, etc.
- **Expected**: Handled by mixin handler registry or `_is_mixin_for_table`
- **Verified**: Yes — these are caught earlier in the method

### R6: Table construction from structured ndarray unchanged
- **Input**: `Table(structured_array)` (whole array as data)
- **Expected**: Decomposes into individual columns via `_init_from_ndarray`
- **Verified**: Yes — `_init_from_ndarray` is a separate code path

### R7: Table operations (join, hstack, vstack, groups) unchanged
- **Input**: Tables with various column types
- **Expected**: All table operations work identically
- **Verified**: The test suite covers these (644 PASS_TO_PASS tests)

### R8: Table serialization/I/O unchanged
- **Input**: Tables with NdarrayMixin columns loaded from files
- **Expected**: Existing serialized data can still be loaded
- **Verified**: serialize.py NdarrayMixin handler is untouched

### R9: Table repr/pformat unchanged for structured columns
- **Input**: Table with structured Column
- **Expected**: Formatted correctly (field names, values)
- **Verified**: Column already supports structured dtype repr

## Forbidden Changes

- Do NOT remove the `NdarrayMixin` class or its imports
- Do NOT modify `serialize.py`
- Do NOT modify test fixtures in `conftest.py`
- Do NOT modify any other method in `Table`
- Do NOT add FutureWarning (consensus in issue discussion was to change directly)
- Do NOT modify `_init_from_ndarray`
