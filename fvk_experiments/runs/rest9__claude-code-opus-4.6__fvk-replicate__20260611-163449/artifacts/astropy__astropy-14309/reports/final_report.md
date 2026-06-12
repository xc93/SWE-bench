# FVK SWE-bench Experiment: astropy__astropy-14309

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=9&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-14309
- Base commit: cdb66059a2feb44ee49021874605ba90801f9986
- Base commit URL: https://github.com/astropy/astropy/commit/cdb66059a2feb44ee49021874605ba90801f9986
- Version: 5.1
- Difficulty: <15 min fix

## Evaluator Shape

- FAIL_TO_PASS: 1
- PASS_TO_PASS: 141
- Official resolved condition: 1/1 FAIL_TO_PASS and 141/141 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

`identify_format("write", Table, "bububu.ecsv", None, [], {})` raises `IndexError: tuple index out of range` because `is_fits()` in `astropy/io/fits/connect.py` unconditionally accesses `args[0]` on line 72 without checking if `args` is empty. This happens when `filepath` is a string without a FITS extension and no positional arguments are passed.

## v1 Patch

- Files changed: `astropy/io/fits/connect.py` (1 line)
- Behavioral change: Added `bool(args)` guard before `isinstance(args[0], ...)` so `is_fits()` returns `False` when args is empty instead of crashing
- Public tests run: `test_registries.py` (221 passed), `test_connect.py` (141 passed)

## v1 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 141 / 141
Resolved: true

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

1. **v1 is correct and minimal** — the `bool(args)` guard exactly addresses the bug without side effects
2. **votable/connect.py has the same pattern** (Finding 2) — but fixing it is out of scope and risks regressions
3. **v1 is consistent with the IO registry API contract** — `args` can be empty is an implicit requirement
4. **No behavioral change for valid inputs** — `bool(args)` short-circuits only when args is empty
5. **All 10 proof obligations satisfied** — including bug fix and 7 non-regression obligations

## v2 Patch

- Files changed: `astropy/io/fits/connect.py` (1 line)
- Behavioral change: Same as v1 — `bool(args)` guard
- Difference from v1: None — v2 is identical to v1
- Why this follows from FVK: ITERATION_GUIDANCE.md explicitly recommends keeping v2 identical to v1 because the fix is already complete and any additional changes risk regressions

## v2 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 141 / 141
Resolved: true

## Delta

FAIL_TO_PASS delta: 0
PASS_TO_PASS delta: 0
Resolved delta: unchanged

## Did FVK Help?

1. **Did v2 improve the bug-revealing tests?** No — v1 already passed 1/1. No improvement possible.

2. **Did v2 preserve regressions better or worse than v1?** Same — 141/141 in both.

3. **Did v2 get a worse total score?** No — identical scores.

4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — v2 did not get worse.

5. **Was the v2 change justified by the FVK artifacts?** Yes — FVK's key contribution was confirming that v1 was already correct and that no additional changes should be made. This is itself valuable: FVK prevented unnecessary "improvements" that could have introduced regressions.

6. **Did FVK overgeneralize the desired behavior?** No — FVK correctly identified that the votable fix (Finding 2) was out of scope and should not be included. This is the right call for a regression-heavy task.

7. **What should be changed in the FVK process for regression-heavy SWE-bench tasks?** For tasks where v1 already resolves perfectly, FVK's primary value is as a "do no harm" safeguard — confirming the fix is complete and preventing unnecessary changes. The non-regression obligations (PO-2 through PO-10) were the most important FVK output. For future regression-heavy tasks, FVK should front-load the non-regression analysis and give it equal weight to the bug-fix analysis.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
