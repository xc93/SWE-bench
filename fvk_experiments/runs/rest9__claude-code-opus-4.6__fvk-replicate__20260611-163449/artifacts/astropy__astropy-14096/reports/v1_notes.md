# v1 Notes

## Behavior Change

When a subclass of `SkyCoord` defines a property whose getter raises `AttributeError` internally (e.g., by accessing a non-existent attribute), the error message now correctly reports which attribute is actually missing, instead of misleadingly claiming the property itself doesn't exist.

Before: `'custom_coord' object has no attribute 'prop'`
After: `'custom_coord' object has no attribute 'random_attr'`

## Files Modified

- `astropy/coordinates/sky_coordinate.py`: Added descriptor re-invocation logic before the final `AttributeError` raise in `__getattr__`.

## Approach

In `__getattr__`, before raising the generic "no attribute" error, we scan the class MRO for the requested attribute. If it exists as a descriptor (has `__get__`), we know `__getattr__` was called because the descriptor's `__get__` raised `AttributeError`. We re-invoke the descriptor to let the original error propagate.

## Public Tests Run

- `astropy/coordinates/tests/test_sky_coord.py`: 426 passed, 1 failed (unrelated leap-second issue), 3 skipped, 1 xfailed.

## Why v1 Matches the Issue

The issue requests that the *original* `AttributeError` propagate when a subclassed `SkyCoord` property fails internally. v1 achieves this by detecting descriptors in the class hierarchy and re-invoking them.
