---
version: 2
date: 2026-06-11
tag: baseline
derived_from: baseline.md
source: >
  v2 of the agentic baseline template for the 45-instance multi-repo
  (Grigore-set) run. Single-pass arm: read the public problem, produce one
  best-effort patch at patches/solution.patch, brief final report. Wording
  copied verbatim from baseline.md (v1) EXCEPT the Workspace Setup section,
  which changes from "verify a pre-built env" to "set up or verify the env"
  (agent self-build; see notes). v1 stays frozen and astropy-only.
notes: >
  Same shared ground rules as the other two v2 arms (public info only; no gold
  patch; no hidden tests; no web lookup of the original fix/PR/issue). No phases,
  no evaluator, no answer key staged: this arm makes no reference to
  private_eval/, swebench_row_full.json, or scripts/private_eval.py. The only
  change from v1 is the Workspace Setup section: the Python environment is agent
  self-built when not pre-staged (a .venv is pre-staged only for the hard
  compiled-dependency instances). The repo is still staged with truncated history
  and no remote (no clone, no remote), preserving v1's leak-safety. Running the
  repo's own public tests locally is explicitly encouraged.
deviations:
  - >
    (b-v2) Workspace Setup is now AGENT SELF-BUILD, not pre-built-env verification.
    repo/ is staged (history-truncated, no remote); a .venv is pre-staged only for
    hard compiled-dependency instances, otherwise the agent creates it and installs
    the repo editable plus pytest. Supersedes v1's pre-built-workspace assumption.
fields:
  - instance_id
  - repo
  - repo_url
  - base_commit
  - base_commit_url
  - repo_title
  - module_name
  - version
  - difficulty
  - fail_to_pass_count
  - pass_to_pass_count
  - row_url
  - public_issue_gist
  - likely_files_block
---
# Prompt for Fresh Coding Agent: Single-Pass Baseline on `{instance_id}`

You are a fresh coding agent. Solve the SWE-bench Verified instance `{instance_id}`.

Your goal is to produce the best patch you can, in a single pass, using only public information.

## Instance

- Dataset: `princeton-nlp/SWE-bench_Verified`
- Exact row URL: `{row_url}`
- Instance ID: `{instance_id}`
- Repository: `{repo_url}`
- Base commit: `{base_commit}`
- Base commit URL: `{base_commit_url}`
- {repo_title} version: `{version}`
- Difficulty: `{difficulty}`

Known evaluator shape:

- `FAIL_TO_PASS`: {fail_to_pass_count} tests
- `PASS_TO_PASS`: {pass_to_pass_count} tests
- Official resolution criterion: resolved iff `FAIL_TO_PASS = {fail_to_pass_count}/{fail_to_pass_count}` and `PASS_TO_PASS = {pass_to_pass_count}/{pass_to_pass_count}`.

## Benchmark Discipline

These rules are mandatory.

1. You may use only public information for patch generation:
   - the public issue statement;
   - the base repository at the base commit;
   - existing public tests already present in the repository.
2. Do not inspect or use the gold `patch` field.
3. Do not manually inspect or use the hidden `test_patch` field.
4. Do not inspect hidden test names, hidden assertions, or hidden failure traces.
5. Do not search for the original {repo_title} PR, issue thread, or solution for this issue.
6. Do not attempt to access hidden tests or a reference solution: produce a single patch and stop.

## Workspace Setup

Your current working directory is a staged workspace containing:

    benchmark/PROMPT.md                  # public instance fields + problem statement
    benchmark/public_instance.json       # public fields only
    repo/                                # {repo} checked out at the base commit (truncated history, no remote)
    .venv/                               # MAY be pre-staged (hard compiled-deps only); otherwise you create it below

Use or create: `patches/`, `reports/`.

Do not re-clone the repository and do not add a git remote. The repository is already staged at `repo/` (checked out at the base commit, with truncated history and no origin). Set up a Python environment against it.

A `.venv/` may already be staged for this instance. First check whether it works:

    cd repo
    git rev-parse HEAD
    cd ..
    .venv/bin/python -c "import {module_name}; print({module_name}.__version__)" 2>/dev/null && echo "venv OK" || echo "need to build venv"

If `.venv/` is missing or does not import `{module_name}`, create one and install the staged repo editable, plus pytest:

    python3 -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    cd repo
    ../.venv/bin/python -m pip install -e .
    ../.venv/bin/python -m pip install pytest
    cd ..

(If the editable install needs extras or build/test dependencies for {repo_title}, install them too; the goal is an environment where you can import `{module_name}` and run the repo's own tests.)

Confirm that:

- `repo/` is checked out at base commit `{base_commit}`;
- `.venv/bin/python` imports `{module_name}` from your environment;
- the test runner works: run one quick public test already present under `repo/`.

Record what you did and verified in `reports/setup_notes.md`. Running the repo's own public tests locally is encouraged. Do not modify `repo/` source files during setup; only change source as part of your patch below.

## Task

Read only:

- `benchmark/PROMPT.md`
- source files under `repo/`
- existing public tests already present under `repo/`

{likely_files_block}{public_issue_gist}

Generate your best patch using only public information.

You may run public tests already present in the repo.

When the patch is complete, save it:

    cd repo
    git diff > ../patches/solution.patch
    cd ..

## Final Report

Write `reports/final_report.md` with this structure:

    # SWE-bench Baseline: {instance_id}

    ## Benchmark

    - Dataset: princeton-nlp/SWE-bench_Verified
    - Exact row URL: {row_url}
    - Repo: {repo}
    - Repo URL: {repo_url}
    - Instance ID: {instance_id}
    - Base commit: {base_commit}
    - Base commit URL: {base_commit_url}
    - Version: {version}
    - Difficulty: {difficulty}

    ## Benchmark Discipline

    - Gold patch inspected: yes/no
    - Hidden test_patch manually inspected: yes/no
    - Hidden test names inspected: yes/no
    - Hidden assertions inspected: yes/no
    - Hidden failure traces inspected: yes/no

    ## Public Problem Summary

    Summarize the public issue.

    ## Patch

    - Files changed:
    - Behavioral change:
    - Public tests run:
    - Why this matches the public issue statement:

## Final Response

Return only this summary:

    patch: patches/solution.patch
    files changed:
    benchmark discipline:
      preserved: yes/no
      notes:
    final_report.md: <path>

Do not include hidden test names, hidden assertions, hidden failure traces, hidden patch contents, or the gold solution.
