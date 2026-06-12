# START-45 — run the 45-instance FVK experiment (handoff runbook)

You're picking up a ready-to-run experiment. This doc is self-contained: follow it
top to bottom and you can run the whole thing without anyone explaining it.

## What you're running (30-second version)

A **controlled 3-arm comparison** on **45 SWE-bench_Verified instances** (the set a
collaborator ran; 8 repos — django 22, sympy 7, sphinx 5, astropy 3, pytest 3, xarray 2,
pylint 2, scikit-learn 1), executed as **headless Claude Code (Opus 4.6) agent sessions**.
The three arms differ only in what happens after the agent's first draft:

| arm | what it does |
|---|---|
| `baseline` | one pass: read the issue + repo, write a patch. No review. |
| `review-control` | draft → self-check → **plain-English review** → revise. (control) |
| `fvk-replicate` | draft → self-check → **Formal-Verification-Kit review** → revise. |

The point is to see whether FVK beats (a) plain review and (b) a single pass. Background
and the already-finished 10-instance pilot result: **[AGENTIC_FVK_ASTROPY10.md](AGENTIC_FVK_ASTROPY10.md)**.
Design rationale: [DESIGN.md](DESIGN.md). The 45 are split into **5 groups of 9**; you run
**one group per sitting**, all 3 arms.

## Prerequisites (check once)

```bash
claude --version          # Claude Code installed + logged in (the agent runs as `claude -p`)
docker ps                 # docker daemon up (grading uses official SWE-bench images)
.venv/bin/python -V       # the uv-managed venv this repo uses
```
- Run everything **from the repo root** (`/.../SWE-bench`).
- **No API keys needed** — this uses your Claude Code login, not an API.
- First run per repo pulls a docker image (cached after).

## The 5 groups

Each group is 9 instances. `[H]` = a "hard" repo whose env is pre-built for the agent so it
doesn't burn turns installing it. **Before starting a group, check its status here: only run
a group marked `open`, then mark it TAKEN and push, so no group is ever run twice.**

| group | status | instances |
|---|---|---|
| **batch1** | open | astropy-13398 [H], django-10554, -11138, -11400, -11885, -12325, -12708, -13128, -13212 |
| **batch2** | open | astropy-13579 [H], django-13344, -13449, -13837, -14007, -14011, -14631, -15128, -15268 |
| **batch3** | **DONE** — results in [AGENTIC_FVK_BATCH3.md](AGENTIC_FVK_BATCH3.md) | astropy-14369 [H], django-15503, -15629, -15957, -16263, -16560, -16631, pylint-4551, pylint-8898 |
| **batch4** | open | xarray-3993 [H], pytest-10356, -5787, -6197, sphinx-11510, -7590, -8548, -9229, -9461 |
| **batch5** | **TAKEN** — tested elsewhere, do not run | xarray-6992 [H], scikit-learn-25102 [H], sympy-12489, -13852, -13878, -14248, -16597, -17630, -18199 |

## Run ONE group (this is the whole loop)

Do a group at a time. Example for **batch1** — for any other group, swap `batch1` → `batchN`.

```bash
PY=.venv/bin/python
RUN="$PY fvk_experiments/run.py"
CFG=fvk_experiments/configs

# 0. one-time per group: warm the official docker images so sessions never wait on the registry
$RUN prepull-images --config $CFG/batch1__claude-code-opus46__baseline.yaml

# 1-3. the three arms, one at a time (each ~an hour+; phased arms are slower)
$RUN run --config $CFG/batch1__claude-code-opus46__baseline.yaml
$RUN run --config $CFG/batch1__claude-code-opus46__review-control.yaml
$RUN run --config $CFG/batch1__claude-code-opus46__fvk-replicate.yaml
```

Each `run` prints `solved X/9` at the end and writes `fvk_experiments/runs/<run_id>/report.md`.
Problems run **one at a time** (the configs set `max_workers: 1`) — don't parallelise.

## After a group: write up + commit

```bash
# per-instance pair reports vs the group's baseline (same group, same model)
$RUN compare --baseline fvk_experiments/runs/<batch1-baseline-run-id> \
             --treatment fvk_experiments/runs/<batch1-fvk-run-id>
$RUN results                                   # regenerate RESULTS.md from all runs

git add fvk_experiments/runs/batch1__* fvk_experiments/RESULTS.md fvk_experiments/reports/
git commit -m "batch1: agentic 45-set results (baseline/review/fvk)"
git push origin main
```

Find run ids with `ls -dt fvk_experiments/runs/batch1__*`. Repeat the whole loop for
batch2 … batch5 (one per sitting).

## How to read it / confirm it's healthy

- **`solved X/9`** is the official docker-harness `resolved` count (bug-fix tests all pass
  AND no regressions).
- For the phased arms, `report.md` has a **v1 → v2 transition table** (what the revise step
  changed) and a **claimed-vs-official** column (the agent's in-session score vs the real
  harness — they should agree).
- **Audit alarms are NOT all real — do not read `solved X/9` until you've checked them.**
  Sessions are sealed (no web, no memory, no plugins, no Skill tool) and the answer key
  lives outside the agent's reach; the audit (`runs/<id>/audit/<iid>.json`) still
  auto-blanks any session it flags, but **two false-positive classes are known**. Follow
  the mandatory procedure in **"Audit alarms: the without-audit scoring policy"** below.

## Audit alarms: the without-audit scoring policy (owner decision 2026-06-12)

