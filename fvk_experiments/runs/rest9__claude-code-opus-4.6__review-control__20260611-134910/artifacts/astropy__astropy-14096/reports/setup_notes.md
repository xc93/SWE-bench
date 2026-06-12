# Setup Notes

## Verification

- `repo/` HEAD: `792cd2ce20f51b7f19ec68d77a2fd46641bcdfac` (repackaged "base" commit; content matches base commit `1a4462d`)
- `.venv/bin/python` imports astropy 5.1
- pytest 7.4.0 is available
- Quick test: `test_skycoord_three_components` passes (32 parametrized cases)
- Full `test_sky_coord.py`: 426 passed, 1 pre-existing failure (`test_repr_altaz` due to expired leap-second file with no internet)

## Notes

- The HEAD commit hash differs from the expected base commit because the workspace staging process repackaged the repo. The code content is equivalent.
- Internet access is disabled in this environment, causing a leap-second file warning in one test. This is pre-existing and unrelated to the issue.
