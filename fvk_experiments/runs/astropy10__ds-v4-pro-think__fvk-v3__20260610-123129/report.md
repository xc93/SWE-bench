# Run report — `astropy10__ds-v4-pro-think__fvk-v3__20260610-123129`

Generated: 2026-06-10 12:39 UTC

- **Arm / variant**: `fvk-v3`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__fvk-v3`
- **FVK prompt**: `prompts/fvk/v3.md` (version **v3**, sha256 `8e64c5149c8c…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **2 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | — | ❌ no | 1 | 241350 | 3207 | 73.0 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 239665 | 3975 | 115.6 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 280396 | 2514 | 59.6 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 245270 | 3368 | 90.6 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 244890 | 2486 | 60.9 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 242859 | 7022 | 144.0 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 262310 | 1368 | 33.9 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ❌ no | 1 | 263088 | 5454 | 114.0 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 239217 | 1717 | 44.8 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 244346 | 1538 | 34.9 |  |

Resolved: `astropy__astropy-13579`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__fvk-v3__20260610-123129/`