The transcript audit has **two known false-positive classes**, found live on batch3. The
rule fix is deferred to a dedicated session — **do NOT edit the audit code mid-campaign**
(arms must all be graded by identical code).

1. **F2P name public at base.** The rule "hidden FAIL_TO_PASS name in the transcript ⇒
   leak" assumes hidden test names don't exist publicly — false when the instance's hidden
   test_patch *modifies an existing public test* (pylint-8898: its only F2P test exists
   verbatim at the base commit) or adds parameters to one (astropy-14369, pylint-4551).
   Reading the public test suite — allowed and necessary — trips the wire.
2. **Reads of the agent's own score log.** Any Read-tool access to a path containing
   `/private_eval/` is treated as an answer-key read, but that dir holds only
   `eval_log.jsonl`, the aggregate-only score log the evaluator writes *for* the agent.
   (`bash cat` doesn't trip it; the Read tool does — pure session luck.)

**Policy: batch scores are reported "without-audit".** Run the pipeline UNMODIFIED (the
audit still logs and still auto-blanks; its artifacts stay untouched as provenance). Then,
for EVERY auto-blanked instance (`final=contaminated` in the run output):

1. Read `runs/<id>/audit/<iid>.json` and confirm the evidence is one of the two classes
   above. **If it's anything else — a read of the real key (`row.json`), network reach,
   denied-tool use — STOP and escalate to the owner. Do not merge.**
2. Salvage the agent's final patch from its workspace
   (`~/.cache/fvk-workspaces/<run-dir-name>/<iid>/patches/`; baseline arm:
   `solution.patch`, phased arms: the final patch named in the workspace's
   `reports/final_report.md`, typically `solution_v2.patch`) into `runs/<id>/salvaged/`.
3. Re-grade it with the official harness. Write a one-line
   `runs/<id>/salvaged/predictions.jsonl`
   (`{"instance_id": "<iid>", "model_name_or_path": "salvage-regrade", "model_patch": "<patch>"}`),
   then from the repo root:
   ```bash
   .venv/bin/python -m swebench.harness.run_evaluation \
     --dataset_name princeton-nlp/SWE-bench_Verified --split test \
     --predictions_path fvk_experiments/runs/<id>/salvaged/predictions.jsonl \
     --instance_ids <iid> --max_workers 1 --timeout 1800 --cache_level instance \
     --run_id salvage__<short-label> --report_dir fvk_experiments/runs/<id>/salvaged
   ```
   (Known quirk: the report JSON lands in the CWD — move it into `salvaged/`.)
4. **Merge** the re-grade into the arm's reported score and document the case (mechanism,
   patch file, re-grade verdict) in `runs/<id>/salvaged/README.md`. The arm's reported
   number = pipeline `solved X/9` **+ restored resolves**, labeled **without-audit**; the
   pipeline's own `report.md`/`eval/` are never edited.

The seal itself (web denied, truncated history, key outside the workspace) is unchanged —
actual cheating is still prevented; we've only demoted an over-eager *detector* from gate
to log. All transcripts are preserved verbatim, so the corrected audit can be re-applied
retroactively to confirm these scores in the fix-session.

## Gotchas

- **It's slow.** A phased session is ~10–40 min (env build + multi-phase + docker grade), so
  a full group of 27 sessions is several hours. That's expected.
- **Sessions are sandboxed but the infra has one un-exercised step:** every gold patch grades
  correctly across all 8 repos (see `PREP_NOTES.md` → "VALIDATION RESULTS"), but a *live agent
  session* on a non-astropy repo hasn't been run end-to-end yet. **batch1 is the first real
  run** — after the first instance finishes, glance at `runs/<id>/raw/astropy__astropy-13398.jsonl`
  (or any instance) and its `audit/` to confirm the agent built its env and graded cleanly. If
  something's off, stop and inspect before burning the rest.
- **Image pull flaked?** Re-run `prepull-images`. **A session wedged?** The 90-min per-session
  timeout harvests whatever exists and moves on — no babysitting needed.
- **Resume:** `run --run-id <existing>` continues a run; `--stages infer,eval,report` runs a
  subset (e.g. re-grade without re-inferring).

## Where everything lives

- **Configs:** `fvk_experiments/configs/batch{1..5}__claude-code-opus46__{baseline,review-control,fvk-replicate}.yaml`
- **The three protocols (prompts):** `fvk_experiments/prompts/agentic/{baseline,review-control,fvk-replicate}-v2.md`
  (replicate-vs-control diff: `prompts/agentic/CONTROL_DIFF-v2.md`; the collaborator's verbatim
  source: `prompts/agentic/source/`)
- **Pilot result + methodology:** `fvk_experiments/AGENTIC_FVK_ASTROPY10.md`
- **Prep details + the full validation matrix:** `PREP_NOTES.md` (repo root)
- **Per-run output (transcripts, prompts, audits, eval):** `fvk_experiments/runs/`
- **Results index:** `fvk_experiments/RESULTS.md`

## If you want to change something

- **Different instances / regroup:** edit `dataset.instance_ids` in a config, or regenerate
  all 15 with `.venv/bin/python fvk_experiments/scripts/build_batch45_configs.py`.
- **One quick smoke before committing to a full group:** copy a config, cut
  `instance_ids` to a single id, run it.
- House rules (frozen prompts, config conventions, network/docker quirks): the repo's
  `CLAUDE.md` and `fvk_experiments/README.md`.
