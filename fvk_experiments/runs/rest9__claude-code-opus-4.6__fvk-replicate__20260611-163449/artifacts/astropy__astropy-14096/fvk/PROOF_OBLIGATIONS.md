# PROOF OBLIGATIONS — SkyCoord.__getattr__ Descriptor Error Propagation

## Bug-fix obligation (FAIL_TO_PASS)

**O1: Descriptor error propagation**
- When `attr` is a descriptor in `type(self).__mro__` whose `__get__` raises `AttributeError`
- AND all frame-based lookups have failed
- THEN `__getattr__` must propagate the original `AttributeError` from `__get__`, not a generic one
- Verified by: the issue's reproduction case

## Non-regression obligations (PASS_TO_PASS — 426 tests)

### Frame name resolution
**O2**: `sc.icrs` returns self (identity transform)
**O3**: `sc.galactic` returns galactic-frame transformed coordinates
**O4**: All named frame transformations continue to work

### Frame attribute access
**O5**: `sc.ra`, `sc.dec` return coordinate components
**O6**: `sc.equinox`, `sc.obstime` return frame attributes
**O7**: `sc.distance` returns distance through `_sky_coord_frame`

### Missing attribute error
**O8**: `sc.totally_nonexistent` raises `AttributeError` with the standard message format
**O9**: The error message uses `self.__class__.__name__` (correct for subclasses)

### Initialization safety
**O10**: During `SkyCoord.__init__`, attribute access before `_sky_coord_frame` is set must not crash in new ways
**O11**: `SkyCoord()` construction must succeed normally

### __setattr__ and __delattr__ unchanged
**O12**: `__setattr__` behavior is not affected (not modified)
**O13**: `__delattr__` behavior is not affected (not modified)

### Subclass compatibility
**O14**: `SkyCoord` subclasses can define custom properties that work correctly
**O15**: `SkyCoord` subclasses can access frame attributes normally
**O16**: `test_setitem_exceptions` and other subclass tests pass

### Edge cases
**O17**: Private attributes (`_foo`) are handled correctly (the `break` in the MRO scan handles this)
**O18**: Attributes that shadow frame attributes resolve to the frame attribute (frame lookup happens first)

## Forbidden changes

**F1**: Do not modify `__setattr__` or `__delattr__`
**F2**: Do not change the frame lookup order or logic
**F3**: Do not add new import dependencies
**F4**: Do not change the error message format for genuinely missing attributes
**F5**: Do not modify tests
