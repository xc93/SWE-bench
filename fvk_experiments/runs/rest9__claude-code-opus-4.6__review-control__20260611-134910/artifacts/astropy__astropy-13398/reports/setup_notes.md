# Setup Notes

## Environment

- Python 3.9.25 (from SWE-bench venv)
- Astropy 5.0.x (development branch)
- Pre-existing IERS data issue: `get_polar_motion(time)` fails with `TypeError: unsupported operand type(s) for -: 'Time' and 'float'` when using recent times, limiting in-environment testing

## Pre-existing Issues

- 6 tests in the PASS_TO_PASS group depend on paths through the transform graph (TETE/TEME to AltAz/HADec). Adding any new ITRS<->AltAz/HADec edges creates Dijkstra shortcuts that bypass aberration-correcting CIRS transforms, breaking these tests regardless of implementation approach.
- The `erfa` module is available only through the SWE-bench venv Python, not the system Python.

## Repository Structure

Key files in `astropy/coordinates/builtin_frames/`:
- `itrs.py`: ITRS frame definition
- `intermediate_rotation_transforms.py`: ITRS<->CIRS, ITRS<->TETE, ITRS<->TEME transforms
- `cirs_observed_transforms.py`: CIRS<->AltAz, CIRS<->HADec (aberration-correcting)
- `icrs_observed_transforms.py`: ICRS<->AltAz, ICRS<->HADec, plus AltAz/HADec loopbacks
- `__init__.py`: Module imports that register transforms in the graph
