# Run report — `rest9__claude-code-opus-4.6__review-control__20260611-134910`

Generated: 2026-06-11 16:34 UTC

- **Arm**: `review-control`
- **Model**: `claude-code-opus-4.6` (thinking=off), label `claude-code-opus-4.6__review-control`
- **System prompt**: `prompts/agentic/review-control.md` (version **v1**, sha256 `5a53d6728d17…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (9 pinned instances)

## Result: **7 / 9 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 35 | 17312 | 644.6 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ✅ yes | 1 | 53 | 30092 | 1011.3 |  |
| astropy__astropy-13398 | ✅ yes | ✅ yes | ❌ no | 1 | 138 | 152134 | 3610.6 |  |
| astropy__astropy-13453 | ❌ no | — | ❌ no | 1 | — | — | 296.0 | session cli_error: rc=1 |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 34 | 27670 | 654.6 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ✅ yes | 1 | 96 | 78039 | 1702.0 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 30 | 25897 | 681.3 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ✅ yes | 1 | 47 | 24260 | 671.7 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 22 | 9678 | 312.5 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13033`, `astropy__astropy-13579`, `astropy__astropy-13977`, `astropy__astropy-14096`, `astropy__astropy-14182`, `astropy__astropy-14309`

## Agentic phases: v1 → v2 (official harness verdicts)

v1 = the pre-self-review patch (`predictions_v1.jsonl`, harness run `rest9__claude-code-opus-4.6__review-control__20260611-134910-v1`); v2 = the final submission. "claimed" is what the session's own report asserted (parsed from `artifacts/<iid>/reports/`).

**v1 solved 5 / 9** → **v2 solved 7 / 9**

| instance_id | v1 resolved (official) | v2 resolved (official) | v1→v2 | claimed (in-session) | claimed = official |
|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | R→R | F2P 2/2 · P2P 13/13 · resolved True | ✅ match |
| astropy__astropy-13033 | ❌ no | ✅ yes | X→R 📈 | F2P 1/1 · P2P 19/20 · resolved False | ❌ MISMATCH |
| astropy__astropy-13398 | ❌ no | ❌ no | X→X | F2P 2/4 · P2P 61/68 · resolved False | ✅ match |
| astropy__astropy-13453 | ❌ no | ❌ no | X→X | — | — |
| astropy__astropy-13579 | ✅ yes | ✅ yes | R→R | F2P 1/1 · P2P 40/40 · resolved True | ✅ match |
| astropy__astropy-13977 | ❌ no | ✅ yes | X→R 📈 | F2P 20/20 · P2P 322/322 · resolved True | ✅ match |
| astropy__astropy-14096 | ✅ yes | ✅ yes | R→R | F2P 1/1 · P2P 426/426 · resolved True | ✅ match |
| astropy__astropy-14182 | ✅ yes | ✅ yes | R→R | F2P 1/1 · P2P 9/9 · resolved True | ✅ match |
| astropy__astropy-14309 | ✅ yes | ✅ yes | R→R | F2P 1/1 · P2P 141/141 · resolved True | ✅ match |

Transitions: R→R 5 · R→X 0 · X→R 2 · X→X 2

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/rest9__claude-code-opus-4.6__review-control__20260611-134910/`
