# Pair comparison — baseline vs fvk-v3

Generated: 2026-06-10 12:39 UTC

| | baseline | fvk-v3 |
|---|---|---|
| **solved_count** | **2 / 10** | **2 / 10** |
| run_id | `astropy10__ds-v4-pro-think__baseline__20260610-115611` | `astropy10__ds-v4-pro-think__fvk-v3__20260610-123129` |
| model | `deepseek-v4-pro-think__baseline` | `deepseek-v4-pro-think__fvk-v3` |
| FVK prompt | — | `v3` (sha256 `8e64c5149c8c…`) |

**solved_count_baseline = 2** · **solved_count_fvk = 2** · Δ = +0

## Per-instance pairs

| instance_id | baseline resolved | fvk-v3 resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-13033 | ❌ no | ❌ no | = |
| astropy__astropy-13236 | ❌ no | ❌ no | = |
| astropy__astropy-13398 | ❌ no | ❌ no | = |
| astropy__astropy-13453 | ❌ no | ❌ no | = |
| astropy__astropy-13579 | ✅ yes | ✅ yes | = |
| astropy__astropy-13977 | ❌ no | ❌ no | = |
| astropy__astropy-14096 | ❌ no | ❌ no | = |
| astropy__astropy-14182 | ❌ no | ❌ no | = |
| astropy__astropy-14309 | ❌ no | ✅ yes | 📈 fvk-only |

- Solved by both: 1 · by neither: 7
- Solved **only with FVK**: 1 ['astropy__astropy-14309']
- Solved **only by baseline**: 1 ['astropy__astropy-12907']

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__ds-v4-pro-think__baseline__20260610-115611/report.md`
- fvk-v3: `fvk_experiments/runs/astropy10__ds-v4-pro-think__fvk-v3__20260610-123129/report.md`
