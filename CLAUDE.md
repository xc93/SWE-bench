# CLAUDE.md

Fork of SWE-bench (MIT, Princeton NLP) hosting **FVK pair-comparison experiments** in
`fvk_experiments/`: A/B tests of whether a distilled formal-verification-kit prompt
(https://github.com/grosu/formal-verification-kit) improves DeepSeek's SWE-bench solve
rate. Keep upstream `swebench/` unmodified — all experiment code lives in `fvk_experiments/`.

## Start here

- `fvk_experiments/RESULTS.md` — auto-generated summary of every run (the shareable file; ALL solved counts live there, nowhere else)
- `fvk_experiments/DESIGN.md` — experiment design decisions + evidence (read before changing methodology)
- `fvk_experiments/README.md` — rerun commands, config knobs, and the arm table
- `fvk_experiments/prompts/fvk/CHANGELOG.md` — what each prompt version is and why it exists
- **Experiment map (as of 2026-06-10)**: subject set `astropy10` (first 10 SWE-bench_Verified astropy instances, pinned in every config); models `deepseek-v4-flash` + `deepseek-v4-pro`; arms = baseline (no system prompt), fvk-v1 (1k-token digest, spec-first), fvk-v2 (10k distillation), fvk-v3 (entire kit verbatim — regenerate via `fvk_experiments/scripts/build_v3_verbatim.py`), fvk-v4 (draft → FVK-check → regenerate), review-v5 (no-FVK control for v4), jointembed-v6 (per-instance demonstrations). Numbers: RESULTS.md.
- Prompts are versioned and FROZEN once run: `fvk_experiments/prompts/fvk/vN.md` (frontmatter: version/date/source commit; optional `tag:` overrides the `fvk-vN` arm label — used by control arms like `review-v5`; sha256 recorded in every run's `meta.json`). New idea ⇒ new `vN.md` + new config + CHANGELOG entry; never edit a frozen version.
- **Per-instance prompts (since v6)**: the system message is composed per test instance = static `prompt.system_prompt` + optional `prompt.demos` (either alone, or both — FVK+demos is one config). `prompt.demos` points to a registry YAML (`fvk_experiments/prompts/demos/*.yaml`): 3 picks {id, rationale} per target, drawn from the benchmark OUTSIDE the evaluated set (validator-enforced; also exactly-3-distinct). Revise picks in the registry, then refreeze verbatim issue+patch content: `run.py build-demos --registry <yaml>` → sibling `.content.json`, sha-stamped against the registry so stale content hard-fails at inference. Exact composed messages archived per instance in `runs/<id>/prompts/<iid>.system.txt`; both shas in `meta.json`. Code: `fvk_bench/demos.py`.
- The kit itself is a submodule at `fvk_experiments/vendor/formal-verification-kit`, pinned to the commit prompts were distilled from (`git submodule update --init`). Distill new prompt versions from the submodule (read files via `git -C <submodule> show <ref>:<path>` for pinned reads).

## Environment

- `.venv/` is uv-managed (no pip binary): use `.venv/bin/python`; install via `uv pip install --python .venv/bin/python <pkg>`
- Inference needs `DEEPSEEK_API_KEY` env var; evaluation needs a running docker daemon
- Configs are one per (subject × model × arm): `configs/<subject>__<model-short>__<arm>.yaml` (e.g. `astropy10__v4-pro__fvk-v1.yaml`). New model ⇒ copy a config, change `model.name` + `run_name` only. Pair-compare arms within the same model.
- An arm is what it injects (no declared type): nothing ⇒ `baseline`; `prompt.system_prompt` and/or `prompt.demos` ⇒ a treatment arm. Label precedence: config `tag:` > prompt frontmatter `tag:` > `baseline` / `fvk-<version>`. Legacy configs with `variant:` / `fvk_prompt:` still load (aliased); run artifacts use `arm` / `prompt_*` keys and readers fall back to the old `variant_tag` / `fvk_prompt_*`.
- DeepSeek V4 API: models `deepseek-v4-flash` / `deepseek-v4-pro`; thinking mode is a request param `{"thinking": {"type": "enabled"}}` (no more `deepseek-reasoner` alias)

## Commands

- Run an arm: `.venv/bin/python fvk_experiments/run.py run --config fvk_experiments/configs/<cfg>.yaml` (stages: `--stages infer,eval,report`; `--run-id <existing>` resumes)
- Pair report: `.venv/bin/python fvk_experiments/run.py compare --baseline fvk_experiments/runs/<a> --treatment fvk_experiments/runs/<b>`
- Env sanity: `.venv/bin/python fvk_experiments/run.py gold-sanity --config <cfg>` (gold patches must resolve 10/10 before trusting model evals)
- New subject set: `.venv/bin/python fvk_experiments/run.py pin-instances --repo <repo> --n <k>` (prints pinned ids to paste into new configs)
- Refreeze demos after editing a registry: `.venv/bin/python fvk_experiments/run.py build-demos --registry fvk_experiments/prompts/demos/<name>.yaml [--source <pool.json>]`
- Regenerate results index: `.venv/bin/python fvk_experiments/run.py results`
- Unit tests: `.venv/bin/python -m pytest fvk_experiments/tests/ -q`
- Typical cost/time on this machine: an arm of 10 instances ≈ 5–15 min end-to-end with cached docker images, well under $1 on either model (v3's 240k-token prompts ride DeepSeek prefix caching)

## Gotchas (this machine / network)

- HuggingFace Hub: transient `SSL: UNEXPECTED_EOF` — retry, or `HF_ENDPOINT=https://hf-mirror.com`
- Docker Hub pulls flake (EOF from registry-1.docker.io). The eval wrapper keeps images (`cache_level: instance`) and auto-reruns infra-errored instances; "Patch Apply Failed" is deterministic and never retried. Never read solved counts without checking `error_ids` — infra errors masquerade as model failures.
- The harness writes its report JSON to CWD (ignores `--report_dir`); `fvk_bench/evaluate.py` relocates the fresh copy. Ground truth = `runs/<id>/eval/*.json` + `logs/run_evaluation/<run_id>/**/report.json`.
- DeepSeek diffs routinely carry wrong `@@` hunk counts; `fvk_bench/extract.py` mechanically normalizes them (content untouched, both arms identically). Unnormalized originals: `runs/<id>/predictions.pre-normalize.jsonl`.
- `logs/` is gitignored (harness execution logs); `fvk_experiments/runs/` is committed for provenance (raw responses incl. reasoning, exact prompts, eval reports).
