# v1 Notes

## Behavioral change

In `SlicedLowLevelWCS.world_to_pixel_values`, when constructing the full world coordinate array for the underlying WCS, dropped world dimensions were filled with a hardcoded value of `1.0`. This is incorrect when the WCS has coupled dimensions (non-diagonal PC matrix), because the incorrect fill value propagates through the inverse transform.

The fix computes the actual world coordinate values at the slice reference pixel position using `_pixel_to_world_values_all(*[0]*len(self._pixel_keep))`, then uses those values for the dropped dimensions. This is correct because dropped world dimensions are, by definition, not correlated with any kept pixel dimension (per the axis correlation matrix), so their reference values depend only on the fixed slice pixel positions.

## Files modified

- `astropy/wcs/wcsapi/wrappers/sliced_wcs.py`: Changed `world_to_pixel_values` method (line 254), replacing `1.` with `world_ref[iworld]`.

## Public tests run

- `repo/astropy/wcs/wcsapi/wrappers/tests/test_sliced_wcs.py`: 40/40 passed (before and after fix)
- Manual roundtrip tests with the issue's WCS at pixel positions (0,0), (10,5), (49.5,12), (99,24): all pass
- Manual test at slice index 1: passes

## Why v1 matches the issue

The issue describes `world_to_pixel` on a `SlicedLowLevelWCS` returning erroneous results when the underlying WCS has coupled spatial-spectral dimensions via a non-trivial PC matrix. The hint identifies line 254 (the `1.` literal) as the root cause. The fix replaces that value with the correct world coordinate computed from the slice position, restoring consistency between `pixel_to_world` and `world_to_pixel` on sliced WCS objects.
