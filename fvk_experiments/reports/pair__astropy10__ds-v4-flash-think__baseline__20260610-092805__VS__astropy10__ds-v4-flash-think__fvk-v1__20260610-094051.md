# Pair comparison — baseline vs fvk-v1

Generated: 2026-06-10 10:07 UTC

| | baseline | fvk-v1 |
|---|---|---|
| **solved_count** | **3 / 10** | **4 / 10** |
| run_id | `astropy10__ds-v4-flash-think__baseline__20260610-092805` | `astropy10__ds-v4-flash-think__fvk-v1__20260610-094051` |
| model | `deepseek-v4-flash-think__baseline` | `deepseek-v4-flash-think__fvk-v1` |
| FVK prompt | — | `v1` (sha256 `540c2ababb8c…`) |

**solved_count_baseline = 3** · **solved_count_fvk = 4** · Δ = +1

## Per-instance pairs

| instance_id | baseline resolved | fvk-v1 resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ❌ no | ❌ no | = |
| astropy__astropy-13236 | ❌ no | ❌ no | = |
| astropy__astropy-13398 | ❌ no | ❌ no | = |
| astropy__astropy-13453 | ❌ no | ❌ no | = |
| astropy__astropy-13579 | ❌ no | ✅ yes | 📈 fvk-only |
| astropy__astropy-13977 | ❌ no | ❌ no | = |
| astropy__astropy-14096 | ✅ yes | ✅ yes | = |
| astropy__astropy-14182 | ❌ no | ❌ no | = |
| astropy__astropy-14309 | ✅ yes | ✅ yes | = |

- Solved by both: 3 · by neither: 6
- Solved **only with FVK**: 1 ['astropy__astropy-13579']
- Solved **only by baseline**: 0 

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__ds-v4-flash-think__baseline__20260610-092805/report.md`
- fvk-v1: `fvk_experiments/runs/astropy10__ds-v4-flash-think__fvk-v1__20260610-094051/report.md`
