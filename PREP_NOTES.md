# PREP_NOTES — 45-instance multi-repo run (DRAFT, UNVALIDATED)

Drafted on branch `prep-45` in the isolated worktree `SWE-bench-prep45`, while a
live astropy10 batch runs in the sibling checkout. **Nothing here has been run
end-to-end.** No model session, no docker, and no venv/image build was performed
while drafting — all real builds/docker/sessions are deferred to the validation
pass below.

This extends the agentic `claude-code` family (baseline / review-control /
fvk-replicate) from the astropy-only **v1** design to a **v2** multi-repo design
for the 45-instance Grigore-set spanning 8 repos (django 22, sympy 7, sphinx-doc
5, astropy 3, pytest-dev 3, pydata/xarray 2, pylint-dev 2, scikit-learn 1).

## The agreed v2 design (what's implemented as a draft)

1. **Agent self-builds its env (Phase 0).** v1 pre-built a `.venv` per workspace
   and verified it; v2 reverts that half of deviation (b): the agent creates its
   own venv and `pip install -e .`s the **pre-staged** repo (no clone, no
   remote — the truncated-history leak fence is unchanged) plus pytest. Ad-hoc
   local test running is explicitly encouraged. The **6 hard
   compiled-dependency instances** (3 astropy + 2 xarray + 1 scikit-learn) keep
   a **pre-built** venv from our builder; the other **39** are repo-only.
2. **Authoritative grading via docker.** The in-session `scripts/private_eval.py`
   (Phase 2/5 aggregate) and final scoring grade inside the instance's
   **official prebuilt SWE-bench image**, reusing the harness eval mechanism —
   NOT a local temp copy. The agent's self-built env is only its iterating
   scratchpad; it never produces the reported numbers. Output contract is
   IDENTICAL to v1: exactly three aggregate lines, no test names.

## Files created / modified (all in the worktree, branch `prep-45`)

Created:
- `fvk_experiments/fvk_bench/env_specs.py` — env-recipe adapter over
  `swebench.harness.constants.MAP_REPO_VERSION_TO_SPECS`. `spec_for(repo,
  version) -> EnvSpec{python_version, install_cmds, test_cmd, repo_import_name,
  found, raw}` and `import_name_for(repo)` (repo->import map; sklearn/sphinx/etc.
  fixed, fallback to the path tail). Pure read — no installs/docker/network.
- `fvk_experiments/prompts/agentic/{baseline,review-control,fvk-replicate}-v2.md`
  — v2 templates. **Verbatim copies of v1 except Phase 0 / Workspace Setup**,
  which become "a `.venv` may already be staged — verify it; if not, create one
  and `pip install -e .` the staged repo + pytest", plus explicit encouragement
  of ad-hoc local tests. Frontmatter `version: 2`, `derived_from`, `deviations:`
  (`DEVIATION (b-v2)`). v1 templates are **untouched and frozen**.
- `fvk_experiments/configs/batch{1..5}__claude-code-opus46__{baseline,
  review-control,fvk-replicate}.yaml` — 15 configs (5 sittings x 3 arms), via
  `scripts/build_batch45_configs.py`. provider claude-code, name
  claude-code-opus-4.6, cc_model claude-opus-4-6, max_turns 200,
  session_timeout_s 5400, inference.max_workers 1, prompt -> the arm's v2
  template, tag = arm.
- `fvk_experiments/scripts/build_batch45_configs.py` — deterministic config
  generator with a self-check (union == the 45 unique ids).
- `fvk_experiments/tests/test_env_specs.py`, `tests/test_batch_configs.py` — unit
  tests (below). Extended `tests/test_agentic_prompts.py` with v2 + generalized
  import-name tests.

Modified:
- `fvk_experiments/fvk_bench/agentic_prompts.py` — `module_name` is now the
  generalized IMPORT name via `env_specs.import_name_for` (sklearn->sklearn,
  sphinx-doc->sphinx, …); for astropy it stays `astropy`, so curated-13236
  fidelity is unaffected. `repo_title` stays the display name from the repo path.
