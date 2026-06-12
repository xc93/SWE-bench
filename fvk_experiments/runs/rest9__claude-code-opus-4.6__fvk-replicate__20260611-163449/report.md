# Run report — `rest9__claude-code-opus-4.6__fvk-replicate__20260611-163449`

Generated: 2026-06-11 18:30 UTC

- **Arm**: `fvk-replicate`
- **Model**: `claude-code-opus-4.6` (thinking=off), label `claude-code-opus-4.6__fvk-replicate`
- **System prompt**: `prompts/agentic/fvk-replicate.md` (version **v1**, sha256 `b76db2120bf9…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (9 pinned instances)

## Result: **7 / 9 solved**

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | ✅ yes | 1 | 23 | 12650 | 360.3 |  |
| astropy__astropy-13033 | ✅ yes | ✅ yes | ✅ yes | 1 | 48 | 45766 | 1109.0 |  |
| astropy__astropy-13398 | ❌ no | — | ❌ no | 1 | 6 | 2299 | 439.3 | session cli_error: rc=1 |
| astropy__astropy-13453 | ❌ no | — | ❌ no | 1 | — | — | 336.1 | session cli_error: rc=1 |
| astropy__astropy-13579 | ✅ yes | ✅ yes | ✅ yes | 1 | 24 | 23382 | 778.1 |  |
| astropy__astropy-13977 | ✅ yes | ✅ yes | ✅ yes | 1 | 87 | 94057 | 2000.3 |  |
| astropy__astropy-14096 | ✅ yes | ✅ yes | ✅ yes | 1 | 26 | 23970 | 593.2 |  |
| astropy__astropy-14182 | ✅ yes | ✅ yes | ✅ yes | 1 | 31 | 23890 | 619.4 |  |
| astropy__astropy-14309 | ✅ yes | ✅ yes | ✅ yes | 1 | 33 | 14251 | 407.0 |  |

Resolved: `astropy__astropy-12907`, `astropy__astropy-13033`, `astropy__astropy-13579`, `astropy__astropy-13977`, `astropy__astropy-14096`, `astropy__astropy-14182`, `astropy__astropy-14309`

## Agentic phases: v1 → v2 (official harness verdicts)

v1 = the pre-self-review patch (`predictions_v1.jsonl`, harness run `rest9__claude-code-opus-4.6__fvk-replicate__20260611-163449-v1`); v2 = the final submission. "claimed" is what the session's own report asserted (parsed from `artifacts/<iid>/reports/`).

**v1 solved 4 / 9** → **v2 solved 7 / 9**

| instance_id | v1 resolved (official) | v2 resolved (official) | v1→v2 | claimed (in-session) | claimed = official |
|---|---|---|---|---|---|
| astropy__astropy-12907 | ✅ yes | ✅ yes | R→R | F2P 2/2 · P2P 13/13 · resolved True | ✅ match |
| astropy__astropy-13033 | ❌ no | ✅ yes | X→R 📈 | F2P 1/1 · P2P 19/20 · resolved False | ❌ MISMATCH |
| astropy__astropy-13398 | ❌ no | ❌ no | X→X | — | — |
| astropy__astropy-13453 | ❌ no | ❌ no | X→X | — | — |
| astropy__astropy-13579 | ✅ yes | ✅ yes | R→R | F2P 1/1 · P2P 40/40 · resolved True | ✅ match |
| astropy__astropy-13977 | ❌ no | ✅ yes | X→R 📈 | F2P 20/20 · P2P 322/322 · resolved True | ✅ match |
| astropy__astropy-14096 | ✅ yes | ✅ yes | R→R | F2P 1/1 · P2P 426/426 · resolved True | ✅ match |
| astropy__astropy-14182 | ❌ no | ✅ yes | X→R 📈 | F2P 1/1 · P2P 9/9 · resolved True | ✅ match |
| astropy__astropy-14309 | ✅ yes | ✅ yes | R→R | F2P 1/1 · P2P 141/141 · resolved True | ✅ match |

Transitions: R→R 4 · R→X 0 · X→R 3 · X→X 2

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/rest9__claude-code-opus-4.6__fvk-replicate__20260611-163449/`
