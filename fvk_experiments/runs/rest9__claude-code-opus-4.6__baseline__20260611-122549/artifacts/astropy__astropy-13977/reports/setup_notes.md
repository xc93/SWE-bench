# Setup Verification

- Repo HEAD: `ab2a4c3020b459e033611f749b25db172baff991` (tagged "base"; different hash from spec but correct v5.1 content)
- astropy version: 5.1 (confirmed via `import astropy; print(astropy.__version__)`)
- pytest version: 7.4.0
- Pre-existing test failures (environment/numpy compat issues, not related to this change):
  - `test_quantity_array_methods.py::TestQuantityStatsFuncs::test_min`
  - Several tests in `test_quantity_non_ufuncs.py` (eig, eigh, completeness)
- All relevant unit tests pass: 2570 passed, 5 skipped, 2 xfailed
