# SWE-bench Baseline: astropy__astropy-13579

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=5&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-13579
- Base commit: 0df94ff7097961e92fd7812036a24b145bc13ca8
- Base commit URL: https://github.com/astropy/astropy/commit/0df94ff7097961e92fd7812036a24b145bc13ca8
- Version: 5.0
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

`SlicedLowLevelWCS.world_to_pixel_values` returns incorrect results when the underlying WCS has coupled dimensions (non-trivial PC matrix). When a dimension is sliced out (e.g., wavelength), the `world_to_pixel_values` method fills in a hardcoded value of `1.` for dropped world dimensions. This is incorrect — it should use the actual world coordinate corresponding to the pixel value at which the slice was taken. The incorrect fill value causes the inverse transform to produce wildly wrong pixel coordinates for coupled dimensions.

## Patch

- Files changed: `astropy/wcs/wcsapi/wrappers/sliced_wcs.py`
- Behavioral change: For dropped world dimensions in `world_to_pixel_values`, instead of filling in `1.`, compute the actual world coordinate at the slice point using `_pixel_to_world_values_all` and use that value. This ensures the inverse WCS transform has the correct world coordinates for all dimensions.
- Public tests run: `astropy/wcs/wcsapi/wrappers/tests/test_sliced_wcs.py` — 40 passed; `astropy/wcs/wcsapi/tests/` — 44 passed (28 deselected due to pre-existing unrelated failures)
- Why this matches the public issue statement: The issue explicitly identifies line 253-254 (the `1.` value) as the root cause, and states it should be "the world coordinate corresponding to the pixel value in the slice." The fix computes exactly that using the existing `_pixel_to_world_values_all` helper, which evaluates the WCS transform at the sliced pixel positions.
