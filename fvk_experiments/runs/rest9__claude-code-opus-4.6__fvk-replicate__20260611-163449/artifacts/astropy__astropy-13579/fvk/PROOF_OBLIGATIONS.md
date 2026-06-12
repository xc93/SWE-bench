# PROOF OBLIGATIONS — SlicedLowLevelWCS patch

## Bug-Fix Obligation (FAIL_TO_PASS)

**O1: Round-trip correctness for coupled WCS with integer slice**

For any N-dimensional WCS `W` with non-trivial PC matrix coupling, and any integer slice `s` on one or more pixel dimensions:
- Let `S = SlicedLowLevelWCS(W, s)`
- Let `P` be a valid pixel position for `S`
- Let `world = S.pixel_to_world_values(P)`
- Then `S.world_to_pixel_values(*world) ≈ P` (within floating-point tolerance)

This must hold specifically for the issue's example: 3D WCS with PC2_3=-1.0, sliced at wavelength pixel 0.

## Non-Regression Obligations (PASS_TO_PASS)

**O2: Ellipsis/identity slicing unchanged**
- `SlicedLowLevelWCS(wcs, Ellipsis)` must behave identically to the base commit for all methods.
- No dropped world dimensions → the `any(...)` guard is False → no `_pixel_to_world_values_all` call → code path unchanged.

**O3: Range slicing unchanged**
- `SlicedLowLevelWCS(wcs, [slice(a,b), ...])` with only range slices keeps all pixel/world dimensions.
- No dropped world dimensions → same as O2.

**O4: Integer slice on uncoupled WCS unchanged**
- `test_spectral_slice` slices spectral axis (uncoupled from celestial) at integer 10.
- `world_to_pixel_values(10, 25)` fills dropped FREQ with `world_ref[1]` instead of `1.`.
- Because FREQ is uncoupled from GLAT/GLON, the fill value does NOT affect the GLAT/GLON pixel outputs.
- The returned pixel values are identical.

**O5: Celestial integer slice with full world dims unchanged**
- `test_celestial_slice` slices pixel dim 0 but keeps all 3 world dims.
- No dropped world dimensions → `any(...)` guard is False → unchanged.

**O6: Rotated WCS range slice unchanged**
- `test_celestial_range_rot` uses a 90-degree rotated PC matrix with range slicing only.
- No dropped dimensions → unchanged.

**O7: combine_slices unchanged**
- Pure utility function, not touched by the patch.

**O8: sanitize_slices unchanged**
- Pure utility function, not touched by the patch.

**O9: Nested slicing unchanged**
- `test_nested_slicing` uses nested `SlicedLowLevelWCS`. The inner WCS is combined into a single `_slices_array`.
- The final `world_to_pixel_values` call may invoke the fix, but the combined slicing still produces correct results because `_pixel_to_world_values_all` correctly handles the combined slice values.

**O10: dropped_world_dimensions unchanged**
- Property not modified. Uses same `_pixel_to_world_values_all(*[0]*len(self._pixel_keep))` pattern.

**O11: pixel_to_world_values unchanged**
- Not modified by the patch.

**O12: 1D, 4D, None-type, no-shape WCS unchanged**
- Tests do not exercise dropped world dimensions in `world_to_pixel_values`, OR the uncoupled nature means fill value is irrelevant.

**O13: Broadcasting unchanged**
- `_pixel_to_world_values_all(*[0]*len(...))` returns scalars for scalar pixel inputs, which broadcast correctly with any array-shaped `world_arrays`.

**O14: Different integer types unchanged**
- `test_pixel_to_world_values_different_int_types` tests `pixel_to_world_values`, not `world_to_pixel_values`. Not affected.

## Summary

- The patch modifies exactly one code path: the `else` branch of the world dimension loop in `world_to_pixel_values`.
- This branch is only entered when there are dropped world dimensions (integer slices that remove pixel dimensions, causing some world dimensions to become uncorrelated with any kept pixel dimension).
- For uncoupled WCS (all existing tests), the new fill value produces identical results to the old `1.`.
- For coupled WCS (the bug), the new fill value produces correct results.
- No other methods or properties are modified.
