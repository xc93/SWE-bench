# Pair comparison — baseline vs jointembed-v6

Generated: 2026-06-11 05:06 UTC

| | baseline | jointembed-v6 |
|---|---|---|
| **solved_count** | **8 / 10** | **9 / 10** |
| run_id | `astropy10__codex-5.5-xhigh__baseline__20260611-042659` | `astropy10__codex-5.5-xhigh__jointembed-v6__20260611-044734` |
| model | `codex-5.5-xhigh__baseline` | `codex-5.5-xhigh__jointembed-v6` |
| treatment prompt | — | `v6` (sha256 `ad1565f39207…`) + demos `prompts/demos/astropy10_demos_v1.yaml` |

**solved_count_baseline = 8** · **solved_count_treatment = 9** · Δ = +1

## Per-instance pairs

| instance_id | baseline resolved | jointembed-v6 resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ❌ no | ✅ yes | 📈 treatment-only |
| astropy__astropy-13236 | ✅ yes | ✅ yes | = |
| astropy__astropy-13398 | ✅ yes | ✅ yes | = |
| astropy__astropy-13453 | ✅ yes | ✅ yes | = |
| astropy__astropy-13579 | ✅ yes | ✅ yes | = |
| astropy__astropy-13977 | ❌ no | ❌ no | = |
| astropy__astropy-14096 | ✅ yes | ✅ yes | = |
| astropy__astropy-14182 | ✅ yes | ✅ yes | = |
| astropy__astropy-14309 | ✅ yes | ✅ yes | = |

- Solved by both: 8 · by neither: 1
- Solved **only by jointembed-v6**: 1 ['astropy__astropy-13033']
- Solved **only by baseline**: 0 

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__baseline__20260611-042659/report.md`
- jointembed-v6: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__jointembed-v6__20260611-044734/report.md`
