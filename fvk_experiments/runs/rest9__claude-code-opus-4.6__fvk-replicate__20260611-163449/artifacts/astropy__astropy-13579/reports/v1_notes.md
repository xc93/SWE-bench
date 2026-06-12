# v1 Notes

## Behavioral Change

In `SlicedLowLevelWCS.world_to_pixel_values`, dropped world dimensions were filled with a hardcoded `1.` when reconstructing the full world coordinate array for the underlying WCS. This caused incorrect inverse transforms when the WCS has coupled dimensions (non-trivial PCij matrix).

The fix computes the actual world coordinate at the sliced pixel position using `_pixel_to_world_values_all` and uses those values for dropped world dimensions instead of `1.`.

## Files Modified

- `astropy/wcs/wcsapi/wrappers/sliced_wcs.py`: Changed `world_to_pixel_values` method (line ~254).

## Public Tests Run

- `astropy/wcs/wcsapi/wrappers/tests/test_sliced_wcs.py`: 40/40 passed before and after the fix.
- Manual reproduction of the issue from the bug report: confirmed bug exists before fix, confirmed fix resolves it.

## Why This Matches the Public Issue

The issue reports that `world_to_pixel` on a sliced 2D WCS (sliced from a 3D WCS with coupled spectral-spatial dimensions) returns an erroneous result (1.8e11) for one dimension. The hint in the issue points to line 254 where `1.` is used as a placeholder. The fix replaces this with the correct world coordinate derived from the pixel value in the slice.
