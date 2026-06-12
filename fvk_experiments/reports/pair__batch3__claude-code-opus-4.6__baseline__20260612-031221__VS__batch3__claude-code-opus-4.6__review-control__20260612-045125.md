# Pair comparison — baseline vs review-control

Generated: 2026-06-12 11:36 UTC

| | baseline | review-control |
|---|---|---|
| **solved_count** | **2 / 9** | **4 / 9** |
| run_id | `batch3__claude-code-opus-4.6__baseline__20260612-031221` | `batch3__claude-code-opus-4.6__review-control__20260612-045125` |
| model | `claude-code-opus-4.6__baseline` | `claude-code-opus-4.6__review-control` |
| treatment prompt | — | `v2` (sha256 `205fd82a9748…`) |

**solved_count_baseline = 2** · **solved_count_treatment = 4** · Δ = +2

## Per-instance pairs

| instance_id | baseline resolved | review-control resolved | flip |
|---|---|---|---|
| astropy__astropy-14369 | ❌ no | ❌ no | = |
| django__django-15503 | ✅ yes | ✅ yes | = |
| django__django-15629 | ❌ no | ✅ yes | 📈 treatment-only |
| django__django-15957 | ✅ yes | ✅ yes | = |
| django__django-16263 | ❌ no | ❌ no | = |
| django__django-16560 | ❌ no | ✅ yes | 📈 treatment-only |
| django__django-16631 | ❌ no | ❌ no | = |
| pylint-dev__pylint-4551 | ❌ no | ❌ no | = |
| pylint-dev__pylint-8898 | ❌ no | ❌ no | = |

- Solved by both: 2 · by neither: 5
- Solved **only by review-control**: 2 ['django__django-15629', 'django__django-16560']
- Solved **only by baseline**: 0 

With n=9 this is directional evidence, not statistical significance.

## Run reports

- baseline: `fvk_experiments/runs/batch3__claude-code-opus-4.6__baseline__20260612-031221/report.md`
- review-control: `fvk_experiments/runs/batch3__claude-code-opus-4.6__review-control__20260612-045125/report.md`
