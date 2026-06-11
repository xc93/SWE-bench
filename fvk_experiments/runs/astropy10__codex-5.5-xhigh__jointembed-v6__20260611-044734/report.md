# Run report — `astropy10__codex-5.5-xhigh__jointembed-v6__20260611-044734`

Generated: 2026-06-11 05:06 UTC

- **Arm**: `jointembed-v6`
- **Model**: `codex-5.5` (thinking=off), label `codex-5.5-xhigh__jointembed-v6`
- **System prompt**: `prompts/fvk/v6.md` (version **v6**, sha256 `ad1565f39207…`)
- **Demos**: `prompts/demos/astropy10_demos_v1.yaml` (registry sha `d65fc4b58c48…`, content sha `273f7ad0d6fa…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (10 pinned instances)

## Result: **9 / 10 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 166463 | 2274 | 57.3 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ✅ yes | 1 | 183536 | 8203 | 183.0 |  |
| astropy__astropy-13236 | ✅ yes | ✅ yes | ✅ yes | 1 | 372207 | 4826 | 114.2 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ✅ yes | 1 | 209124 | 11655 | 559.4 |  |
| astropy__astropy-13453 | ✅ yes | ✅ yes | ✅ yes | 1 | 221721 | 7924 | 175.5 |  |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 118557 | 8514 | 166.3 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ❌ no | 1 | 269640 | 5668 | 117.7 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 433059 | 6608 | 139.9 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ✅ yes | 1 | 127968 | 8741 | 176.3 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 35426 | 659 | 18.5 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13033`, `astropy__astropy-13236`, `astropy__astropy-13398`, `astropy__astropy-13453`, `astropy__astropy-13579`, `astropy__astropy-14096`, `astropy__astropy-14182`, `astropy__astropy-14309`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/astropy10__codex-5.5-xhigh__jointembed-v6__20260611-044734/`
