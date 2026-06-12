# Pair comparison — baseline vs fvk-replicate

Generated: 2026-06-12 11:36 UTC

| | baseline | fvk-replicate |
|---|---|---|
| **solved_count** | **2 / 9** | **5 / 9** |
| run_id | `batch3__claude-code-opus-4.6__baseline__20260612-031221` | `batch3__claude-code-opus-4.6__fvk-replicate__20260612-061923` |
| model | `claude-code-opus-4.6__baseline` | `claude-code-opus-4.6__fvk-replicate` |
| treatment prompt | — | `v2` (sha256 `d225f92797d9…`) |

**solved_count_baseline = 2** · **solved_count_treatment = 5** · Δ = +3

## Per-instance pairs

| instance_id | baseline resolved | fvk-replicate resolved | flip |
|---|---|---|---|
| astropy__astropy-14369 | ❌ no | ❌ no | = |
| django__django-15503 | ✅ yes | ✅ yes | = |
| django__django-15629 | ❌ no | ✅ yes | 📈 treatment-only |
| django__django-15957 | ✅ yes | ✅ yes | = |
| django__django-16263 | ❌ no | ❌ no | = |
| django__django-16560 | ❌ no | ✅ yes | 📈 treatment-only |
| django__django-16631 | ❌ no | ✅ yes | 📈 treatment-only |
| pylint-dev__pylint-4551 | ❌ no | ❌ no | = |
| pylint-dev__pylint-8898 | ❌ no | ❌ no | = |

- Solved by both: 2 · by neither: 4
- Solved **only by fvk-replicate**: 3 ['django__django-15629', 'django__django-16560', 'django__django-16631']
- Solved **only by baseline**: 0 

With n=9 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/batch3__claude-code-opus-4.6__baseline__20260612-031221/report.md`
- fvk-replicate: `fvk_experiments/runs/batch3__claude-code-opus-4.6__fvk-replicate__20260612-061923/report.md`
