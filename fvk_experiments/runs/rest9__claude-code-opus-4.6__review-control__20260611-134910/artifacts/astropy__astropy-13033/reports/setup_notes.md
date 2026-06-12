# Setup Notes

## Environment Verification

- `repo/` HEAD: `734f571` (tagged as "base"); workspace pre-built, astropy version 4.3 confirmed
- `.venv/bin/python` imports astropy 4.3 correctly
- pytest 7.4.0 installed and working
- Quick test `TestTimeSeries::test_add_column` passes

## Notes

- numpy RuntimeWarning about ndarray size change appears but does not affect functionality
- Internet access is disabled in this environment
