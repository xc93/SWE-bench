# FVK SWE-bench Experiment: pylint-dev__pylint-8898

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

The `bad-names-rgxs` pylint option (and all other `regexp_csv`-type options) mangles regular expressions containing commas. The `_regexp_csv_transfomer` function naively splits on all commas via `_csv_transformer`, breaking regex quantifiers like `{1,3}`. For example, `(foo{1,3})` is split into `(foo{1` and `3})`, where the first part is an invalid regex causing pylint to crash.

## v1 Patch

- Files changed: `pylint/config/argument.py`
- Behavioral change: Replaced naive comma splitting in `_regexp_csv_transfomer` with a brace-aware `_regexp_csv_split` function that does not split on commas inside `{...}` blocks.
- Public tests run: `repo/tests/config/test_config.py` (15 passed, 1 failed — the failing test `test_csv_regex_error` tests old broken behavior)

## v1 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 18 / 18
Resolved: true

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

1. v1 correctly identifies the root cause and fixes it minimally.
2. v1 is properly scoped — only modifies `_regexp_csv_transfomer`, does not touch `_csv_transformer` or other shared utilities.
3. All proof obligations (bug-fix and non-regression) are satisfied.
4. No unnecessary changes or overgeneralizations detected.
5. FVK recommended keeping v2 identical to v1.

## v2 Patch

- Files changed: `pylint/config/argument.py`
- Behavioral change: Same as v1
- Difference from v1: None — v2 is identical to v1
- Why this follows from FVK: FVK analysis confirmed v1 was correct, minimal, and fully resolved. Any change would risk regressions for zero additional benefit.

## v2 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 18 / 18
Resolved: true

## Delta

FAIL_TO_PASS delta: 0
PASS_TO_PASS delta: 0
Resolved delta: unchanged

## Did FVK Help?

1. Did v2 improve the bug-revealing tests? No — v1 already passed all bug-revealing tests.
2. Did v2 preserve regressions better or worse than v1? Same — v2 is identical to v1.
3. Did v2 get a worse total score? No.
4. If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both? N/A.
5. Was the v2 change justified by the FVK artifacts? Yes — FVK correctly recommended no changes.
6. Did FVK overgeneralize the desired behavior? No.
7. What should be changed in the FVK process for regression-heavy SWE-bench tasks? When v1 is already fully resolved, FVK's primary value is confirming the fix is correct and avoiding unnecessary changes. For cases where v1 fails, FVK's structured analysis of proof obligations and forbidden changes would help guide targeted improvements. The non-regression obligations framework (explicitly listing what must not change) is particularly valuable for regression-heavy tasks.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
