---
version: 1
date: 2026-06-11
tag: baseline
derived_from: fvk-replicate.md
notes: >
  Single-pass baseline arm: read the public problem (benchmark/PROMPT.md) and
  repo/, produce one best-effort patch at patches/solution.patch, write a brief
  final report. Same instance metadata, same pre-built workspace model
  (deviation (b) of fvk-replicate.md), and the same shared ground rules as the
  other two arms (public info only, no gold patch, no hidden tests, no web search
  for the original fix/PR/issue) — but no phases, no review, no evaluator. Per the
  shared contract the answer key is not staged in this workspace and the baseline
  has no evaluator, so this arm makes no reference to private_eval/,
  swebench_row_full.json, or scripts/private_eval.py. Net: a clean single-pass arm
  with the same ground rules as the other two arms, just no review/eval/phases.
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

Your current working directory is a pre-built workspace staged with:

    benchmark/PROMPT.md                  # public instance fields + problem statement
    benchmark/public_instance.json       # public fields only
    repo/                                # {repo} checked out at the base commit
    .venv/                               # ready Python environment with repo/ installed

Use or create: `patches/`, `reports/`.

Do not re-clone the repository or rebuild the environment. Verify what is staged:

    cd repo
    git rev-parse HEAD
    cd ..
    .venv/bin/python -c "import {module_name}; print({module_name}.__version__)"
    .venv/bin/python -m pytest --version

Confirm that:

- `repo/` is checked out at base commit `{base_commit}`;
- `.venv/bin/python` imports `{module_name}` from the staged environment;
- the test runner works: run one quick public test already present under `repo/`.

Record what you verified in `reports/setup_notes.md`. If something is broken, repair the environment without changing `repo/` source files, and note what you did.

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
