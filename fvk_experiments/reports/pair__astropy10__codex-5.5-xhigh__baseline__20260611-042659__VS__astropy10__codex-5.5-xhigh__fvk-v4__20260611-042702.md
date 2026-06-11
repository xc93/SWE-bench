# Pair comparison — baseline vs fvk-v4

Generated: 2026-06-11 05:06 UTC

| | baseline | fvk-v4 |
|---|---|---|
| **solved_count** | **8 / 10** | **7 / 10** |
| run_id | `astropy10__codex-5.5-xhigh__baseline__20260611-042659` | `astropy10__codex-5.5-xhigh__fvk-v4__20260611-042702` |
| model | `codex-5.5-xhigh__baseline` | `codex-5.5-xhigh__fvk-v4` |
| treatment prompt | — | `v4` (sha256 `e9d27c533914…`) |

**solved_count_baseline = 8** · **solved_count_treatment = 7** · Δ = -1

## Per-instance pairs

| instance_id | baseline resolved | fvk-v4 resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ❌ no | ❌ no | = |
| astropy__astropy-13236 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-13398 | ✅ yes | ✅ yes | = |
| astropy__astropy-13453 | ✅ yes | ✅ yes | = |
| astropy__astropy-13579 | ✅ yes | ✅ yes | = |
| astropy__astropy-13977 | ❌ no | ❌ no | = |
| astropy__astropy-14096 | ✅ yes | ✅ yes | = |
| astropy__astropy-14182 | ✅ yes | ✅ yes | = |
| astropy__astropy-14309 | ✅ yes | ✅ yes | = |

- Solved by both: 7 · by neither: 2
- Solved **only by fvk-v4**: 0 
- Solved **only by baseline**: 1 ['astropy__astropy-13236']

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__baseline__20260611-042659/report.md`
- fvk-v4: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__fvk-v4__20260611-042702/report.md`
