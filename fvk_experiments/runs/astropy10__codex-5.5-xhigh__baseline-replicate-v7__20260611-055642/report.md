# Run report — `astropy10__codex-5.5-xhigh__baseline-replicate-v7__20260611-055642`

Generated: 2026-06-11 06:18 UTC

- **Arm**: `baseline-replicate-v7`
- **Model**: `codex-5.5` (thinking=off), label `codex-5.5-xhigh__baseline-replicate-v7`
- **System prompt**: none
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **8 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 114112 | 2713 | 63.6 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ✅ yes | 1 | 130151 | 6471 | 165.0 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ✅ yes | 1 | 292318 | 4878 | 119.6 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 354329 | 22139 | 451.9 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ✅ yes | 1 | 220278 | 7752 | 203.7 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ❌ no | 1 | 721317 | 10333 | 303.6 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ✅ yes | 1 | 447566 | 10186 | 252.3 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 427641 | 11613 | 255.0 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ✅ yes | 1 | 193009 | 9070 | 236.0 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 125517 | 3560 | 87.3 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13033`, `astropy__astropy-13236`, `astropy__astropy-13453`, `astropy__astropy-13977`, `astropy__astropy-14096`, `astropy__astropy-14182`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__codex-5.5-xhigh__baseline-replicate-v7__20260611-055642/`
