# Run report — `rest9__claude-code-opus-4.6__baseline__20260611-122549`

Generated: 2026-06-11 13:48 UTC

- **Arm**: `baseline`
- **Model**: `claude-code-opus-4.6` (thinking=off), label `claude-code-opus-4.6__baseline`
- **System prompt**: `prompts/agentic/baseline.md` (version **v1**, sha256 `0720aa20c937…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (9 pinned instances)

## Result: **7 / 9 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 11 | 4983 | 184.1 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ✅ yes | 1 | 20 | 10007 | 310.7 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 75 | 54401 | 1539.2 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ✅ yes | 1 | 14 | 7015 | 238.2 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 20 | 17357 | 471.2 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 46 | 32527 | 988.9 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 18 | 13597 | 391.4 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ✅ yes | 1 | 18 | 9909 | 430.2 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 12 | 4360 | 180.3 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13033`, `astropy__astropy-13453`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14182`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/rest9__claude-code-opus-4.6__baseline__20260611-122549/`
