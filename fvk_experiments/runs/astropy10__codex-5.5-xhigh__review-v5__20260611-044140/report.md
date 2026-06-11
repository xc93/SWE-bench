# Run report — `astropy10__codex-5.5-xhigh__review-v5__20260611-044140`

Generated: 2026-06-11 04:50 UTC

- **Arm**: `review-v5`
- **Model**: `codex-5.5` (thinking=off), label `codex-5.5-xhigh__review-v5`
- **System prompt**: `prompts/fvk/v5.md` (version **v5**, sha256 `09becca148f3…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **5 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 28239 | 1169 | 29.4 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 26575 | 1778 | 38.8 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 66355 | 680 | 19.4 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 32012 | 1615 | 36.1 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ✅ yes | 1 | 31355 | 4312 | 83.5 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 29453 | 4947 | 94.8 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 48419 | 6978 | 134.9 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 49169 | 758 | 20.7 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 26192 | 5383 | 103.8 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 30976 | 659 | 19.0 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13453`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__codex-5.5-xhigh__review-v5__20260611-044140/`
