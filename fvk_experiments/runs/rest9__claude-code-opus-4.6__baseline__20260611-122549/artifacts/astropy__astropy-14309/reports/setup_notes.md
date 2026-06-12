# Setup Verification

- repo/ HEAD: 5b39d6c (tagged "base") — matches the pre-staged SWE-bench environment
- astropy version: 5.1
- pytest version: 7.4.0
- .venv/bin/python imports astropy correctly
- Quick test run: `pytest repo/astropy/io/fits/tests/test_connect.py` — 141 passed, 8 skipped, 5 xfailed
