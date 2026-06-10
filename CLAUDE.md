# CLAUDE.md

Fork of SWE-bench (MIT, Princeton NLP) hosting **FVK pair-comparison experiments** in
`fvk_experiments/`: A/B tests of whether a distilled formal-verification-kit prompt
(https://github.com/grosu/formal-verification-kit) improves DeepSeek's SWE-bench solve
rate. Keep upstream `swebench/` unmodified — all experiment code lives in `fvk_experiments/`.

## Start here

- `fvk_experiments/RESULTS.md` — auto-generated summary of every run (the shareable file)
- `fvk_experiments/DESIGN.md` — experiment design decisions + evidence (read before changing methodology)
- `fvk_experiments/README.md` — rerun commands and config knobs
- Prompts are versioned: `fvk_experiments/prompts/fvk/vN.md` (frontmatter: version/date/source commit; sha256 recorded in every run's `meta.json`). New prompt ⇒ new `vN.md` + new config + CHANGELOG entry; never edit a frozen version.
- The kit itself is a submodule at `fvk_experiments/vendor/formal-verification-kit`, pinned to the commit prompts were distilled from (`git submodule update --init`). Distill new prompt versions from the submodule (read files via `git -C <submodule> show <ref>:<path>` for pinned reads).

## Environment

- `.venv/` is uv-managed (no pip binary): use `.venv/bin/python`; install via `uv pip install --python .venv/bin/python <pkg>`
- Inference needs `DEEPSEEK_API_KEY` env var; evaluation needs a running docker daemon
- DeepSeek V4 API: models `deepseek-v4-flash` / `deepseek-v4-pro`; thinking mode is a request param `{"thinking": {"type": "enabled"}}` (no more `deepseek-reasoner` alias)

## Commands

- Run an arm: `.venv/bin/python fvk_experiments/run.py run --config fvk_experiments/configs/<cfg>.yaml` (stages: `--stages infer,eval,report`; `--run-id <existing>` resumes)
- Pair report: `.venv/bin/python fvk_experiments/run.py compare --baseline fvk_experiments/runs/<a> --treatment fvk_experiments/runs/<b>`
- Env sanity: `.venv/bin/python fvk_experiments/run.py gold-sanity --config <cfg>` (gold patches must resolve 10/10 before trusting model evals)
- Regenerate results index: `.venv/bin/python fvk_experiments/run.py results`
- Unit tests: `.venv/bin/python -m pytest fvk_experiments/tests/ -q`

## Gotchas (this machine / network)

- HuggingFace Hub: transient `SSL: UNEXPECTED_EOF` — retry, or `HF_ENDPOINT=https://hf-mirror.com`
- Docker Hub pulls flake (EOF from registry-1.docker.io). The eval wrapper keeps images (`cache_level: instance`) and auto-reruns infra-errored instances; "Patch Apply Failed" is deterministic and never retried. Never read solved counts without checking `error_ids` — infra errors masquerade as model failures.
- The harness writes its report JSON to CWD (ignores `--report_dir`); `fvk_bench/evaluate.py` relocates the fresh copy. Ground truth = `runs/<id>/eval/*.json` + `logs/run_evaluation/<run_id>/**/report.json`.
- DeepSeek diffs routinely carry wrong `@@` hunk counts; `fvk_bench/extract.py` mechanically normalizes them (content untouched, both arms identically). Unnormalized originals: `runs/<id>/predictions.pre-normalize.jsonl`.
- `logs/` is gitignored (harness execution logs); `fvk_experiments/runs/` is committed for provenance (raw responses incl. reasoning, exact prompts, eval reports).
