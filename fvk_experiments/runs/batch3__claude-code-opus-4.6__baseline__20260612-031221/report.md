# Run report — `batch3__claude-code-opus-4.6__baseline__20260612-031221`

Generated: 2026-06-12 04:49 UTC

- **Arm**: `baseline`
- **Model**: `claude-code-opus-4.6` (thinking=off), label `claude-code-opus-4.6__baseline`
- **System prompt**: `prompts/agentic/baseline-v2.md` (version **v2**, sha256 `1aa4dad51826…`)
- **Dataset**: `princeton-nlp/SWE-bench_Verified` (9 pinned instances)

## Result: **2 / 9 solved**

> ⚠️ **1 INVALIDATED for contamination** — prediction emptied, scored unsolved. Evidence in `audit/<iid>.json`.
> - `pylint-dev__pylint-8898` — f2p name before eval: test_csv_regex_error; f2p name before eval: test_csv_regex_error

| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
| astropy__astropy-14369 | ✅ yes | ✅ yes | ❌ no | 1 | 18 | 36588 | 747.9 |  |
| django__django-15503 | ✅ yes | ✅ yes | ✅ yes | 1 | 40 | 31937 | 820.8 |  |
| django__django-15629 | ✅ yes | ✅ yes | ❌ no | 1 | 46 | 9911 | 425.8 |  |
| django__django-15957 | ✅ yes | ✅ yes | ✅ yes | 1 | 29 | 20185 | 628.9 |  |
| django__django-16263 | ✅ yes | ✅ yes | ❌ no | 1 | 113 | 36662 | 945.3 |  |
| django__django-16560 | ✅ yes | ✅ yes | ❌ no | 1 | 54 | 15924 | 356.9 |  |
| django__django-16631 | ✅ yes | ✅ yes | ❌ no | 1 | 39 | 10818 | 320.8 |  |
| pylint-dev__pylint-4551 | ✅ yes | ✅ yes | ❌ no | 1 | 59 | 53922 | 1221.6 |  |
| pylint-dev__pylint-8898 ⚠️ CONTAMINATED | ❌ no | — | ❌ no | 1 | 31 | 8901 | 255.8 | contaminated: f2p name before eval: test_csv_regex_error; f2p name before eval: test_csv_regex_error |

Resolved: `django__django-15503`, `django__django-15957`

## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/batch3__claude-code-opus-4.6__baseline__20260612-031221/`
