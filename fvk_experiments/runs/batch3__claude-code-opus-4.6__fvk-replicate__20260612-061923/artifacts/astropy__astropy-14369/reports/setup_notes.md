# Setup Notes

- `.venv/` was pre-staged and working; astropy 5.1 imports successfully.
- `repo/` is checked out at a truncated-history base commit (single "base" commit); content matches `fa4e8d1cd279acf9b24560813c8652494ccd5922`.
- Test runner verified: `pytest repo/astropy/io/ascii/tests/test_cds.py` passes all 12 tests.
- `pytest repo/astropy/units/tests/test_format.py` passes all 732 tests.
