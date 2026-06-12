# Final Report — astropy__astropy-13398

## Instance Summary

**Issue**: Add direct ITRS to Observed (AltAz, HADec) coordinate transformations that stay within the ITRS framework, avoiding the aberration-correcting CIRS/ICRS path.

**Difficulty**: 1-4 hours | **Evaluator shape**: 4 FAIL_TO_PASS, 68 PASS_TO_PASS

## Scores

| Phase | FAIL_TO_PASS | PASS_TO_PASS | Resolved |
|-------|-------------|-------------|----------|
| v1 (before review) | 0 / 4 | 62 / 68 | No |
| v2 (after review) | 2 / 4 | 61 / 68 | No |

**Delta**: +2 FAIL_TO_PASS, -1 PASS_TO_PASS

## v1 Approach

Created `itrs_observed_transforms.py` with:
- `itrs_to_observed_mat()`: Rotation matrix from ITRS to local horizon (AltAz or HADec) based on geodetic coordinates
- `itrs_to_observed()`: ITRS→AltAz/HADec via topocentric subtraction + rotation
- `observed_to_itrs()`: Reverse via inverse rotation + geocentric addition
- Registered as `FunctionTransformWithFiniteDifference` transforms

The direct transforms worked correctly for ITRS→AltAz/HADec, but 0/4 FAIL_TO_PASS passed (all tests required the ITRS `location` attribute). The 6 PASS_TO_PASS regressions were from Dijkstra shortest-path shortcuts: TETE/TEME now took 2-hop paths through ITRS to AltAz/HADec, bypassing aberration correction.

## Review Findings

The review identified three issues:

1. **Missing ITRS `location` attribute**: The issue discussion explicitly described adding `EarthLocationAttribute` to ITRS for topocentric coordinates. All 4 FAIL_TO_PASS tests required this.

2. **Graph shortcut problem**: Direct ITRS↔AltAz/HADec edges created shorter paths that bypass aberration. Merged transforms were needed to force TETE/TEME through the correct CIRS path.

3. **ITRS loopback**: The existing ITRS→CIRS→ITRS loopback doesn't handle location differences. Could need a custom function.

## v2 Changes (Review-Guided)

1. **Added `location = EarthLocationAttribute(default=EARTH_CENTER)` to ITRS frame** in `itrs.py`, with imports and docstring updates.

2. **Updated ITRS↔observed transforms** to handle topocentric ITRS:
   ```python
   topocentric_itrs_repr = (itrs_coo.cartesian
                            + itrs_coo.location.get_itrs().cartesian
                            - observed_frame.location.get_itrs().cartesian)
   ```

3. **Added 8 merged transforms** for TETE/TEME↔AltAz/HADec to prevent shortcuts.

## Diagnostic Variants Explored

| Variant | F2P | P2P | Notes |
|---------|-----|-----|-------|
| v1 (base) | 0/4 | 62/68 | Direct transforms only |
| + merged only | 0/4 | 61/68 | All F2P need location |
| + location only | 1/4 | 62/68 | Location gets 1 F2P |
| v2 (location+merged) | 2/4 | 61/68 | Best combination |
| + custom ITRS loopback | 2/4 | 61/68 | No change |
| + forward-only merged | 2/4 | 61/68 | No change |
| + CIRS/TETE loc propagation | 1/4 | 56/68 | Made things worse |

## Analysis of Remaining Gaps

### 2 unsolved FAIL_TO_PASS
The remaining tests likely need changes I could not determine within benchmark discipline constraints. Possibilities:
- The ITRS↔CIRS/TETE transforms may need location-aware handling in `intermediate_rotation_transforms.py` (my attempt to add this caused 12 P2P regressions, suggesting the approach was wrong)
- There may be a different ITRS self-transform approach needed
- The tests may check graph properties or transform path characteristics

### 7 PASS_TO_PASS regressions
- 6 from TETE/TEME↔AltAz/HADec shortcuts: the merged transforms create 1-hop edges that should fix these, but empirically they don't (P2P stays at 62 with or without merged for the location-only variant)
- 1 additional from merged transforms: cascading graph effects where new 1-hop edges create shorter paths for unrelated frame pairs

## Key Technical Insight

The transform graph is a Dijkstra shortest-path system. Adding new edges (direct transforms or merged composites) changes shortest paths for ALL frame pairs, not just the intended ones. This creates a fundamental tension: the ITRS→AltAz edge must exist for direct use, but its existence creates shortcuts that other frames exploit. Merged transforms partially address this but introduce their own cascading effects. A priority-based approach cannot resolve this because the priority that prevents shortcuts also prevents the intended direct path.

## Review Effectiveness

The review correctly identified the two most impactful missing pieces (location attribute and merged transforms), producing the +2 F2P improvement. However, it overestimated the fix potential of merged transforms for P2P regressions — the 6 shortcut regressions persist despite merged transforms, suggesting a deeper graph topology issue or that the regressions have a different root cause than assumed.
