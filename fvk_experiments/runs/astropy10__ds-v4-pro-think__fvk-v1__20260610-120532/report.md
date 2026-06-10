# Run report — `astropy10__ds-v4-pro-think__fvk-v1__20260610-120532`

Generated: 2026-06-10 12:14 UTC

- **Arm / variant**: `fvk-v1`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__fvk-v1`
- **FVK prompt**: `prompts/fvk/v1.md` (version **v1**, sha256 `540c2ababb8c…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **4 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 6696 | 6375 | 124.8 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 5011 | 3170 | 60.8 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ❌ no | 1 | 45742 | 3319 | 62.6 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 10616 | 5341 | 99.1 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 10236 | 4711 | 84.1 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 8205 | 7590 | 144.7 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 27656 | 4558 | 82.6 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 28434 | 9070 | 166.6 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 4563 | 2245 | 40.9 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 9692 | 1764 | 29.3 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__fvk-v1__20260610-120532/`
