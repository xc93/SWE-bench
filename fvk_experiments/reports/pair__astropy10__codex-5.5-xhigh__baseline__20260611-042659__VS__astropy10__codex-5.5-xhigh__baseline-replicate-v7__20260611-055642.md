# Pair comparison — baseline vs baseline-replicate-v7

Generated: 2026-06-11 06:19 UTC

| | baseline | baseline-replicate-v7 |
|---|---|---|
| **solved_count** | **8 / 10** | **8 / 10** |
| run_id | `astropy10__codex-5.5-xhigh__baseline__20260611-042659` | `astropy10__codex-5.5-xhigh__baseline-replicate-v7__20260611-055642` |
| model | `codex-5.5-xhigh__baseline` | `codex-5.5-xhigh__baseline-replicate-v7` |
| treatment prompt | — | — |

**solved_count_baseline = 8** · **solved_count_treatment = 8** · Δ = +0

## Per-instance pairs

| instance_id | baseline resolved | baseline-replicate-v7 resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ❌ no | ✅ yes | 📈 treatment-only |
| astropy__astropy-13236 | ✅ yes | ✅ yes | = |
| astropy__astropy-13398 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-13453 | ✅ yes | ✅ yes | = |
| astropy__astropy-13579 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-13977 | ❌ no | ✅ yes | 📈 treatment-only |
| astropy__astropy-14096 | ✅ yes | ✅ yes | = |
| astropy__astropy-14182 | ✅ yes | ✅ yes | = |
| astropy__astropy-14309 | ✅ yes | ✅ yes | = |

- Solved by both: 6 · by neither: 0
- Solved **only by baseline-replicate-v7**: 2 ['astropy__astropy-13033', 'astropy__astropy-13977']
- Solved **only by baseline**: 2 ['astropy__astropy-13398', 'astropy__astropy-13579']

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__baseline__20260611-042659/report.md`
- baseline-replicate-v7: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__baseline-replicate-v7__20260611-055642/report.md`
