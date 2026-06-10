# Run report — `astropy10__ds-v4-pro-think__jointembed-v6__20260610-141549`

Generated: 2026-06-10 14:27 UTC

- **Arm / variant**: `jointembed-v6`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__jointembed-v6`
- **FVK prompt**: `prompts/fvk/v6.md` (version **v6**, sha256 `ad1565f39207…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **4 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 10609 | 3975 | 77.4 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 9344 | 3049 | 48.4 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 49446 | 3244 | 70.4 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 17878 | 5508 | 93.5 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 14889 | 4552 | 85.8 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 17989 | 16955 | 375.6 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 30787 | 2638 | 56.4 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 30382 | 13225 | 286.1 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 7626 | 4719 | 94.7 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 13861 | 1399 | 29.7 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__jointembed-v6__20260610-141549/`
