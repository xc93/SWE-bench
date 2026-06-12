# v1 Notes

## Behavioral Change

When a subclassed `SkyCoord` has a property that internally raises `AttributeError`, the error message now correctly identifies the missing attribute instead of misleadingly claiming the property itself doesn't exist.

Before: `AttributeError: 'custom_coord' object has no attribute 'prop'`
After: `AttributeError: 'custom_coord' object has no attribute 'random_attr'`

## Files Modified

- `astropy/coordinates/sky_coordinate.py`: Added descriptor check before the final `AttributeError` raise in `__getattr__`.

## Approach

In `SkyCoord.__getattr__`, before raising the final "object has no attribute" error, we check if the attribute exists as a descriptor (e.g., a `property`) on the class hierarchy (via MRO). If so, `__getattr__` was only called because the descriptor's `__get__` raised `AttributeError` internally. We re-invoke the descriptor directly so the real error propagates with the correct message.

## Public Tests Run

- `test_sky_coord.py`: 426 passed (excluding 1 pre-existing infrastructure failure unrelated to this change)
- Manual test reproducing the issue: confirmed fix works correctly

## Why This Matches the Issue

The issue reports that `c.prop` gives `'custom_coord' object has no attribute 'prop'` when really `random_attr` is the missing attribute. The fix ensures the real `AttributeError` from inside the property propagates to the user.
