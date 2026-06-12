<!-- RECONSTRUCTED PROMPT: auto-generated from the public issue; NOT Grigore's verbatim. Only astropy-13236 is verbatim. -->

# Prompt for Fresh Coding Agent: Single-Pass Baseline on `sympy__sympy-17630`

You are a fresh coding agent. Solve the SWE-bench Verified instance `sympy__sympy-17630`.

Your goal is to produce the best patch you can, in a single pass, using only public information.

## Instance

- Dataset: `princeton-nlp/SWE-bench_Verified`
- Exact row URL: `https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=461&length=1`
- Instance ID: `sympy__sympy-17630`
- Repository: `https://github.com/sympy/sympy.git`
- Base commit: `58e78209c8577b9890e957b624466e5beed7eb08`
- Base commit URL: `https://github.com/sympy/sympy/commit/58e78209c8577b9890e957b624466e5beed7eb08`
- Sympy version: `1.5`
- Difficulty: `1-4 hours`

Known evaluator shape:

- `FAIL_TO_PASS`: 2 tests
- `PASS_TO_PASS`: 19 tests
- Official resolution criterion: resolved iff `FAIL_TO_PASS = 2/2` and `PASS_TO_PASS = 19/19`.

## Benchmark Discipline

These rules are mandatory.

1. You may use only public information for patch generation:
   - the public issue statement;
   - the base repository at the base commit;
   - existing public tests already present in the repository.
2. Do not inspect or use the gold `patch` field.
3. Do not manually inspect or use the hidden `test_patch` field.
4. Do not inspect hidden test names, hidden assertions, or hidden failure traces.
5. Do not search for the original Sympy PR, issue thread, or solution for this issue.
6. Do not attempt to access hidden tests or a reference solution: produce a single patch and stop.

## Workspace Setup

Your current working directory is a staged workspace containing:

    benchmark/PROMPT.md                  # public instance fields + problem statement
    benchmark/public_instance.json       # public fields only
    repo/                                # sympy/sympy checked out at the base commit (truncated history, no remote)
    .venv/                               # MAY be pre-staged (hard compiled-deps only); otherwise you create it below

Use or create: `patches/`, `reports/`.

Do not re-clone the repository and do not add a git remote. The repository is already staged at `repo/` (checked out at the base commit, with truncated history and no origin). Set up a Python environment against it.

A `.venv/` may already be staged for this instance. First check whether it works:

    cd repo
    git rev-parse HEAD
    cd ..
    .venv/bin/python -c "import sympy; print(sympy.__version__)" 2>/dev/null && echo "venv OK" || echo "need to build venv"

If `.venv/` is already staged and works, verify it and use it. Otherwise create one and install the repo and its test dependencies yourself. Prefer repo instructions; practical fallback:

    export SETUPTOOLS_SCM_PRETEND_VERSION=1.5  # the staged checkout has truncated history (no tags), which otherwise breaks setuptools-scm version detection
    uv venv --python 3.9 .venv || uv venv --python 3.11 .venv || python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -U pip setuptools wheel
    (cd repo && python -m pip install -e .) || true
    python -m pip install pytest || true

Install enough public test dependencies to run relevant tests.

Confirm that:

- `repo/` is checked out at base commit `58e78209c8577b9890e957b624466e5beed7eb08`;
- `.venv/bin/python` imports `sympy` from your environment;
- the test runner works: run one quick public test already present under `repo/`.

Record what you did and verified in `reports/setup_notes.md`. Running the repo's own public tests locally is encouraged. Do not modify `repo/` source files during setup; only change source as part of your patch below.

## Task

Read only:

- `benchmark/PROMPT.md`
- source files under `repo/`
- existing public tests already present under `repo/`

The public issue is: "Exception when multiplying BlockMatrix containing ZeroMatrix blocks".

Generate your best patch using only public information.

You may run public tests already present in the repo.

When the patch is complete, save it:

    cd repo
    git diff > ../patches/solution.patch
    cd ..

## Final Report

Write `reports/final_report.md` with this structure:

    # SWE-bench Baseline: sympy__sympy-17630

    ## Benchmark

    - Dataset: princeton-nlp/SWE-bench_Verified
    - Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=461&length=1
    - Repo: sympy/sympy
    - Repo URL: https://github.com/sympy/sympy.git
    - Instance ID: sympy__sympy-17630
    - Base commit: 58e78209c8577b9890e957b624466e5beed7eb08
    - Base commit URL: https://github.com/sympy/sympy/commit/58e78209c8577b9890e957b624466e5beed7eb08
    - Version: 1.5
    - Difficulty: 1-4 hours

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
