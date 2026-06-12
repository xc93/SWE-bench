# Review Findings: v1 Patch for astropy__astropy-13579

## 1. Intended public behavior change

`SlicedLowLevelWCS.world_to_pixel_values` should be the correct inverse of `pixel_to_world_values` when the underlying WCS has coupled dimensions (non-diagonal PC matrix). Previously, dropped world dimensions were filled with a hardcoded `1.0`, which corrupted the inverse transform when those dimensions were coupled to kept pixel dimensions through the PC matrix.

## 2. Current behavior in implicated code paths

`world_to_pixel_values` (line 245-272): Constructs a full world coordinate array for the underlying WCS by filling in values for dropped world dimensions. The old code used `1.0` for all dropped dims. The fix uses `_pixel_to_world_values_all(*[0]*N)` to compute the actual world coordinates at the slice reference pixel position.

`_pixel_to_world_values_all` (line 212-227): Takes pixel coordinates for kept dims, fills in slice values for dropped pixel dims, and calls the underlying WCS's `pixel_to_world_values`. This already existed and is reused by the fix.

`dropped_world_dimensions` (line 156-186): Uses the exact same pattern (`_pixel_to_world_values_all(*[0]*len(self._pixel_keep))`) at line 161. Validates that the fix's approach is consistent with existing code.

## 3. What the issue implies for astropy behavior

The issue is a correctness bug in the sliced WCS wrapper. It affects any WCS with:
- A non-diagonal PC/CD matrix (coupled dimensions)
- An integer slice that drops a pixel dimension
- The dropped world dimension having a different value than `1.0` in the underlying WCS units

## 4-7. What must remain unchanged

**Public APIs (4):** All other methods of `SlicedLowLevelWCS` are unchanged: `pixel_to_world_values`, `_pixel_to_world_values_all`, `dropped_world_dimensions`, properties, `array_shape`, `pixel_bounds`, `axis_correlation_matrix`.

**Related code paths (5):** The `HighLevelWCSWrapper` that wraps `SlicedLowLevelWCS` calls `world_to_pixel_values` internally. Its behavior improves (correct results instead of incorrect ones).

**Inputs outside scope (6):** When there are NO dropped world dimensions (e.g., slicing by range or keeping all dims), the `else` branch in the loop is never entered. The `world_ref` is computed but unused. This is correct but mildly wasteful.

**Edge cases (7):**
- Decoupled axes (diagonal PC matrix): The dropped world value doesn't affect kept pixel results regardless (old `1.0` and new reference value both give the same pixel results for kept dims). Verified with `test_spectral_slice` scenario.
- Nested slicing: The `__init__` combines slices and stores the original WCS. The fix operates on the combined state. Safe.
- 1D WCS with slice: No dropped world dims possible (would raise ValueError). Safe.
- Broadcasting: The fix returns a scalar for each dropped world dim (from `_pixel_to_world_values_all` with scalar inputs). `np.broadcast_arrays` handles this correctly.

## 8. What v1 got right

- Correct root cause identification: the `1.0` literal at line 254.
- Correct replacement: world coordinates at the slice reference pixel position.
- Consistent approach: reuses the same pattern as `dropped_world_dimensions` (line 161).
- Minimal change: only the `world_to_pixel_values` method is modified.
- All 40 existing public tests pass.

## 9. What v1 is potentially missing or overgeneralizing

**Minor inefficiency (not a bug):** `world_ref` is computed on every call to `world_to_pixel_values`, even when there are no dropped world dimensions. This costs one extra `pixel_to_world_values` computation per call. Could be guarded with `if len(self._world_keep) < self._wcs.world_n_dim:` but this is an optimization, not a correctness issue.

**No correctness concerns found.** The fix is minimal and correct. The dropped world dimensions are guaranteed (by the axis_correlation_matrix) to be independent of kept pixel dimensions, so using `0` for kept pixel dims in the reference computation is correct.

## 10. Exact minimal changes justified for v2

The v1 patch is already minimal and correct. The only defensible change for v2 is:
- Guard the `world_ref` computation with a condition check so it's only computed when there are actually dropped world dimensions.

This is a minor performance optimization, NOT a correctness fix. The risk of introducing a regression is essentially zero, since it only adds a skip condition for a code path that was already correct.

## 11. Changes forbidden (regression risks)

- Do NOT change `_pixel_to_world_values_all` — it's used by `pixel_to_world_values` and `dropped_world_dimensions`.
- Do NOT change how `_world_keep` or `_pixel_keep` are computed.
- Do NOT change the loop structure or the kept-world-dimension indexing.
- Do NOT add caching via `lazyproperty` for `world_ref` — the slice state is immutable but caching adds complexity for minimal gain.
- Do NOT refactor the method signature or return type.
