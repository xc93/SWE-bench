# FVK SWE-bench Experiment: astropy__astropy-13579

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

## Evaluator Shape

- FAIL_TO_PASS: 1
- PASS_TO_PASS: 40
- Official resolved condition: 1/1 FAIL_TO_PASS and 40/40 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

`SlicedLowLevelWCS.world_to_pixel_values` produces incorrect results when the WCS has a non-trivial PC matrix that couples spectral and spatial dimensions. When reconstructing the full world coordinate array for the underlying WCS, dropped world dimensions (those not correlated with any kept pixel dimension) were filled with a hardcoded `1.` instead of the world coordinate corresponding to the pixel value in the slice. This caused the inverse transform to produce essentially infinite pixel values for certain dimensions.

## v1 Patch

- Files changed: `astropy/wcs/wcsapi/wrappers/sliced_wcs.py`
- Behavioral change: In `world_to_pixel_values`, dropped world dimensions are filled with the actual world coordinate at the sliced pixel position (computed via `_pixel_to_world_values_all`) instead of `1.`.
- Public tests run: `astropy/wcs/wcsapi/wrappers/tests/test_sliced_wcs.py` — 40/40 passed. Manual reproduction of the issue confirmed the fix.

## v1 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 40 / 40
Resolved: true

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

1. **Root cause confirmed**: The hardcoded `1.` fill value for dropped world dimensions is the sole root cause. v1 correctly fixes it.
2. **Consistency with existing code**: v1 uses the same `_pixel_to_world_values_all(*[0]*len(self._pixel_keep))` pattern as the `dropped_world_dimensions` property.
3. **Uncoupled WCS equivalence**: For all existing tests (which use uncoupled WCS with diagonal PC matrices), the new fill value produces identical results to the old `1.`, because the dropped world dimension doesn't affect kept pixel dimensions.
4. **14 proof obligations verified**: 1 bug-fix obligation + 13 non-regression obligations, all satisfied by v1.
5. **Conservative recommendation**: With a 40:1 regression-to-bug ratio, FVK recommended no changes for v2.

## v2 Patch

- Files changed: `astropy/wcs/wcsapi/wrappers/sliced_wcs.py`
- Behavioral change: Identical to v1.
- Difference from v1: None.
- Why this follows from FVK: ITERATION_GUIDANCE.md recommended keeping v1 unchanged. The patch is correct, minimal, consistent with existing patterns, and all proof obligations are satisfied.

## v2 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 40 / 40
Resolved: true

## Delta

FAIL_TO_PASS delta: 0 (1 - 1)
PASS_TO_PASS delta: 0 (40 - 40)
Resolved delta: unchanged

## Did FVK Help?

1. **Did v2 improve the bug-revealing tests?** No change — v1 already passed 1/1.
2. **Did v2 preserve regressions better or worse than v1?** Same — 40/40 in both.
3. **Did v2 get a worse total score?** No — identical.
4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — v2 did not get worse.
5. **Was the v2 change justified by the FVK artifacts?** Yes — FVK correctly identified that v1 needed no modification.
6. **Did FVK overgeneralize the desired behavior?** No — FVK was appropriately conservative, identifying that the fix is minimal and targeted.
7. **What should be changed in the FVK process for regression-heavy SWE-bench tasks?** FVK correctly handled this case by explicitly analyzing all 14 non-regression obligations and recommending no changes when v1 was already resolved. For regression-heavy tasks where v1 is imperfect, the FVK's proof obligations framework would help identify which specific regressions to guard against, but the conservative "if it works, don't touch it" guidance is the right default.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
