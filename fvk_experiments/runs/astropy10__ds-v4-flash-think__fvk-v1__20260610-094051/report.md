# Run report — `astropy10__ds-v4-flash-think__fvk-v1__20260610-094051`

Generated: 2026-06-10 10:07 UTC

- **Arm / variant**: `fvk-v1`
- **Model**: `deepseek-v4-flash` (thinking=on), label `deepseek-v4-flash-think__fvk-v1`
- **FVK prompt**: `prompts/fvk/v1.md` (version **v1**, sha256 `540c2ababb8c…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **4 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 6696 | 2986 | 36.8 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 5011 | 5157 | 58.6 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 45742 | 1879 | 24.8 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 10616 | 3975 | 39.9 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 10236 | 3005 | 35.9 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 8205 | 5982 | 69.6 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 27656 | 6699 | 70.3 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 28434 | 5069 | 59.2 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 4563 | 5143 | 58.8 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 9692 | 2441 | 24.2 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-flash-think__fvk-v1__20260610-094051/`
