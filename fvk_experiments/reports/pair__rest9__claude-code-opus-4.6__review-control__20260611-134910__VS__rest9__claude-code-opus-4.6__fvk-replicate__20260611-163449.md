# Pair comparison — review-control vs fvk-replicate

Generated: 2026-06-12 00:46 UTC

| | review-control | fvk-replicate |
|---|---|---|
| **solved_count** | **7 / 9** | **7 / 9** |
| run_id | `rest9__claude-code-opus-4.6__review-control__20260611-134910` | `rest9__claude-code-opus-4.6__fvk-replicate__20260611-163449` |
| model | `claude-code-opus-4.6__review-control` | `claude-code-opus-4.6__fvk-replicate` |
| treatment prompt | — | `v1` (sha256 `b76db2120bf9…`) |

**solved_count_baseline = 7** · **solved_count_treatment = 7** · Δ = +0

## Per-instance pairs

| instance_id | review-control resolved | fvk-replicate resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ✅ yes | ✅ yes | = |
| astropy__astropy-13398 | ❌ no | ❌ no | = |
| astropy__astropy-13453 | ❌ no | ❌ no | = |
| astropy__astropy-13579 | ✅ yes | ✅ yes | = |
| astropy__astropy-13977 | ✅ yes | ✅ yes | = |
| astropy__astropy-14096 | ✅ yes | ✅ yes | = |
| astropy__astropy-14182 | ✅ yes | ✅ yes | = |
| astropy__astropy-14309 | ✅ yes | ✅ yes | = |

- Solved by both: 7 · by neither: 2
- Solved **only by fvk-replicate**: 0 
- Solved **only by review-control**: 0 

With n=9 this is directional evidence, not statistical significance.

## Run reports

- review-control: `fvk_experiments/runs/rest9__claude-code-opus-4.6__review-control__20260611-134910/report.md`
- fvk-replicate: `fvk_experiments/runs/rest9__claude-code-opus-4.6__fvk-replicate__20260611-163449/report.md`
