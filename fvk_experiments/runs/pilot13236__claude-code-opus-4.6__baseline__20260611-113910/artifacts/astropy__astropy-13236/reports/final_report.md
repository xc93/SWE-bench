# SWE-bench Baseline: astropy__astropy-13236

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=2&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-13236
- Base commit: 6ed769d58d89380ebaa1ef52b300691eefda8928
- Base commit URL: https://github.com/astropy/astropy/commit/6ed769d58d89380ebaa1ef52b300691eefda8928
- Version: 5.0
- Difficulty: 15 min - 1 hour

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

When adding a structured `np.ndarray` (an array with a compound dtype like `[('x', 'i4'), ('y', 'U2')]`) to an Astropy `Table`, the array was automatically converted to an `NdarrayMixin` via `.view(NdarrayMixin)`. This auto-transformation was originally necessary because structured dtype `Column` didn't work well, especially for serialization. After improvements in PR #12644, structured `Column` now works correctly. The issue requests removing this auto-transformation so structured arrays are added directly as `Column` objects.

The discussion consensus was to make this change immediately (no deprecation warning), since NdarrayMixin was "somewhat crippled" (I/O and repr limitations) and any NdarrayMixin functionality is compatible with Column (both are ndarray subclasses).

## Patch

- Files changed:
  - `astropy/table/table.py` — Removed the 6-line block that auto-converted structured ndarrays to NdarrayMixin
  - `astropy/table/tests/test_mixin.py` — Updated `test_ndarray_mixin` to assert structured arrays become `Column` (not `NdarrayMixin`); explicitly created `NdarrayMixin` objects still remain as `NdarrayMixin`
- Behavioral change: Structured `np.ndarray` objects added to a `Table` are now stored as `Column` instead of being auto-converted to `NdarrayMixin`. Explicitly created `NdarrayMixin` objects are unaffected.
- Public tests run:
  - `astropy/table/tests/test_mixin.py` — 186 passed, 6 skipped (1 pre-existing failure excluded)
  - `astropy/table/tests/test_pprint.py -k structured` — 2 passed
  - `astropy/table/tests/test_init_table.py -k structured` — 2 passed
- Why this matches the public issue statement: The issue explicitly requests removing the auto-transform code block that converts structured ndarrays to NdarrayMixin, and the discussion consensus is to do so immediately. This patch removes exactly that block and updates the corresponding test.
