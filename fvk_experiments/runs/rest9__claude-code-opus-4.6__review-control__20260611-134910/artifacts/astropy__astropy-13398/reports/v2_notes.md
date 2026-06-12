# v2 Notes

## Changes from v1 to v2

v2 adds two capabilities on top of v1:

### 1. ITRS `location` attribute (EarthLocationAttribute)

Added `location = EarthLocationAttribute(default=EARTH_CENTER)` to the ITRS frame class, modeled after the same attribute on CIRS and TETE. This enables "topocentric ITRS" — coordinates expressed relative to an Earth surface location rather than Earth's center. The transforms use this attribute to correctly handle the topocentric offset:

```python
topocentric_itrs_repr = (itrs_coo.cartesian
                         + itrs_coo.location.get_itrs().cartesian
                         - observed_frame.location.get_itrs().cartesian)
```

For geocentric ITRS (default), `location.get_itrs().cartesian` is (0,0,0), making the addition a no-op.

### 2. Merged transforms to prevent graph shortcuts

Adding direct ITRS<->AltAz/HADec edges creates 2-hop shortcuts (e.g., TETE->ITRS->AltAz) that bypass the aberration-correcting CIRS path. Eight `_add_merged_transform` calls create single-hop composite edges that force TETE and TEME to go through the correct CIRS path:
- TETE<->AltAz via GCRS+CIRS 
- TETE<->HADec via GCRS+CIRS
- TEME<->AltAz via ITRS+CIRS
- TEME<->HADec via ITRS+CIRS

## Files Modified (cumulative)

1. `astropy/coordinates/builtin_frames/itrs.py`: Added `location` attribute, `EarthLocationAttribute` import, `EARTH_CENTER` import, docstring update
2. `astropy/coordinates/builtin_frames/itrs_observed_transforms.py` (NEW): Direct transforms + merged transforms
3. `astropy/coordinates/builtin_frames/__init__.py`: Added import

## Review-Guided Changes

The review identified:
- **Missing location attribute**: v1 used geocentric-only ITRS. The issue discussion explicitly proposed a topocentric ITRS frame with an EarthLocationAttribute. Added in v2.
- **Graph shortcut problem**: v1 created 6 PASS_TO_PASS regressions from TETE/TEME taking 2-hop shortcuts through ITRS to AltAz/HADec, bypassing aberration correction. Merged transforms address forward shortcuts but introduce 1 cascading regression.

## Diagnostic Variants Tested

| Variant | Location | Merged | F2P | P2P |
|---------|----------|--------|-----|-----|
| v1 | No | No | 0/4 | 62/68 |
| + merged only | No | Yes | 0/4 | 61/68 |
| + location only | Yes | No | 1/4 | 62/68 |
| v2 (location+merged) | Yes | Yes | 2/4 | 61/68 |

Also tested: custom ITRS self-transform with location handling, forward-only merged, location propagation in CIRS/TETE transforms — none improved beyond 2/4, 61/68.

## Remaining Gaps

- 2 FAIL_TO_PASS tests remain unsolved. They likely require additional changes I could not identify within benchmark discipline (possibly modifications to intermediate rotation transforms, or a different approach to the ITRS self-transform).
- 7 PASS_TO_PASS regressions persist: 6 from the direct ITRS<->AltAz/HADec edges creating Dijkstra shortcuts, +1 cascading from merged transforms.
