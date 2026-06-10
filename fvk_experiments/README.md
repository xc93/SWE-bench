# FVK Pair-Comparison Experiments

A/B testing of a distilled **formal-verification-kit (FVK)** methodology prompt for
DeepSeek on SWE-bench. **Results: [RESULTS.md](RESULTS.md)** (auto-generated, one line
per run). Design decisions and rationale: [DESIGN.md](DESIGN.md).

- **Arm A — baseline**: DeepSeek (V4, thinking) gets the standard SWE-bench *oracle*
  prompt (issue + relevant source files) and answers with a patch. No special prompts.
- **Arm B — fvk**: identical, plus a versioned FVK prompt
  ([prompts/fvk/](prompts/fvk/)) injected as a system message: *formalize the program,
  then verify the fix against the spec, before emitting the patch*.

"Solved" = `resolved` in the official SWE-bench evaluation harness (docker).

## Quickstart (from the SWE-bench repo root)

```bash
export DEEPSEEK_API_KEY=…           # required for inference

PY=.venv/bin/python
RUN="$PY fvk_experiments/run.py"

# 0. one-time environment sanity: do the gold patches still pass? (also pre-pulls images)
$RUN gold-sanity --config fvk_experiments/configs/astropy10_baseline.yaml

# 1. baseline arm  →  prints "solved X/10", writes runs/<run_id>/report.md
$RUN run --config fvk_experiments/configs/astropy10_baseline.yaml

# 2. fvk arm
$RUN run --config fvk_experiments/configs/astropy10_fvk_v1.yaml

# 3. pair report → solved_count_baseline vs solved_count_fvk
$RUN compare --baseline fvk_experiments/runs/<baseline_run_id> \
             --treatment fvk_experiments/runs/<fvk_run_id>
```

Useful flags for `run`: `--stages infer,eval,report` (any subset), `--run-id <existing>`
to continue/redo stages of a run, `--no-resume` to force fresh API calls.

## Changing the experiment

Everything is config-driven ([configs/](configs/)):

- **Which tests**: edit `dataset.instance_ids` (pin new ones with
  `run.py pin-instances --repo <repo> --n <k>`).
- **Which FVK prompt**: point `prompt.fvk_prompt` at `prompts/fvk/vN.md`. Prompt files
  carry YAML frontmatter (`version`, `source`, `date`); the version becomes part of the
  run label and the file's sha256 is recorded in `meta.json`/reports, so every report is
  traceable to an exact prompt.
- **Which model**: `model.name` (`deepseek-v4-flash` ⇄ `deepseek-v4-pro`),
  `model.thinking` (true/false).

## Where results land

```
runs/<run_name>__<utc-ts>/
  config.snapshot.yaml   exact config used
  meta.json              model, prompt version + sha256, timing, counts
  prompts/               exact system/user messages sent per instance
  raw/<iid>.json         full API responses incl. reasoning_content + usage
  predictions.jsonl      SWE-bench prediction format
  eval/                  official harness report JSON
  report.md / summary.json   human + machine readable per-run results
reports/pair__<A>__VS__<B>.md   the pair comparison
```

Harness execution logs: `logs/run_evaluation/<run_id>/` (repo root).

Unit tests: `.venv/bin/python -m pytest fvk_experiments/tests/ -q`

## License & attribution

This directory lives in a fork of [SWE-bench](https://github.com/SWE-bench/SWE-bench)
(MIT License, © 2023 Carlos E Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin
Pei, Ofir Press, Karthik R Narasimhan — see the repo-root [LICENSE](../LICENSE), which
also covers these additions). The FVK prompt is distilled from
[grosu/formal-verification-kit](https://github.com/grosu/formal-verification-kit) (MIT);
source commit recorded in each prompt's frontmatter.
