# Setup Verification

- `repo/` HEAD: a0241a1 (tagged "base" — matches environment_setup_commit cdf311e, which is the setup commit that installs the repo at base commit 0df94ff)
- `.venv/bin/python` imports astropy 5.0
- pytest 7.4.0 works; ran `astropy/wcs/wcsapi/wrappers/tests/test_sliced_wcs.py` — 40 passed
- Pre-existing test failures in `test_time_cube` and `test_spectralcoord_frame` due to expired IERS data / warning-as-error — unrelated to our change
