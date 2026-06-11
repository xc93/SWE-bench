# Run report — `astropy10__codex-5.5-xhigh__baseline__20260611-042659`

Generated: 2026-06-11 04:47 UTC

- **Arm**: `baseline`
- **Model**: `codex-5.5` (thinking=off), label `codex-5.5-xhigh__baseline`
- **System prompt**: none
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **8 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 112596 | 1927 | 50.0 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ❌ no | 1 | 79570 | 4994 | 102.2 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ✅ yes | 1 | 283363 | 5277 | 181.0 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ✅ yes | 1 | 658786 | 15682 | 360.6 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ✅ yes | 1 | 186206 | 6405 | 189.0 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 231474 | 13147 | 283.1 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 255770 | 10125 | 214.0 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 441002 | 9038 | 213.7 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ✅ yes | 1 | 142586 | 7682 | 162.7 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 147926 | 5789 | 133.1 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13236`, `astropy__astropy-13398`, `astropy__astropy-13453`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14182`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__codex-5.5-xhigh__baseline__20260611-042659/`
