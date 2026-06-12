# FVK SWE-bench Experiment: astropy__astropy-14096

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=7&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-14096
- Base commit: 1a4462d72eb03f30dc83a879b1dd57aac8b2c18b
- Base commit URL: https://github.com/astropy/astropy/commit/1a4462d72eb03f30dc83a879b1dd57aac8b2c18b
- Version: 5.1
- Difficulty: 15 min - 1 hour

## Evaluator Shape

- FAIL_TO_PASS: 1
- PASS_TO_PASS: 426
- Official resolved condition: 1/1 FAIL_TO_PASS and 426/426 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

Subclassed `SkyCoord` gives misleading attribute access message. When a `SkyCoord` subclass defines a property whose getter raises `AttributeError` internally (e.g., by accessing a non-existent attribute), `SkyCoord.__getattr__` masks the original error and instead reports that the *property* doesn't exist. The user gets `"object has no attribute 'prop'"` when the real issue is `"object has no attribute 'random_attr'"` inside the property getter.

## v1 Patch

- Files changed: `astropy/coordinates/sky_coordinate.py`
- Behavioral change: In `__getattr__`, before raising the generic "no attribute" error, scan `type(self).__mro__` for the attribute. If found as a descriptor (has `__get__`), re-invoke it to propagate the original `AttributeError`.
- Public tests run: `astropy/coordinates/tests/test_sky_coord.py` — 426 passed, 1 failed (unrelated leap-second issue), 3 skipped, 1 xfailed.

## v1 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 426 / 426
Resolved: true

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

1. **Fix correctly placed**: The descriptor check runs after all frame-based lookups (frame name, frame attributes, frame delegation, frame transformation), so it never interferes with SkyCoord's coordinate resolution.
2. **Appropriately general**: `hasattr(desc, '__get__')` covers properties, cached_property, custom descriptors, and slot descriptors without over-catching.
3. **No recursion risk**: Each `__getattr__` call invokes the descriptor at most once; the chain terminates at non-descriptor leaf attributes.
4. **Initialization safety**: Safe during `__init__` because the descriptor check terminates with the same error as without the fix.
5. **All proof obligations satisfied**: v1 meets all 18 proof obligations and violates no forbidden changes.

## v2 Patch

- Files changed: `astropy/coordinates/sky_coordinate.py` (identical to v1)
- Behavioral change: Same as v1
- Difference from v1: None — v2 is identical to v1
- Why this follows from FVK: ITERATION_GUIDANCE.md recommended keeping v1 unchanged because all proof obligations are satisfied and any modification risks regressions without improving the already-perfect score.

## v2 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 426 / 426
Resolved: true

## Delta

FAIL_TO_PASS delta: 0
PASS_TO_PASS delta: 0
Resolved delta: unchanged

## Did FVK Help?

1. **Did v2 improve the bug-revealing tests?** No change — v1 already passed 1/1.
2. **Did v2 preserve regressions better or worse than v1?** Same — 426/426 in both.
3. **Did v2 get a worse total score?** No.
4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — scores are identical.
5. **Was the v2 change justified by the FVK artifacts?** Yes — FVK correctly identified that no changes were needed, and the "keep v1 unchanged" guidance was the right call.
6. **Did FVK overgeneralize the desired behavior?** No — FVK correctly scoped the fix to the specific `__getattr__` failure path.
7. **What should be changed in the FVK process for regression-heavy SWE-bench tasks?** FVK performed well here as a conservative guard: it confirmed v1 was correct and prevented unnecessary over-iteration. For regression-heavy tasks, FVK's main value is in the proof obligations and forbidden-changes lists, which provide a formal basis for deciding "don't touch it." The key improvement would be earlier detection of when v1 is already optimal, to avoid spending time on a v2 that will inevitably be identical.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