- `fvk_experiments/fvk_bench/agentic.py` — v2 env policy + docker grading.
  - `HARD_VENV_INSTANCES` (the 6 hard ids), `protocol_version(cfg)` (reads the
    template's frontmatter `version:`), `venv_prestaged(cfg, iid)` (v1 => always
    pre-built so astropy10 is unchanged; v2 => only the hard ids). Aliases
    `HARD_PREBUILD_IDS` / `should_prebuild_env` for id-only callers.
  - `build_workspace(..., prebuild_env=None, grading_backend="local")`: venv
    decision = `build_venv AND (prebuild_env if given else venv_prestaged(cfg,
    iid))` — `build_venv=False` still hard-skips (tests); manifest records
    `prebuilt_env` + `grading_backend`.
  - Docker grading: `instance_image_candidates`, `docker_eval_staging` (the
    `_staging.eval` payload — official image names + the official `eval_script`
    that embeds the hidden test_patch + parser; lives in the OUT-OF-WORKSPACE
    row.json only), `ensure_instance_image` (pre-pull), and the docker variant
    of `scripts/private_eval.py` (`PRIVATE_EVAL_SCRIPT_DOCKER`), selected by
    `grading_backend="docker"`. `_render_private_eval` picks the backend.
- `fvk_experiments/prompts/fvk/CHANGELOG.md` — v2 entry.

NOTE: `fvk_bench/agentic.py`'s docker-grading subsystem (image candidates,
`docker_eval_staging`, `ensure_instance_image`, `PRIVATE_EVAL_SCRIPT_DOCKER`) was
co-developed in this worktree; this prep wired it into `build_workspace` /
`_staging_extras` / `_render_private_eval` and tests, and removed an earlier
harness-CLI docker draft that it superseded. The whole docker path is still
**UNVALIDATED** (see below).

## Batch -> id mapping (union == 45 unique; the 5 batches partition the 45)

Hard (pre-built-venv) instances flagged `[H]`.

- **batch1** (9): astropy-13398 [H], django-10554, -11138, -11400, -11885,
  -12325, -12708, -13128, -13212
- **batch2** (9): astropy-13579 [H], django-13344, -13449, -13837, -14007,
  -14011, -14631, -15128, -15268
- **batch3** (9): astropy-14369 [H], django-15503, -15629, -15957, -16263,
  -16560, -16631, pylint-4551, pylint-8898
- **batch4** (9): xarray-3993 [H], pytest-10356, pytest-5787, pytest-6197,
  sphinx-11510, sphinx-7590, sphinx-8548, sphinx-9229, sphinx-9461
- **batch5** (9): xarray-6992 [H], scikit-learn-25102 [H], sympy-12489, -13852,
  -13878, -14248, -16597, -17630, -18199

Hard coverage: batches 1–4 carry one hard instance each; batch5 carries two
(xarray-6992 + scikit-learn-25102). All 6 hard ids present exactly once.

## What the unit tests cover (green: `pytest fvk_experiments/tests/ -q`)

- **env_specs**: import names for all 8 repos + fallback; `spec_for` returns the
  right python/import/test_cmd/install order for django/sympy/sphinx/astropy/
  sklearn/xarray/pylint/pytest at the versions the 45 actually use; unknown pair
  => generic `found=False`.
- **batch_configs**: all 15 configs load + label + point at the v2 templates;
  the 5 batches partition the 45 exactly (disjoint, union == 45, none
  missing/extra); all 6 hard ids present; `protocol_version` reads the template
  frontmatter; **`venv_prestaged` is True for all under v1 (astropy10 unchanged)
  and only the hard ids under v2**; `build_workspace` records
  `prebuilt_env`/`grading_backend`, repo-only skips the venv, the local vs docker
  evaluator scripts are emitted correctly, the docker `_staging.eval` payload
  stays OUT of the workspace, `instance_image_candidates` mangling matches the
  official key, unsupported repos raise in `docker_eval_staging`, bad backend
  rejected.
