# Pair comparison — baseline vs fvk-v2

Generated: 2026-06-10 12:39 UTC

| | baseline | fvk-v2 |
|---|---|---|
| **solved_count** | **2 / 10** | **4 / 10** |
| run_id | `astropy10__ds-v4-pro-think__baseline__20260610-115611` | `astropy10__ds-v4-pro-think__fvk-v2__20260610-122143` |
| model | `deepseek-v4-pro-think__baseline` | `deepseek-v4-pro-think__fvk-v2` |
| FVK prompt | — | `v2` (sha256 `8c8f31b1e7b2…`) |

**solved_count_baseline = 2** · **solved_count_fvk = 4** · Δ = +2

## Per-instance pairs

| instance_id | baseline resolved | fvk-v2 resolved | flip |
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
| astropy__astropy-14309 | ❌ no | ✅ yes | 📈 fvk-only |

- Solved by both: 2 · by neither: 6
- Solved **only with FVK**: 2 ['astropy__astropy-14096', 'astropy__astropy-14309']
- Solved **only by baseline**: 0 

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__ds-v4-pro-think__baseline__20260610-115611/report.md`
- fvk-v2: `fvk_experiments/runs/astropy10__ds-v4-pro-think__fvk-v2__20260610-122143/report.md`
