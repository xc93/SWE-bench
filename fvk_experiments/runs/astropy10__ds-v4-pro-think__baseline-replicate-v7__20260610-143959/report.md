# Run report — `astropy10__ds-v4-pro-think__baseline-replicate-v7__20260610-143959`

Generated: 2026-06-10 14:49 UTC

- **Arm / variant**: `baseline-replicate-v7`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__baseline-replicate-v7`
- **FVK prompt**: none (baseline arm)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **2 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 5197 | 2413 | 48.0 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 3512 | 2150 | 45.0 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 44243 | 3612 | 70.0 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 9117 | 3100 | 48.7 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 8737 | 5610 | 103.4 |  |
| astropy__astropy-13579 | ✅ yes | — | ❌ no | 1 | 6706 | 15791 | 286.9 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 26157 | 3702 | 67.0 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ❌ no | 1 | 26935 | 10845 | 225.3 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 3064 | 5467 | 114.7 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 8193 | 1456 | 28.3 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__baseline-replicate-v7__20260610-143959/`
