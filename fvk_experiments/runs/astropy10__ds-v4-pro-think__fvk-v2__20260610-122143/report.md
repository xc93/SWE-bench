# Run report — `astropy10__ds-v4-pro-think__fvk-v2__20260610-122143`

Generated: 2026-06-10 12:31 UTC

- **Arm / variant**: `fvk-v2`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__fvk-v2`
- **FVK prompt**: `prompts/fvk/v2.md` (version **v2**, sha256 `8c8f31b1e7b2…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **4 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 14881 | 2171 | 45.0 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 13196 | 2767 | 64.4 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 53927 | 2399 | 54.8 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 18801 | 3844 | 70.2 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 18421 | 2600 | 60.0 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 16390 | 12339 | 263.9 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 35841 | 10095 | 182.8 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 36619 | 7604 | 150.6 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 12748 | 5918 | 128.3 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 17877 | 1437 | 26.4 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__fvk-v2__20260610-122143/`
