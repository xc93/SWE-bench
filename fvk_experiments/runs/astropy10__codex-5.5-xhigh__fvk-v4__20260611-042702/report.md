# Run report — `astropy10__codex-5.5-xhigh__fvk-v4__20260611-042702`

Generated: 2026-06-11 04:41 UTC

- **Arm**: `fvk-v4`
- **Model**: `codex-5.5` (thinking=off), label `codex-5.5-xhigh__fvk-v4`
- **System prompt**: `prompts/fvk/v4.md` (version **v4**, sha256 `e9d27c533914…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **7 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 29155 | 651 | 18.6 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 27491 | 694 | 19.4 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 67271 | 712 | 19.3 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ✅ yes | 1 | 234674 | 15695 | 618.1 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ✅ yes | 1 | 207958 | 5892 | 144.5 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 160988 | 5767 | 122.2 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 49335 | 660 | 19.4 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 50085 | 3861 | 75.5 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ✅ yes | 1 | 178233 | 4555 | 105.5 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 31892 | 480 | 17.1 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13398`, `astropy__astropy-13453`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14182`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__codex-5.5-xhigh__fvk-v4__20260611-042702/`
