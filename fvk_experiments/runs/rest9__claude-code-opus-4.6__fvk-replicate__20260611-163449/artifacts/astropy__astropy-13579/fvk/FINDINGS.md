# FINDINGS — SlicedLowLevelWCS world_to_pixel_values

## Finding 1: Hardcoded fill value for dropped world dimensions (BUG — the reported issue)

**Evidence:** `sliced_wcs.py` line 254, `world_arrays_new.append(1.)`

**Input → observed vs expected:**
- Input: 3D WCS with PC2_3=-1.0 (coupling HPLT with WAVE pixel), sliced at wavelength pixel 0
- `world_to_pixel_values(world_hpln, world_hplt)` where world values correspond to pixel (0,0,0)
- Observed: `(1.8e11, ~0)` — first pixel is essentially infinite
- Expected: `(~0, ~0)` — round-trip should recover original pixel position

**Root cause:** The dropped WAVE world dimension is filled with `1.` (in internal units, meters). The actual wavelength at pixel 0 is 1.05e-10 m. Due to the coupling via PC2_3, this enormous discrepancy in the spectral world coordinate propagates through the inverse transform into the spatial pixel output.

**v1 status:** FIXED. v1 computes the correct world reference via `_pixel_to_world_values_all`.

## Finding 2: v1 uses same pattern as `dropped_world_dimensions` (POSITIVE)

**Evidence:** `dropped_world_dimensions` (line 161) already uses:
```python
world_coords = self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))
```

v1's fix reuses this same pattern for consistency. The dropped_world_dimensions property uses these values to report the world coordinates of dropped dimensions, confirming this is the correct reference.

## Finding 3: Potentially undefined variable `world_ref` (MINOR STYLE)

**Evidence:** v1 defines `world_ref` inside an `if any(...)` guard. If no world dimensions are dropped, `world_ref` is never defined. It's never accessed either (the `else` branch is never reached), so this is functionally correct. However, a static analysis tool or linter might flag it.

**Recommendation:** Not worth fixing — changing this adds risk for no functional benefit. The guard is correct.

## Finding 4: Performance — extra pixel_to_world call per world_to_pixel (MINOR)

**Evidence:** v1 calls `_pixel_to_world_values_all` on every `world_to_pixel_values` invocation when there are dropped world dimensions. This could be cached since the slice positions are fixed.

**Recommendation:** Not worth changing for v2. The cost is negligible for typical WCS usage, and caching adds complexity. The `any(...)` guard already skips the computation when there are no dropped world dimensions.

## Finding 5: No existing test covers coupled WCS with integer slicing (COVERAGE GAP)

**Evidence:** All existing tests use `WCS_SPECTRAL_CUBE` which has a diagonal PC matrix (no coupling). The test `test_spectral_slice` slices at integer 10 on the spectral axis, but the spectral axis is uncoupled from the celestial axes, so the fill value doesn't affect the output.

**Recommendation:** The hidden test likely covers this. No action needed for v2 (we cannot add tests to match hidden expectations).
