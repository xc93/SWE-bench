# SWE-bench Baseline: astropy__astropy-13398

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=3&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-13398
- Base commit: 6500928dc0e57be8f06d1162eacc3ba5e2eff692
- Base commit URL: https://github.com/astropy/astropy/commit/6500928dc0e57be8f06d1162eacc3ba5e2eff692
- Version: 5.0
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

Users wanting to observe near-Earth objects (satellites, airplanes, mountains) experience inaccurate ITRS to AltAz/HADec transforms because the existing path goes through CIRS/ICRS, which applies stellar aberration corrections inappropriate for near-Earth objects. The issue proposes a direct ITRS to observed (AltAz/HADec) transformation that stays entirely within the ITRS framework, treating ITRS coordinates as time-invariant and performing only geometric rotations between the geocentric ITRS frame and the observer's local horizontal (AltAz) or hour angle-declination (HADec) frame.

## Patch

- Files changed:
  - `astropy/coordinates/builtin_frames/itrs_observed_transforms.py` (new file)
  - `astropy/coordinates/builtin_frames/__init__.py` (added import)

- Behavioral change:
  - Added direct ITRS <-> AltAz transform (registered in frame transform graph)
  - Added direct ITRS <-> HADec transform (registered in frame transform graph)
  - The transforms compute topocentric ITRS position by subtracting the observer's ITRS position, then apply a geometric rotation matrix to convert between ITRS Cartesian and AltAz/HADec coordinates
  - ITRS positions are treated as time-invariant (no obstime synchronization)
  - No stellar aberration is applied (appropriate for near-Earth objects)
  - The ITRS->AltAz path is now 1 step instead of 2 (previously ITRS->CIRS->AltAz)

- Public tests run:
  - Manual verification of ITRS->AltAz for straight-overhead case (alt=90 deg exactly)
  - Manual verification of ITRS->HADec for straight-overhead case (HA=0, Dec=latitude exactly)
  - Manual verification of ITRS->AltAz->ITRS roundtrip (0 mm separation)
  - Manual verification of ITRS->HADec->ITRS roundtrip (0 mm separation)
  - Manual verification that CIRS->AltAz, ICRS->AltAz, CIRS->ITRS paths still work
  - Manual verification of satellite observation use case with array inputs
  - Note: pytest-based tests could not run in this environment due to numpy binary incompatibility and IERS data access issues

- Why this matches the public issue statement:
  - Implements exactly the code provided in the issue description
  - Registers direct ITRS<->AltAz and ITRS<->HADec transforms in the frame transform graph
  - Uses FunctionTransformWithFiniteDifference (same as the issue code)
  - Treats ITRS coordinates as time-invariant (key feature described in the issue)
  - Stays entirely within ITRS for the conversion (no SSB reference)
  - Computes topocentric position by subtracting observer ITRS coordinates
  - Applies geometric rotation matrix based on geodetic longitude/latitude
