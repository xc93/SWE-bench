# FVK Pair-Comparison Experiments

A/B testing of **formal-verification-kit (FVK)** methodology prompts for DeepSeek on
SWE-bench. **Results: [RESULTS.md](RESULTS.md)** (auto-generated, one line per run).
Design decisions and rationale: [DESIGN.md](DESIGN.md); prompt lineage and intent:
[prompts/fvk/CHANGELOG.md](prompts/fvk/CHANGELOG.md).

Every treatment arm pairs against a **baseline**: DeepSeek (V4, thinking) gets the
standard SWE-bench *oracle* prompt (issue + relevant source files) and answers with a
patch — no system message. Treatment arms inject one frozen, versioned prompt from
[prompts/fvk/](prompts/fvk/) as the system message:

| arm | prompt | idea |
|---|---|---|
| `fvk-v1` | `v1.md` (~1.7k tok) | distilled FVK digest, spec-first: formalize → verify → patch |
| `fvk-v2` | `v2.md` (~10k tok) | comprehensive distillation: full K knowledge base + procedure |
| `fvk-v3` | `v3.md` (~212k tok) | entire kit repo **verbatim**, thin one-shot wrapper — no distillation; regenerate with [scripts/build_v3_verbatim.py](scripts/build_v3_verbatim.py) |
| `fvk-v4` | `v4.md` (~1.9k tok) | draft a candidate fix → FVK-check it (formalize + verify, findings) → regenerate |
| `review-v5` | `v5.md` (~0.8k tok) | **control for v4**: same draft → critique → regenerate structure, plain code review, zero FVK content |
| `jointembed-v6` | `v6.md` + [demos](prompts/demos/) (~4–9k tok/instance) | joint-embedding mimic: **per-instance** system message = short directive + 3 hand-matched solved benchmark problems (issue + gold patch) from outside the evaluated set |

The subject set `astropy10` = the first 10 astropy instances of
`SWE-bench_Verified:test` in HF row order, pinned explicitly in every config.
"Solved" = `resolved` in the official SWE-bench evaluation harness (docker).

Since v6, the system message is composed **per test instance**: the static prompt
(`prompt.fvk_prompt`) plus, optionally, that instance's demonstrations
(`prompt.demos`). Either part can be used alone or both together (e.g. an
FVK-plus-demos arm is just one config setting both keys). The exact composed message
sent to the model is always archived per instance in `runs/<id>/prompts/<iid>.system.txt`.

## Quickstart (from the SWE-bench repo root)

```bash
export DEEPSEEK_API_KEY=…           # required for inference

PY=.venv/bin/python
RUN="$PY fvk_experiments/run.py"

# 0. one-time environment sanity: do the gold patches still pass? (also pre-pulls images)
$RUN gold-sanity --config fvk_experiments/configs/astropy10__v4-flash__baseline.yaml

# 1. baseline arm  →  prints "solved X/10", writes runs/<run_id>/report.md
$RUN run --config fvk_experiments/configs/astropy10__v4-flash__baseline.yaml

# 2. fvk arm
$RUN run --config fvk_experiments/configs/astropy10__v4-flash__fvk-v1.yaml

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
- **Which prompt**: point `prompt.fvk_prompt` at `prompts/fvk/vN.md`. Prompt files
  carry YAML frontmatter (`version`, `source`, `date`); the version becomes part of the
  run label and the file's sha256 is recorded in `meta.json`/reports, so every report is
  traceable to an exact prompt. Non-FVK control prompts set frontmatter `tag:`
  (e.g. `review-v5`) to override the default `fvk-vN` arm label. Prompts are frozen
  once run: a new idea ⇒ a new `vN.md` + a CHANGELOG entry + a new config.
- **Which demonstrations** (per-instance prompts): set `prompt.demos` to a registry
  YAML like [prompts/demos/astropy10_demos_v1.yaml](prompts/demos/astropy10_demos_v1.yaml)
  — per test instance, 3 picks `{id, rationale}` chosen from the benchmark **outside**
  the evaluated set. To revise: edit the registry, then refreeze verbatim issue+patch
  content with
  `run.py build-demos --registry fvk_experiments/prompts/demos/<name>.yaml`
  (writes the sibling `.content.json`, sha-stamped so a changed registry can never run
  with stale content; the validator enforces 3 distinct picks and rejects any pick from
  the evaluated instances). Both shas are recorded in each run's `meta.json`.
- **Which model**: `model.name` (`deepseek-v4-flash` ⇄ `deepseek-v4-pro`),
  `model.thinking` (true/false). One config per **(subject × model × arm)**, named
  `<subject>__<model-short>__<arm>.yaml` with
  `run_name: <subject>__ds-<model-short>-think__<arm>` — to add a model, copy an
  existing config and change only `model.name` and `run_name`. The model is carried
  through run ids, prediction labels, reports, and RESULTS.md automatically. Compare
  arms **within** one model; cross-model pair reports get a loud warning banner since
  they measure the model, not the prompt.

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
also covers these additions). The FVK prompts are distilled from
[grosu/formal-verification-kit](https://github.com/grosu/formal-verification-kit) (MIT),
vendored as a git submodule at [vendor/formal-verification-kit](vendor/) and pinned to
the distillation commit recorded in each prompt's frontmatter
(`git submodule update --init` after cloning).
