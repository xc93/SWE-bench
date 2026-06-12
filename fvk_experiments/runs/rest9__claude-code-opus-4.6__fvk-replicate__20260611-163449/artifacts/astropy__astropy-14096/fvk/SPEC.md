# SPEC — SkyCoord.__getattr__ Descriptor Error Propagation

## Intended Behavior Change

When `SkyCoord.__getattr__(self, attr)` is invoked for an `attr` that exists as a descriptor (e.g., a `property`) in `type(self).__mro__`, the method must re-invoke the descriptor's `__get__` so the **original** `AttributeError` propagates, rather than being masked by the generic `"'<ClassName>' object has no attribute '<attr>'"` message.

### Why __getattr__ is called for descriptors

Python's attribute lookup protocol:
1. Data descriptors (e.g. `property`) in `type.__mro__` are tried via `__get__`
2. If `__get__` raises `AttributeError`, `object.__getattribute__` raises `AttributeError`
3. Python then invokes `__getattr__` with the descriptor's name

At this point, the descriptor exists but its `__get__` failed internally. The correct behavior is to surface the original error.

## Precondition

`__getattr__` is called with `attr` that is a descriptor in `type(self).__mro__`, AND all prior SkyCoord frame-based lookups (frame name, frame attributes, frame delegation, frame transformation) have already been tried and failed.

## Postcondition

The original `AttributeError` from the descriptor's `__get__` propagates to the caller, with its original message and traceback.

## Non-regression Obligations

The following behaviors MUST remain unchanged:

1. **Frame name resolution**: `sc.icrs`, `sc.galactic`, etc. must return transformed coordinates
2. **Frame attribute delegation**: `sc.ra`, `sc.dec`, `sc.equinox`, etc. must return frame attributes
3. **Frame attribute via _sky_coord_frame**: `sc.distance`, etc. from the underlying frame
4. **Missing attribute error for non-descriptors**: `sc.nonexistent` must raise `AttributeError` with the standard message
5. **Initialization safety**: During `__init__`, before `_sky_coord_frame` is set, `__getattr__` must not fail in new ways
6. **`__setattr__` and `__delattr__`**: These sibling methods must not be modified
7. **Public API of SkyCoord**: All 426+ existing tests in test_sky_coord.py must continue to pass
