# FVK SWE-bench Experiment: astropy__astropy-14182

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=8&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-14182
- Base commit: a5917978be39d13cd90b517e1de4e7a539ffaa48
- Base commit URL: https://github.com/astropy/astropy/commit/a5917978be39d13cd90b517e1de4e7a539ffaa48
- Version: 5.1
- Difficulty: 15 min - 1 hour

## Evaluator Shape

- FAIL_TO_PASS: 1
- PASS_TO_PASS: 9
- Official resolved condition: 1/1 FAIL_TO_PASS and 9/9 PASS_TO_PASS

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no
- Private evaluator logs used for v2: no

## Public Problem Summary

The RST (RestructuredText) table writer in `astropy.io.ascii` does not support the `header_rows` parameter. When calling `tbl.write(sys.stdout, format="ascii.rst", header_rows=["name", "unit"])`, it raises `TypeError: RST.__init__() got an unexpected keyword argument 'header_rows'`. The `FixedWidth` parent class already supports `header_rows`, but the `RST` subclass doesn't accept or forward it.

## v1 Patch

- Files changed: `astropy/io/ascii/rst.py`
- Behavioral change: `RST.__init__` now accepts `header_rows` and forwards it to `FixedWidth.__init__`. `RST.write()` uses `len(self.header.header_rows)` instead of hardcoded `1` for position line index.
- Public tests run: All 9 tests in `astropy/io/ascii/tests/test_rst.py` — all passed.

## v1 Score

FAIL_TO_PASS: 0 / 1
PASS_TO_PASS: 9 / 9
Resolved: false

## FVK Artifacts

- fvk/SPEC.md
- fvk/FINDINGS.md
- fvk/PROOF_OBLIGATIONS.md
- fvk/ITERATION_GUIDANCE.md

## Key FVK Findings

**Finding 2 (CRITICAL):** The read path is broken for multi-row headers. `SimpleRSTData.start_line = 3` is hardcoded at the class level and only works for single header row. With `header_rows=["name", "unit"]`, the RST format has the separator `===` at line 3 and data starting at line 4, but the reader treats line 3 as the first data row.

**Root cause:** v1 only fixed the write path (accepting `header_rows` and fixing position line indexing) but did not adjust `data.start_line` for the read path.

**Fix:** Add `self.data.start_line = len(self.header.header_rows) + 2` in `RST.__init__`. This is backward compatible: `len(["name"]) + 2 = 3` matches the existing hardcoded value.

## v2 Patch

- Files changed: `astropy/io/ascii/rst.py`
- Behavioral change: Same as v1, plus dynamic `data.start_line` for correct reading with multi-row headers.
- Difference from v1: One additional line in `RST.__init__`: `self.data.start_line = len(self.header.header_rows) + 2`
- Why this follows from FVK: The FVK specification required both read and write contracts, and the round-trip proof obligation (O4) revealed the broken read path. The non-regression obligation (O5) confirmed backward compatibility of the formula.

## v2 Score

FAIL_TO_PASS: 1 / 1
PASS_TO_PASS: 9 / 9
Resolved: true

## Delta

FAIL_TO_PASS delta: +1 (0 → 1)
PASS_TO_PASS delta: 0 (9 → 9)
Resolved delta: improved (false → true)

## Did FVK Help?

1. **Did v2 improve the bug-revealing tests?** Yes. v1 scored 0/1, v2 scored 1/1.
2. **Did v2 preserve regressions better or worse than v1?** Same — both scored 9/9.
3. **Did v2 get a worse total score?** No, v2 is strictly better.
4. **If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?** N/A — v2 did not get worse.
5. **Was the v2 change justified by the FVK artifacts?** Yes. Finding 2 in FINDINGS.md identified the exact bug (hardcoded `data.start_line`), and ITERATION_GUIDANCE.md prescribed the exact one-line fix.
6. **Did FVK overgeneralize the desired behavior?** No. FVK correctly identified that both read and write paths needed to work, which is implied by the public issue's context (RST tables used for documentation workflows where round-tripping is expected).
7. **What should be changed in the FVK process for regression-heavy SWE-bench tasks?** The FVK process correctly handled this case by explicitly including non-regression obligations (O5-O8) and verifying backward compatibility of the formula. For regression-heavy tasks, the key lesson is: always verify that dynamic parameters produce the same values as hardcoded defaults in the base case.

## Artifacts

- patches/solution_v1.patch
- patches/solution_v2.patch
- reports/v1_notes.md
- reports/v1_score.md
- reports/v2_notes.md
- reports/v2_score.md
- reports/final_report.md
