# Run report — `astropy10__ds-v4-pro-think__baseline__20260610-115611`

Generated: 2026-06-10 12:05 UTC

- **Arm / variant**: `baseline`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__baseline`
- **FVK prompt**: none (baseline arm)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **2 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 5197 | 3800 | 68.9 |  |
| astropy__astropy-13033 | ✅ yes | — | ❌ no | 1 | 3512 | 5465 | 98.3 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 44243 | 2902 | 59.9 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 9117 | 6256 | 120.3 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 8737 | 5203 | 103.3 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 6706 | 6631 | 136.9 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 26157 | 2984 | 59.4 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ❌ no | 1 | 26935 | 10604 | 225.9 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 3064 | 10208 | 219.1 |  |
| astropy__astropy-14309 | ✅ yes | — | ❌ no | 1 | 8193 | 1714 | 34.9 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__baseline__20260610-115611/`