- **agentic_prompts (v2)**: v2 templates instantiate (string-substitution only)
  for one instance per repo with the correct `import {module_name}` line;
  scikit-learn emits `import sklearn`; Phase 0 is agent-self-build (no-clone /
  no-remote guard, `python3 -m venv`, `pip install -e .`, ad-hoc tests
  encouraged); phased v2 keeps the 5-phase protocol + discipline + grading line +
  final report; review-control-v2 stays FVK-free; baseline-v2 stays single-pass +
  neutral; **the v1 astropy path is unchanged** (module_name/repo_title still
  astropy/Astropy; the frozen 13236 residual-diff fidelity test still passes).

Unit tests do NOT build any env, call docker, or start a session (the one
pre-existing real-build integration test stays opt-in behind `AGENTIC_IT=1` and
is skipped).

## VALIDATION PENDING — run after the astropy10 batch finishes (host free)

Everything below needs a free host with docker + network; do it on `prep-45`
before any 45-run. **The 6-hard-instance prebuilds and the docker-grading repoint
are UNVALIDATED drafts.**

1. **Pre-build the 6 hard envs.** For each of astropy-13398/-13579/-14369,
   xarray-3993/-6992, scikit-learn-25102: build the workspace with the venv
   (the v2 path pre-builds these via `venv_prestaged`) and confirm `import
   {module_name}` + a quick repo test run inside the built `.venv`. Watch the
   xarray (scipy/pandas/dask) and sklearn (cython, `--no-build-isolation`)
   builds — these are exactly why they're in the hard set.
2. **Smoke one instance per repo (8 repos).** For one id from each of django,
   sympy, sphinx-doc, astropy, pytest-dev, xarray, pylint-dev, scikit-learn:
   - **env**: for the 39 repo-only ids, confirm the agent's Phase-0 self-build
     works (a fresh `python3 -m venv` + `pip install -e .` against the staged
     repo imports the module and runs a public test); for the 6 hard ids, the
     pre-built venv works. (sphinx/django/pytest test entry points differ from
     bare pytest — confirm the agent can run *some* public test, the template
     only asks for that.)
   - **docker grade of a GOLD patch returns resolved**: stage the workspace with
     `grading_backend="docker"`, run `ensure_instance_image(row)` (image pull),
     then `scripts/private_eval.py <gold.patch> gold` and confirm it prints
     `resolved: true` with `FAIL_TO_PASS n/n` / `PASS_TO_PASS m/m`. Cross-check
     the counts against `run.py gold-sanity` for the same id.
   - **agent can run ad-hoc tests**: confirm a session (or a manual repro) can
     run repo tests locally in its env without touching the docker grader.
3. **Confirm the docker-grading repoint output contract.** The docker
   `scripts/private_eval.py` must print EXACTLY the three aggregate lines (no
   test names, no tracebacks, no container logs on stdout), byte-compatible with
   the v1 local evaluator's contract that the report parser (`fvk_bench/report.py
   ::parse_claimed_aggregates`) and the templates expect. Diff a docker-graded
   score against a v1 local-graded score for an astropy id (should agree).
4. **Leak re-check.** Confirm the hidden `eval_script`/test_patch lives ONLY in
   the out-of-workspace `row.json _staging.eval` and never appears under the
   workspace tree (the unit test checks the stub; re-check with a real payload),
   and that the transcript audit still flags any read of the row.
5. **One full batch dry-run.** Run `batch5` (has both remaining hard ids +
   sympy) for one arm with `run.py run --stages infer,eval` and confirm
   in-session aggregates match the final harness eval.

Until items 1–5 pass: treat the 6-hard-instance builders and the docker grading
repoint as drafts. The local backend (`grading_backend="local"`, the v1 default)
remains the validated, unit-tested path.
