# Run report — `astropy10__ds-v4-pro-think__review-v5__20260610-130805`

Generated: 2026-06-10 13:23 UTC

- **Arm / variant**: `review-v5`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__review-v5`
- **FVK prompt**: `prompts/fvk/v5.md` (version **v5**, sha256 `09becca148f3…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **3 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 5851 | 4727 | 94.8 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 4166 | 3801 | 82.1 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 44897 | 3403 | 67.8 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 9771 | 10128 | 202.3 |  |
| astropy__astropy-13453 | ✅ yes | — | ❌ no | 1 | 9391 | 9561 | 166.4 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 7360 | 34768 | 642.1 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 26811 | 12250 | 271.6 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 27589 | 8157 | 171.4 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 3718 | 4753 | 93.7 |  |
| astropy__astropy-14309 | ✅ yes | — | ❌ no | 1 | 8847 | 3169 | 59.2 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`, `astropy__astropy-14096`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__review-v5__20260610-130805/`
