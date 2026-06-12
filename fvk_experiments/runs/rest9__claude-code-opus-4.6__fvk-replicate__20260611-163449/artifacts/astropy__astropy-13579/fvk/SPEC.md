# SPEC — SlicedLowLevelWCS.world_to_pixel_values

## Intended Public Behavior

`SlicedLowLevelWCS.world_to_pixel_values(*world_arrays)` must satisfy the round-trip property with `pixel_to_world_values`: for any valid pixel position `P` in the sliced WCS domain, `world_to_pixel_values(pixel_to_world_values(P))` must return a value close to `P` (within floating-point tolerance).

This must hold for ALL WCS configurations, including those with non-trivial PC matrices that couple spectral and spatial dimensions.

## Current Buggy Behavior (Base Commit)

In `world_to_pixel_values`, when reconstructing the full world coordinate array for the underlying WCS, dropped world dimensions are filled with a hardcoded `1.` (line 254):

```python
else:
    world_arrays_new.append(1.)
```

This breaks the round-trip property when:
1. The WCS has dropped world dimensions (integer slices that remove pixel dimensions)
2. The dropped world dimensions are coupled with kept pixel dimensions through the PC matrix
3. The world coordinate `1.` does not correspond to the actual slice pixel position

## Correct Behavior

Dropped world dimensions must be filled with the world coordinate values at the sliced pixel position. This is computed by calling `_pixel_to_world_values_all(*[0]*len(self._pixel_keep))`, which:
- Uses the integer slice values for dropped pixel dimensions
- Uses 0 for kept pixel dimensions (which don't affect dropped world dimensions per the axis correlation matrix)

## Behavioral Domains

### Domain 1: Uncoupled WCS (diagonal PC matrix)
The fill value for dropped world dimensions does not affect kept pixel outputs. The fix is equivalent to the old behavior. All existing tests use this domain.

### Domain 2: Coupled WCS (non-trivial PC matrix)
The fill value matters. The hardcoded `1.` produces incorrect results; the computed world reference produces correct results. The public issue demonstrates this domain.

## Non-Regression Obligations

The following must remain unchanged:
1. All Ellipsis/identity slicing behavior
2. Range slicing (slice objects) — no dropped world dimensions
3. Spectral integer slicing with uncoupled WCS
4. Celestial integer slicing with uncoupled WCS
5. Rotated WCS slicing (90-degree rotation)
6. Nested slicing behavior
7. Broadcasting behavior for pixel_to_world and world_to_pixel
8. dropped_world_dimensions property
9. Array/pixel shape computation
10. Pixel bounds computation
11. combine_slices utility
12. sanitize_slices utility
13. WCS with None physical types
14. WCS without array shape
15. 1D sliced WCS
16. 4D WCS slicing
17. Different integer types (np.int64 vs int)
