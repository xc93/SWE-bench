# Run report — `pilot13236__claude-code-opus-4.6__fvk-replicate__20260611-120546`

Generated: 2026-06-11 12:17 UTC

- **Arm**: `fvk-replicate`
- **Model**: `claude-code-opus-4.6` (thinking=off), label `claude-code-opus-4.6__fvk-replicate`
- **System prompt**: `prompts/agentic/fvk-replicate.md` (version **v1**, sha256 `b76db2120bf9…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (1 pinned instances)

## Result: **1 / 1 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-13236 | ✅ yes | ✅ yes | ✅ yes | 1 | 41 | 14177 | 533.7 |  |

Resolved: `astropy__astropy-13236`

## Agentic phases: v1 → v2 (official harness verdicts)

v1 = the pre-self-review patch (`predictions_v1.jsonl`, harness run `pilot13236__claude-code-opus-4.6__fvk-replicate__20260611-120546-v1`); v2 = the final submission. "claimed" is what the session's own report asserted (parsed from `artifacts/<iid>/reports/`).

**v1 solved 1 / 1** → **v2 solved 1 / 1**

| instance_id | v1 resolved (official) | v2 resolved (official) | v1→v2 | claimed (in-session) | claimed = official |
|---|---|---|---|---|---|
| astropy__astropy-13236 | ✅ yes | ✅ yes | R→R | F2P 2/2 · P2P 644/644 · resolved True | ✅ match |

Transitions: R→R 1 · R→X 0 · X→R 0 · X→X 0

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/pilot13236__claude-code-opus-4.6__fvk-replicate__20260611-120546/`
