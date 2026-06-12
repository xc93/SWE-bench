# Setup Notes

## Environment Verification

- repo HEAD: `1561f5f` (tagged as "base"; differs from expected `0df94ff` likely due to environment setup commit)
- `astropy.__version__`: 5.0
- `pytest --version`: 7.4.0
- Bug reproduction: confirmed with the low-level API test from the issue hints
- Existing test suite: `test_sliced_wcs.py` runs 40 tests, all passing

## Notes

- The repo HEAD hash differs from the expected base commit `0df94ff7097961e92fd7812036a24b145bc13ca8`. This appears to be due to the workspace build process applying an environment setup commit on top. The source code for the affected file (`sliced_wcs.py`) matches the expected state from the base commit.
- The `.venv` Python environment correctly imports astropy 5.0 from the staged repo.
