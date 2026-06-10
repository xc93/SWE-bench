# Pair comparison — baseline vs review-v5

Generated: 2026-06-10 13:23 UTC

| | baseline | review-v5 |
|---|---|---|
| **solved_count** | **2 / 10** | **3 / 10** |
| run_id | `astropy10__ds-v4-pro-think__baseline__20260610-115611` | `astropy10__ds-v4-pro-think__review-v5__20260610-130805` |
| model | `deepseek-v4-pro-think__baseline` | `deepseek-v4-pro-think__review-v5` |
| FVK prompt | — | `v5` (sha256 `09becca148f3…`) |

**solved_count_baseline = 2** · **solved_count_fvk = 3** · Δ = +1

## Per-instance pairs

| instance_id | baseline resolved | review-v5 resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ❌ no | ❌ no | = |
| astropy__astropy-13236 | ❌ no | ❌ no | = |
| astropy__astropy-13398 | ❌ no | ❌ no | = |
| astropy__astropy-13453 | ❌ no | ❌ no | = |
| astropy__astropy-13579 | ✅ yes | ✅ yes | = |
| astropy__astropy-13977 | ❌ no | ❌ no | = |
| astropy__astropy-14096 | ❌ no | ✅ yes | 📈 fvk-only |
| astropy__astropy-14182 | ❌ no | ❌ no | = |
| astropy__astropy-14309 | ❌ no | ❌ no | = |

- Solved by both: 2 · by neither: 7
- Solved **only with FVK**: 1 ['astropy__astropy-14096']
- Solved **only by baseline**: 0 

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__ds-v4-pro-think__baseline__20260610-115611/report.md`
- review-v5: `fvk_experiments/runs/astropy10__ds-v4-pro-think__review-v5__20260610-130805/report.md`
