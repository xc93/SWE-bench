# Run report — `astropy10__ds-v4-flash-think__fvk-v3__20260610-113837`

Generated: 2026-06-10 11:45 UTC

- **Arm / variant**: `fvk-v3`
- **Model**: `deepseek-v4-flash` (thinking=on), label `deepseek-v4-flash-think__fvk-v3`
- **FVK prompt**: `prompts/fvk/v3.md` (version **v3**, sha256 `8e64c5149c8c…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **3 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 241350 | 2957 | 46.2 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 239665 | 2904 | 45.1 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 280396 | 1323 | 21.0 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 245270 | 1622 | 21.8 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 244890 | 7250 | 89.4 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 242859 | 14947 | 191.1 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 262310 | 4299 | 53.5 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ❌ no | 1 | 263088 | 6400 | 77.5 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 239217 | 1905 | 23.3 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 244346 | 1927 | 23.8 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-flash-think__fvk-v3__20260610-113837/`
