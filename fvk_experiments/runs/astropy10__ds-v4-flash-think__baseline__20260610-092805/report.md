# Run report — `astropy10__ds-v4-flash-think__baseline__20260610-092805`

Generated: 2026-06-10 10:06 UTC

- **Arm / variant**: `baseline`
- **Model**: `deepseek-v4-flash` (thinking=on), label `deepseek-v4-flash-think__baseline`
- **FVK prompt**: none (baseline arm)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **3 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 5197 | 2372 | 32.2 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 3512 | 1814 | 22.7 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 44243 | 952 | 14.8 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 9117 | 2019 | 24.8 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 8737 | 2638 | 36.1 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ❌ no | 1 | 6706 | 8113 | 107.6 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 26157 | 1195 | 16.3 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 26935 | 7294 | 98.9 |  |
| astropy__astropy-14182 | ✅ yes | — | ❌ no | 1 | 3064 | 3464 | 45.3 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 8193 | 1052 | 13.5 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-flash-think__baseline__20260610-092805/`
