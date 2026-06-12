# Iteration Guidance for v2

## Critical Fixes

### 1. Fix Graph Shortcuts (Fixes 6 regressions)
Add `_add_merged_transform` calls in `itrs_observed_transforms.py` after registering the direct transforms. These force TETE/TEME <-> AltAz/HADec to go through the correct aberration-correcting paths:

```python
# Forward: TETE/TEME -> AltAz/HADec should NOT go through ITRS
frame_transform_graph._add_merged_transform(TETE, CIRS, AltAz)
frame_transform_graph._add_merged_transform(TETE, CIRS, HADec)
frame_transform_graph._add_merged_transform(TEME, ITRS, CIRS, AltAz)
frame_transform_graph._add_merged_transform(TEME, ITRS, CIRS, HADec)

# Reverse: AltAz/HADec -> TETE/TEME should NOT go through ITRS
frame_transform_graph._add_merged_transform(AltAz, CIRS, TETE)
frame_transform_graph._add_merged_transform(HADec, CIRS, TETE)
frame_transform_graph._add_merged_transform(AltAz, CIRS, ITRS, TEME)
frame_transform_graph._add_merged_transform(HADec, CIRS, ITRS, TEME)
```

NOTE: Check that each consecutive pair has a direct transform registered. TETE->CIRS might need to go TETE->GCRS->CIRS. Adjust paths accordingly.

### 2. Add location attribute to ITRS (Fixes FAIL_TO_PASS)
Modify `itrs.py` to add:
```python
from astropy.coordinates.attributes import TimeAttribute, EarthLocationAttribute
from .utils import DEFAULT_OBSTIME, EARTH_CENTER

class ITRS(BaseCoordinateFrame):
    obstime = TimeAttribute(default=DEFAULT_OBSTIME)
    location = EarthLocationAttribute(default=EARTH_CENTER)
```

This mirrors CIRS and TETE which also have location attributes.

### 3. Update ITRS<->observed transforms to use location
In `itrs_to_observed()`, the topocentric correction should account for the ITRS frame's location. If the ITRS has `location != EARTH_CENTER`, the coordinates are already topocentric relative to that location.

### 4. Fix ITRS loopback
The ITRS<->ITRS loopback currently goes ITRS->CIRS->ITRS, which doesn't handle different locations. Consider changing this to handle location differences directly.

## Verification Plan

After implementing v2:
1. Run smoke test: ITRS(straight overhead) -> AltAz should give alt=90
2. Check transform graph paths: TETE->AltAz, TEME->AltAz should NOT go through ITRS
3. Verify ITRS(location=loc) doesn't crash
4. Run the private evaluator

## Conservative Approach

- Only change ITRS frame definition (add location attribute)
- Only change itrs_observed_transforms.py (add merged transforms, update transform functions)
- Do NOT touch any other frame definitions
- Do NOT touch any other transform files
