# Pair comparison — baseline vs review-control

Generated: 2026-06-12 00:46 UTC

| | baseline | review-control |
|---|---|---|
| **solved_count** | **7 / 9** | **7 / 9** |
| run_id | `rest9__claude-code-opus-4.6__baseline__20260611-122549` | `rest9__claude-code-opus-4.6__review-control__20260611-134910` |
| model | `claude-code-opus-4.6__baseline` | `claude-code-opus-4.6__review-control` |
| treatment prompt | — | `v1` (sha256 `5a53d6728d17…`) |

**solved_count_baseline = 7** · **solved_count_treatment = 7** · Δ = +0

## Per-instance pairs

| instance_id | baseline resolved | review-control resolved | flip |
|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | = |
| astropy__astropy-13033 | ✅ yes | ✅ yes | = |
| astropy__astropy-13398 | ❌ no | ❌ no | = |
| astropy__astropy-13453 | ✅ yes | ❌ no | 📉 baseline-only |
| astropy__astropy-13579 | ✅ yes | ✅ yes | = |
| astropy__astropy-13977 | ❌ no | ✅ yes | 📈 treatment-only |
| astropy__astropy-14096 | ✅ yes | ✅ yes | = |
| astropy__astropy-14182 | ✅ yes | ✅ yes | = |
| astropy__astropy-14309 | ✅ yes | ✅ yes | = |

- Solved by both: 6 · by neither: 1
- Solved **only by review-control**: 1 ['astropy__astropy-13977']
- Solved **only by baseline**: 1 ['astropy__astropy-13453']

With n=9 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/rest9__claude-code-opus-4.6__baseline__20260611-122549/report.md`
- review-control: `fvk_experiments/runs/rest9__claude-code-opus-4.6__review-control__20260611-134910/report.md`
