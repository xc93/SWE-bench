# FVK Pair-Comparison Experiment — Design

Date: 2026-06-10 · Author: Claude (autonomous session for X.C.)

## Goal

Measure whether injecting a distilled **FVK** (formal-verification-kit) methodology prompt
changes DeepSeek's solve rate on SWE-bench, via a paired A/B comparison:

- **Arm A (baseline)**: DeepSeek, oracle prompt only → `solved_count_baseline`
- **Arm B (fvk)**: identical, plus the FVK prompt injected as a system message → `solved_count_fvk`

Subjects: the **first 10 astropy instances** of `princeton-nlp/SWE-bench_Verified` (test split).

## Decisions and evidence (autonomous brainstorm)

These were resolved from repo/environment evidence rather than interactive Q&A; flag anything
you'd like changed and rerun is one command.

| # | Decision | Choice | Why |
|---|----------|--------|-----|
| 1 | "DS" model | `deepseek-v4-flash`, thinking enabled | API exposes exactly `deepseek-v4-flash` + `deepseek-v4-pro` (V4 = most recent generation). Prior smoke tests in `outputs/*.jsonl` used v4-flash. Thinking is now a request param: `{"thinking": {"type": "enabled"}}`. Switching to pro = one line in config. |
| 2 | Harness setting | **Oracle retrieval, one-shot** (issue + gold-file contents → model emits a patch in a single call) | Matches the prior "full-oracle" experiments (deleted `deepseek-fvk-full-oracle-prompt.txt`, `outputs/deepseek-fvk-full-oracle-one.jsonl`, cached `princeton-nlp/SWE-bench_oracle` dataset). Not an agentic harness. |
| 3 | Prompt source | `text` column of `princeton-nlp/SWE-bench_oracle`, joined by instance_id | Battle-tested official oracle prompt (instructions + issue + full files + patch-format example). Identical user message in both arms. |
| 4 | FVK injection point | System message (baseline has **no** system message) | Cleanest single-variable manipulation; doesn't perturb the user prompt. |
| 5 | "First 10 astropy" | First 10 rows with `instance_id` starting `astropy__` in HF row order of the Verified test split, **pinned explicitly in configs** | Deterministic + reproducible even if the hub reorders rows. |
| 6 | "Solved" | `resolved == true` in the SWE-bench evaluation harness report (FAIL_TO_PASS and PASS_TO_PASS all pass) | Standard metric; harness validated locally today via a gold-patch smoke run. |
| 7 | Sampling params | API defaults; `max_tokens` 65536; temperature unset; thinking explicitly enabled in BOTH arms | Both arms get identical model config — the only difference is the FVK system message. |
| 8 | Retries | Up to 3 retries on API errors; 1 re-sample if the response has no parsable diff. Recorded per instance. | Keeps transient failures from contaminating the comparison; identical policy in both arms. |
| 9 | Env sanity | A `gold` patch evaluation of the same 10 instances runs first | Separates "model failed" from "environment/test is broken", and pre-pulls docker images. Result 2026-06-10: **10/10 resolved**. |
| 10 | Patch normalization | Extracted diffs get **mechanical hunk-header repair** (recount `@@ -A,B +C,D @@` from the body; restore lost leading spaces on blank context lines) before evaluation — identically in both arms | First eval pass showed most DeepSeek diffs carry wrong hunk counts (fatal for `git apply`/GNU `patch`). The repair never alters patch *content*, so "does the fix work" stays the measured variable instead of diff bookkeeping. Predictions were re-derived from the same saved responses (no re-sampling). Original unnormalized predictions kept as `predictions.pre-normalize.jsonl`. |
| 11 | Eval robustness | `cache_level: instance` (keep pulled images) + automatic harness re-runs for infra-errored instances; "Patch Apply Failed" is classified deterministic and never retried | Docker Hub pulls are flaky on this network (`registry-1.docker.io … EOF`); first pass silently left 5/10 baseline instances untested. Infra errors must be distinguishable from model failures or the counts are meaningless. |

## Architecture

```
fvk_experiments/
├── DESIGN.md / README.md / RESULTS.md   # RESULTS.md is auto-generated (run.py results)
├── configs/                  # one YAML per (subject × model × arm) — the rerun knobs
│   ├── astropy10__v4-flash__baseline.yaml
│   ├── astropy10__v4-pro__fvk-v1.yaml … etc.
├── prompts/fvk/              # versioned, frozen prompts (v1..v6) + CHANGELOG.md
│   └── vN.md                 # YAML frontmatter: version, date, source commit, optional tag
├── prompts/demos/            # per-instance demonstration registries (revisable YAML)
│   └── *.yaml + *.content.json   # picks+rationales; frozen verbatim content (build-demos)
├── scripts/
│   └── build_v3_verbatim.py  # regenerates v3.md (entire kit verbatim) from the submodule
├── vendor/formal-verification-kit/   # git submodule pinned at the distillation commit
├── fvk_bench/                # small python package (uses repo .venv)
│   ├── config.py             # YAML → dataclasses, validation, labels
│   ├── data.py               # instance pinning + oracle-text join
│   ├── demos.py              # per-instance demos: registry validation, content freeze, injection
│   ├── extract.py            # pure diff extraction + hunk-count normalization (unit-tested)
│   ├── inference.py          # DeepSeek calls (threaded, resumable, full raw provenance)
│   ├── evaluate.py           # subprocess → swebench.harness.run_evaluation (+infra retries)
│   └── report.py             # per-run report.md + summary.json + pair comparison + RESULTS.md
├── run.py                    # CLI: run / pin-instances / gold-sanity / compare / results
├── tests/                    # unit tests for the pure parts
├── runs/<run_id>/            # one dir per run: config snapshot, prompts sent, raw
│   │                         # responses (incl. reasoning), predictions.jsonl,
│   │                         # eval/<harness report>, report.md, summary.json
└── reports/                  # pair-comparison reports
```

`run_id = <run_name from config>__<UTC timestamp>`, e.g.
`astropy10__ds-v4-flash-think__fvk-v1__20260610-103000`. The harness `--run_id` is the same
string, so docker logs under `logs/run_evaluation/<run_id>/` line up with `runs/<run_id>/`.

`model_name_or_path` in predictions: `deepseek-v4-flash-think__baseline` / `…__fvk-v1` —
the FVK prompt version is part of the label, and its sha256 is recorded in `meta.json`
and the report.

## Error handling

- API error after retries → instance recorded with `error`, empty patch (counts unsolved), run continues.
- No parsable diff after re-sample → empty patch, flagged `patch=no` in report.
- Missing oracle text or instance-id mismatch → hard fail before any API call.
- Eval is idempotent per harness semantics; inference resumes by skipping instances whose
  `raw/<iid>.json` already contains a non-empty patch (`--no-resume` to force).

## Testing

- Unit tests for `extract.py` (fence/`<patch>`-tag/raw-tail formats seen in prior DeepSeek outputs) and config validation.
- Gold-patch sanity eval for environment validation.
- The pair report cross-checks `solved_count` against `resolved_ids` from the harness JSON (no hand counting).

## Non-goals (YAGNI)

Agentic scaffolds, BM25 retrieval mode, multi-seed sampling, statistical tests beyond paired
flip counts (n=10), support for non-DeepSeek providers (the config leaves room, code doesn't branch).
