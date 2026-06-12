# Review-Control SWE-bench Experiment: pylint-dev__pylint-8898

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=329&length=1
- Repo: pylint-dev/pylint
- Repo URL: https://github.com/pylint-dev/pylint.git
- Instance ID: pylint-dev__pylint-8898
- Base commit: 1f8c4d9eb185c16a2c1d881c054f015e1c2eb334
- Base commit URL: https://github.com/pylint-dev/pylint/commit/1f8c4d9eb185c16a2c1d881c054f015e1c2eb334
- Version: 3.0
- Difficulty: 1-4 hours

## Evaluator Shape

- FAIL_TO_PASS: 1
- PASS_TO_PASS: 18
- Official resolved condition: 1/1 FAIL_TO_PASS and 18/18 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

The `bad-names-rgxs` option (and other `regexp_csv`-typed options) in pylint split their value on commas using a naive CSV splitter. This breaks regular expressions containing commas, specifically regex quantifiers like `{1,3}`. For example, `bad-names-rgxs = "(foo{1,3})"` causes pylint to crash because the pattern is split into `(foo{1` and `3})`, both of which are invalid regex fragments.

## v1 Patch

- Files changed: `pylint/config/argument.py`
- Behavioral change: Added `_regexp_csv_split` helper that tracks curly brace depth and only splits on commas at brace depth 0. Modified `_regexp_csv_transfomer` to use this new function instead of the naive `_csv_transformer`.
- Public tests run: `tests/config/test_config.py` (15/16 pass; `test_csv_regex_error` fails because it tested the old broken behavior)

## v1 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 18 / 18
Resolved: true

## Review Artifacts

- review/FINDINGS.md
- review/ITERATION_GUIDANCE.md

## Key Review Findings

1. v1 is correct and minimal — only modifies the `regexp_csv` transformer, not shared CSV utilities
2. Edge case handling is consistent with the old `_splitstrip` behavior (whitespace stripping, empty entry discarding)
3. Brace tracking is robust (handles unmatched braces, nested braces, depth never goes negative)
4. No overreach: does not modify `_regexp_paths_csv_transfomer` or any test files
5. No bugs found in the patch

## v2 Patch

- Files changed: `pylint/config/argument.py`
- Behavioral change: Identical to v1
- Difference from v1: None — the review found no issues requiring changes
- Why this follows from the review: The review confirmed v1 is correct, minimal, and already fully resolved

## v2 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 18 / 18
Resolved: true

## Delta

FAIL_TO_PASS delta: 0
PASS_TO_PASS delta: 0
Resolved delta: unchanged

## Did the Review Help?

1. Did v2 improve the bug-revealing tests? No change needed — v1 already passed 1/1.
2. Did v2 preserve regressions better or worse than v1? Same — v1 already passed 18/18.
3. Did v2 get a worse total score? No.
4. If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both? N/A.
5. Was the v2 change justified by the review artifacts? The review correctly concluded no changes were needed.
6. Did the review overgeneralize the desired behavior? No — the review explicitly identified what should NOT be changed.
7. What should be changed in the review process for regression-heavy SWE-bench tasks? For tasks where v1 already achieves full resolution, the review's primary value is confirming correctness and providing a "do not change" recommendation. The review process correctly applied the principle of "first, do no harm" — recognizing that a passing patch should not be modified without strong justification.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
