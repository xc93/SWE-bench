# Run report — `astropy10__ds-v4-pro-think__fvk-v4__20260610-125349`

Generated: 2026-06-10 13:08 UTC

- **Arm / variant**: `fvk-v4`
- **Model**: `deepseek-v4-pro` (thinking=on), label `deepseek-v4-pro-think__fvk-v4`
- **FVK prompt**: `prompts/fvk/v4.md` (version **v4**, sha256 `e9d27c533914…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **4 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 6769 | 7501 | 146.9 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 5084 | 6121 | 127.0 |  |
| astropy__astropy-13236 | ✅ yes | — | ❌ no | 1 | 45815 | 3745 | 77.8 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 10689 | 10639 | 206.3 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ❌ no | 1 | 10309 | 6097 | 122.1 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 8278 | 14370 | 491.6 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 27729 | 5675 | 121.6 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 28507 | 7215 | 157.4 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ❌ no | 1 | 4636 | 6892 | 140.7 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 9765 | 5543 | 108.3 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__ds-v4-pro-think__fvk-v4__20260610-125349/`
