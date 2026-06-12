# SWE-bench Baseline: astropy__astropy-12907

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

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

`separability_matrix` returns incorrect results for nested CompoundModels. When composing models using `&` where one operand is itself a CompoundModel (e.g., `m.Pix2Sky_TAN() & cm` where `cm = m.Linear1D(10) & m.Linear1D(5)`), the separability matrix incorrectly shows the nested model's outputs as non-separable. The expected behavior is that the nested form should produce the same result as the flat form (`m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5)`).

## Patch

- Files changed: `astropy/modeling/separable.py` (line 245)
- Behavioral change: In `_cstack()`, when the right operand is an already-computed coordinate matrix (ndarray, not a Model), the code now copies the actual matrix values (`= right`) instead of blindly filling with ones (`= 1`). The left operand path (line 240) already correctly copies with `= left`; this was an asymmetric bug affecting only the right side.
- Public tests run: All 11 tests in `astropy/modeling/tests/test_separable.py` pass.
- Why this matches the public issue statement: The fix ensures that nested CompoundModels in `&` expressions preserve their internal separability structure. The reported example `m.Pix2Sky_TAN() & cm` now correctly produces a block-diagonal matrix matching the non-nested equivalent.
