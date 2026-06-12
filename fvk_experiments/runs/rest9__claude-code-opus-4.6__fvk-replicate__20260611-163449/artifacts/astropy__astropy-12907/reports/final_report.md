# FVK SWE-bench Experiment: astropy__astropy-12907

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=0&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-12907
- Base commit: d16bfe05a744909de4b27f5875fe0d4ed41ce607
- Base commit URL: https://github.com/astropy/astropy/commit/d16bfe05a744909de4b27f5875fe0d4ed41ce607
- Version: 4.3
- Difficulty: 15 min - 1 hour

## Evaluator Shape

- FAIL_TO_PASS: 2
- PASS_TO_PASS: 13
- Official resolved condition: 2/2 FAIL_TO_PASS and 13/13 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

`separability_matrix` in `astropy.modeling.separable` does not compute separability correctly for nested CompoundModels. When models are concatenated with `&` and the right operand is itself a compound model (e.g., `Pix2Sky_TAN() & (Linear1D(10) & Linear1D(5))`), the result incorrectly shows all right-side outputs as coupled to all right-side inputs, even when they should be independent. The flat equivalent (`Pix2Sky_TAN() & Linear1D(10) & Linear1D(5)`) produces the correct diagonal result.

## v1 Patch

- Files changed: `astropy/modeling/separable.py`
- Behavioral change: In `_cstack`, when the right operand is an already-resolved ndarray (from a nested CompoundModel), the actual matrix values are now preserved (`= right`) instead of being replaced with all-ones (`= 1`).
- Public tests run: `astropy/modeling/tests/test_separable.py` — 11/11 passed

## v1 Score

FAIL_TO_PASS: 2 / 2
PASS_TO_PASS: 13 / 13
Resolved: true

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

1. The bug is an asymmetric treatment: the left ndarray branch uses `= left` (correct), but the right ndarray branch uses `= 1` (destroys separability information).
2. The bug only manifests when the right operand of `&` is a CompoundModel that has been recursively resolved to an ndarray.
3. The one-token fix (`1` → `right`) is provably correct: it mirrors the left branch logic and produces block-diagonal results matching the flat equivalent.
4. No other functions or operators are affected. The fix has zero collateral risk.

## v2 Patch

- Files changed: `astropy/modeling/separable.py`
- Behavioral change: Same as v1 — one-token fix on line 245
- Difference from v1: None. v2 is identical to v1.
- Why this follows from FVK: The ITERATION_GUIDANCE concluded that v1 is already correct, minimal, and complete. Any additional changes would risk introducing regressions without improving correctness.

## v2 Score

FAIL_TO_PASS: 2 / 2
PASS_TO_PASS: 13 / 13
Resolved: true

## Delta

FAIL_TO_PASS delta: 0 (2 - 2)
PASS_TO_PASS delta: 0 (13 - 13)
Resolved delta: unchanged

## Did FVK Help?

1. **Did v2 improve the bug-revealing tests?** No change — v1 already passed both.
2. **Did v2 preserve regressions better or worse than v1?** Same — both pass all 13.
3. **Did v2 get a worse total score?** No.
4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — scores are identical.
5. **Was the v2 change justified by the FVK artifacts?** Yes — FVK correctly identified that v1 needed no changes, preventing unnecessary modifications.
6. **Did FVK overgeneralize the desired behavior?** No. FVK correctly scoped the fix to the single broken line and explicitly warned against broader refactoring.
7. **What should be changed in the FVK process for regression-heavy SWE-bench tasks?** For simple one-line bugs like this, FVK's main value is as a safety check: confirming the fix is minimal and identifying regression risks. The formal specification machinery (K semantics, reachability claims) is overkill for a one-token typo fix. FVK could add a "complexity triage" step that recognizes trivially minimal fixes and abbreviates the formal analysis accordingly.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
