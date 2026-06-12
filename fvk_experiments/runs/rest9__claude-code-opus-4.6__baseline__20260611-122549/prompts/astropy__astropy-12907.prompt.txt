<!-- RECONSTRUCTED PROMPT: auto-generated from the public issue; NOT Grigore's verbatim. Only astropy-13236 is verbatim. -->

# Prompt for Fresh Coding Agent: Single-Pass Baseline on `astropy__astropy-12907`

You are a fresh coding agent. Solve the SWE-bench Verified instance `astropy__astropy-12907`.

Your goal is to produce the best patch you can, in a single pass, using only public information.

## Instance

- Dataset: `princeton-nlp/SWE-bench_Verified`
- Exact row URL: `https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=0&length=1`
- Instance ID: `astropy__astropy-12907`
- Repository: `https://github.com/astropy/astropy.git`
- Base commit: `d16bfe05a744909de4b27f5875fe0d4ed41ce607`
- Base commit URL: `https://github.com/astropy/astropy/commit/d16bfe05a744909de4b27f5875fe0d4ed41ce607`
- Astropy version: `4.3`
- Difficulty: `15 min - 1 hour`

Known evaluator shape:

- `FAIL_TO_PASS`: 2 tests
- `PASS_TO_PASS`: 13 tests
- Official resolution criterion: resolved iff `FAIL_TO_PASS = 2/2` and `PASS_TO_PASS = 13/13`.

## Benchmark Discipline

These rules are mandatory.

1. You may use only public information for patch generation:
   - the public issue statement;
   - the base repository at the base commit;
   - existing public tests already present in the repository.
2. Do not inspect or use the gold `patch` field.
3. Do not manually inspect or use the hidden `test_patch` field.
4. Do not inspect hidden test names, hidden assertions, or hidden failure traces.
5. Do not search for the original Astropy PR, issue thread, or solution for this issue.
6. Do not attempt to access hidden tests or a reference solution: produce a single patch and stop.

## Workspace Setup

Your current working directory is a pre-built workspace staged with:

    benchmark/PROMPT.md                  # public instance fields + problem statement
    benchmark/public_instance.json       # public fields only
    repo/                                # astropy/astropy checked out at the base commit
    .venv/                               # ready Python environment with repo/ installed

Use or create: `patches/`, `reports/`.

Do not re-clone the repository or rebuild the environment. Verify what is staged:

    cd repo
    git rev-parse HEAD
    cd ..
    .venv/bin/python -c "import astropy; print(astropy.__version__)"
    .venv/bin/python -m pytest --version

Confirm that:

- `repo/` is checked out at base commit `d16bfe05a744909de4b27f5875fe0d4ed41ce607`;
- `.venv/bin/python` imports `astropy` from the staged environment;
- the test runner works: run one quick public test already present under `repo/`.

Record what you verified in `reports/setup_notes.md`. If something is broken, repair the environment without changing `repo/` source files, and note what you did.

## Task

Read only:

- `benchmark/PROMPT.md`
- source files under `repo/`
- existing public tests already present under `repo/`

The public issue is: "Modeling's `separability_matrix` does not compute separability correctly for nested CompoundModels".

Generate your best patch using only public information.

You may run public tests already present in the repo.

When the patch is complete, save it:

    cd repo
    git diff > ../patches/solution.patch
    cd ..

## Final Report

Write `reports/final_report.md` with this structure:

    # SWE-bench Baseline: astropy__astropy-12907

    ## Benchmark

    - Dataset: princeton-nlp/SWE-bench_Verified
    - Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=0&length=1
    - Repo: astropy/astropy
    - Repo URL: https://github.com/astropy/astropy.git
    - Instance ID: astropy__astropy-12907
    - Base commit: d16bfe05a744909de4b27f5875fe0d4ed41ce607
    - Base commit URL: https://github.com/astropy/astropy/commit/d16bfe05a744909de4b27f5875fe0d4ed41ce607
    - Version: 4.3
    - Difficulty: 15 min - 1 hour

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
