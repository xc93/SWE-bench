# Run report — `astropy10__ds-v4-flash-think__fvk-v2__20260610-111221`

Generated: 2026-06-10 11:18 UTC

- **Arm / variant**: `fvk-v2`
- **Model**: `deepseek-v4-flash` (thinking=on), label `deepseek-v4-flash-think__fvk-v2`
- **FVK prompt**: `prompts/fvk/v2.md` (version **v2**, sha256 `8c8f31b1e7b2…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **3 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 14881 | 2313 | 32.5 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 13196 | 3581 | 42.7 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 53927 | 986 | 16.1 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 18801 | 2246 | 28.6 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 18421 | 3891 | 44.8 |  |
| astropy__astropy-13579 | ✅ yes | — | ❌ no | 1 | 16390 | 9780 | 123.2 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 35841 | 4270 | 55.4 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 36619 | 12811 | 155.7 |  |
| astropy__astropy-14182 | ✅ yes | — | ❌ no | 1 | 12748 | 5477 | 73.6 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 17877 | 2017 | 24.6 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-flash-think__fvk-v2__20260610-111221/`
