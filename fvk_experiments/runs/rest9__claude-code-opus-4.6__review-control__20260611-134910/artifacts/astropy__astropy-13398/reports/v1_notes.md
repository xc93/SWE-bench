# v1 Notes

## Behavioral Change

v1 adds direct ITRS <-> AltAz and ITRS <-> HADec transformations that stay entirely within the ITRS framework. Instead of going through the full ICRS/CIRS pipeline (which involves aberration, precession, nutation), these transforms use a simple geometric rotation from Earth-fixed ITRS coordinates to local horizon coordinates.

The approach:
1. Compute topocentric ITRS position by subtracting observer's ITRS position from target's ITRS position
2. Apply a rotation matrix to convert from ITRS to local horizon (AltAz or HADec)
3. The reverse transform applies the inverse rotation and adds back the observer position

The ITRS position is treated as time-invariant (obstime differences between frames are ignored), since ITRS coordinates are Earth-fixed.

## Files Modified

1. `astropy/coordinates/builtin_frames/itrs_observed_transforms.py` (NEW): Contains `itrs_to_observed_mat()`, `itrs_to_observed()`, and `observed_to_itrs()` functions
2. `astropy/coordinates/builtin_frames/__init__.py`: Added import of the new module

## Public Tests Run

- Verified ITRS -> AltAz gives alt=90 for straight-overhead object
- Verified ITRS -> HADec gives ha=0, dec=lat for straight-overhead object
- Verified round-trip ITRS -> AltAz -> ITRS preserves coordinates exactly
- Verified transform graph paths: GCRS->AltAz still uses ICRS path, AltAz->HADec still uses ICRS path, AltAz loopback uses ICRS-based merged transform
- Existing test suite has pre-existing IERS failures unrelated to changes

## Why This Matches the Public Issue

The issue requests "a direct approach to ITRS to Observed transformations that stays within the ITRS." The implementation follows the exact approach proposed in the issue: rotation matrices based on geodetic coordinates to convert between Earth-fixed and local horizon frames, with topocentric correction by subtracting the observer's geocentric ITRS position.
