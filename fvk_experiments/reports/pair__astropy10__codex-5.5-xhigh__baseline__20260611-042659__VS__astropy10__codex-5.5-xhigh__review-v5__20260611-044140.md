# Pair comparison — baseline vs review-v5

Generated: 2026-06-11 05:06 UTC

| | baseline | review-v5 |
|---|---|---|
| **solved_count** | **8 / 10** | **5 / 10** |
| run_id | `astropy10__codex-5.5-xhigh__baseline__20260611-042659` | `astropy10__codex-5.5-xhigh__review-v5__20260611-044140` |
| model | `codex-5.5-xhigh__baseline` | `codex-5.5-xhigh__review-v5` |
| treatment prompt | — | `v5` (sha256 `09becca148f3…`) |

**solved_count_baseline = 8** · **solved_count_treatment = 5** · Δ = -3

## Per-instance pairs

| instance_id | baseline resolved | review-v5 resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ❌ no | ❌ no | = |
| astropy__astropy-13236 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-13398 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-13453 | ✅ yes | ✅ yes | = |
| astropy__astropy-13579 | ✅ yes | ✅ yes | = |
| astropy__astropy-13977 | ❌ no | ❌ no | = |
| astropy__astropy-14096 | ✅ yes | ✅ yes | = |
| astropy__astropy-14182 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-14309 | ✅ yes | ✅ yes | = |

- Solved by both: 5 · by neither: 2
- Solved **only by review-v5**: 0 
- Solved **only by baseline**: 3 ['astropy__astropy-13236', 'astropy__astropy-13398', 'astropy__astropy-14182']

With n=10 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__baseline__20260611-042659/report.md`
- review-v5: `fvk_experiments/runs/astropy10__codex-5.5-xhigh__review-v5__20260611-044140/report.md`
