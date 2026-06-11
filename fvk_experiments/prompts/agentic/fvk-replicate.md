---
version: 1
date: 2026-06-11
tag: fvk-replicate
source: >
  Reversed from Grigore Rosu's verbatim per-instance prompts (Telegram group
  "Fast Verification Positioning", 2026-06-10/11): astropy_13236_fvk_prompt.md
  (primary, followed byte-faithfully) and sympy__sympy-17630_fvk_prompt.md
  (structural cross-check). Copies + sha256s + every structural divergence:
  prompts/agentic/source/PROVENANCE.md.
deviations:
  - >
    (a) FVK comes from the local workspace copy formal-verification-kit/ instead of
    the web: the Instance-section kit line points at the local path instead of
    https://github.com/grosu/formal-verification-kit, and Phase 3 reads the staged
    kit instead of git-cloning it into fvk_repo/. Occurrences marked
    "DEVIATION (a)" in HTML comments.
  - >
    (b) Phase 0 verifies a pre-built workspace instead of creating one: the original
    Workspace Setup (mkdir under /home/openclaw, fetch the HF benchmark row via
    urllib into benchmark/ + private_eval/, git clone the repo) is replaced by a
    staged-layout listing plus "Phase 0: Verify the Pre-Built Environment" (repo/ at
    base_commit, ready .venv, benchmark/, scripts/private_eval.py);
    correspondingly Phase 2 runs the pre-staged scripts/private_eval.py instead of
    "official harness if available, else write a local private evaluator" (the
    original's five evaluator requirements are kept verbatim as the description of
    what scripts/private_eval.py does). The original Phase-0 intent — sanity-check
    that imports and tests run — is kept, with the setup-notes artifact
    (reports/setup_notes.md) from his sympy sample. Occurrences marked
    "DEVIATION (b)" in HTML comments.
  - >
    (c) The answer key is relocated out of the agent's workspace for measurement
    integrity: the full benchmark row (reference solution + hidden tests) is no longer
    staged at private_eval/swebench_row_full.json, so it is dropped from the staged
    layout and the original's "Do not manually open private_eval/swebench_row_full.json"
    rule is replaced by a faithful line stating that grading is done by
    scripts/private_eval.py, which reports only aggregate pass/fail counts and reads the
    reference solution and hidden tests from a location not present in this workspace.
    The evaluator is still invoked identically and the identical aggregate feedback that
    feeds v2 is preserved. Occurrence marked "DEVIATION (c)" in an HTML comment.
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
  - regression_note
  - public_issue_gist
  - likely_files_block
  - instance_questions_block
  - unrelated_behavior_bullet
---
# Prompt for Fresh Coding Agent: FVK Reproduction on `{instance_id}`

You are a fresh coding agent. Run a controlled Formal Verification Kit experiment on the SWE-bench Verified instance `{instance_id}`.

Your goal is to determine whether applying the Formal Verification Kit after an ordinary first patch improves, worsens, or does not change the result.

## Instance

- Dataset: `princeton-nlp/SWE-bench_Verified`
- Exact row URL: `{row_url}`
- Instance ID: `{instance_id}`
- Repository: `{repo_url}`
- Base commit: `{base_commit}`
- Base commit URL: `{base_commit_url}`
- {repo_title} version: `{version}`
- Difficulty: `{difficulty}`
<!-- DEVIATION (a): the original line pointed at https://github.com/grosu/formal-verification-kit;
the kit is staged locally in this workspace instead. -->
- Formal Verification Kit: `formal-verification-kit/` (staged locally in this workspace)

Known evaluator shape:

- `FAIL_TO_PASS`: {fail_to_pass_count} tests
- `PASS_TO_PASS`: {pass_to_pass_count} tests
- Official resolution criterion: resolved iff `FAIL_TO_PASS = {fail_to_pass_count}/{fail_to_pass_count}` and `PASS_TO_PASS = {pass_to_pass_count}/{pass_to_pass_count}`.

{regression_note}

## Benchmark Discipline

These rules are mandatory.

1. You may use only public information for patch generation:
   - the public issue statement;
   - the base repository at the base commit;
   - existing public tests already present in the repository;
   - the Formal Verification Kit.
2. Do not inspect or use the gold `patch` field.
3. Do not manually inspect or use the hidden `test_patch` field.
4. Do not inspect hidden test names, hidden assertions, or hidden failure traces.
5. Do not search for the original {repo_title} PR or solution for this issue.
6. A private evaluator may mechanically read `test_patch`, `FAIL_TO_PASS`, and `PASS_TO_PASS`, but it must print only aggregate counts.
7. Before producing v2, you may look only at the aggregate v1 score:
   - `FAIL_TO_PASS: A / {fail_to_pass_count}`
   - `PASS_TO_PASS: B / {pass_to_pass_count}`
   - `resolved: true/false`
8. Do not use private evaluator logs or hidden failure traces to guide v2.

## Workspace Setup

<!-- DEVIATION (b): the original created the workspace (mkdir under /home/openclaw), fetched
the benchmark row from the HuggingFace datasets server into benchmark/ + private_eval/ via an
inline urllib script, and cloned the repository at the base commit. This run pre-builds the
workspace: the same files are already staged, and a Phase 0 verifies the environment instead
of creating it. The formal-verification-kit/ entry in the listing below is
deviation (a): the kit is staged locally instead of cloned from GitHub. -->
Your current working directory is a pre-built workspace staged with:

    benchmark/PROMPT.md                  # public instance fields + problem statement
    benchmark/public_instance.json       # public fields only
    scripts/private_eval.py              # aggregate-only private evaluator
    repo/                                # {repo} checked out at the base commit
    .venv/                               # ready Python environment with repo/ installed
    formal-verification-kit/             # local copy of the Formal Verification Kit

Use or create: `patches/`, `reports/`, `fvk/`.

<!-- DEVIATION (c): the original staged the full benchmark row at
private_eval/swebench_row_full.json and said "Do not manually open
private_eval/swebench_row_full.json. It contains private benchmark fields." The answer key
(reference solution + hidden tests) is relocated out of this workspace for measurement
integrity; the line below replaces that rule. -->
Grading is performed by `scripts/private_eval.py`, which reports only aggregate pass/fail counts; the reference solution and hidden tests are not available in this workspace.

## Phase 0: Verify the Pre-Built Environment

<!-- DEVIATION (b), continued: replaces the original's fetch-and-clone steps with verification
of the pre-built environment, keeping the original intent of sanity-checking that imports and
tests run before Phase 1. -->
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

## Phase 1: Generate v1 Without FVK

Read only:

- `benchmark/PROMPT.md`
- source files under `repo/`
- existing public tests already present under `repo/`

{likely_files_block}{public_issue_gist}

Generate an ordinary first patch, v1, using only public information.

Do not use FVK yet.

You may run public tests already present in the repo.

When v1 is complete, save it:

    cd repo
    git diff > ../patches/solution_v1.patch
    cd ..

Write `reports/v1_notes.md` explaining:

- what behavior v1 changes;
- what files v1 modifies;
- what public tests you ran;
- why v1 appears to match the public issue statement.

## Phase 2: Evaluate v1 Privately

<!-- DEVIATION (b), continued: the original said "Use the official SWE-bench harness if
available." and, failing that, to write a local private evaluator meeting the five
requirements below. The pre-built workspace stages exactly that evaluator as
scripts/private_eval.py; run it instead. The five requirements are kept verbatim as the
description of what it does. -->
Evaluate with the pre-staged private evaluator:

    .venv/bin/python scripts/private_eval.py patches/solution_v1.patch v1

`scripts/private_eval.py` is a local private evaluator that:

1. creates a fresh checkout of {repo_title} at the base commit;
2. applies `patches/solution_v1.patch`;
3. mechanically applies the hidden `test_patch` from `private_eval/swebench_row_full.json`;
4. mechanically runs the evaluator tests;
5. prints only aggregate counts.

The evaluator may use private benchmark fields mechanically, but it must not print or expose:

- hidden test names;
- hidden assertions;
- hidden failure traces;
- hidden `test_patch` content;
- gold patch content.

Record only aggregate results in `reports/v1_score.md`:

    # v1 Score

    FAIL_TO_PASS: A / {fail_to_pass_count}
    PASS_TO_PASS: B / {pass_to_pass_count}
    Resolved: true/false

## Phase 3: Apply the Formal Verification Kit

<!-- DEVIATION (a): the original cloned https://github.com/grosu/formal-verification-kit.git
into fvk_repo/ here. The kit is staged locally at formal-verification-kit/ instead; the four
files read below are the same files the original read, at the local path. -->
The Formal Verification Kit is staged locally at `formal-verification-kit/`. Do not fetch it from the web.

Read:

- `formal-verification-kit/README.md`
- `formal-verification-kit/AGENTS.md`
- `formal-verification-kit/commands/formalize.md`
- `formal-verification-kit/commands/verify.md`

If `/formalize` and `/verify` slash commands exist in your environment, use them.

If they do not exist, manually follow the workflows in:

- `formal-verification-kit/commands/formalize.md`
- `formal-verification-kit/commands/verify.md`

Allowed FVK inputs:

- `benchmark/PROMPT.md`
- {repo_title} repo at the base commit
- `patches/solution_v1.patch`
- relevant public {repo_title} source files
- existing public tests
- `reports/v1_notes.md`
- `reports/v1_score.md`, aggregate counts only

Forbidden FVK inputs:

- gold patch
- hidden `test_patch` content
- hidden test names
- hidden assertions
- hidden failure traces
- private evaluator logs

FVK must not silently repair the code. It should accumulate findings and guidance.

Because this task has {fail_to_pass_count} bug tests and {pass_to_pass_count} regression tests, FVK must explicitly include non-regression obligations. Do not only formalize the desired new behavior. Also formalize what must remain unchanged.

Write these artifacts:

- `fvk/SPEC.md`
- `fvk/FINDINGS.md`
- `fvk/PROOF_OBLIGATIONS.md`
- `fvk/ITERATION_GUIDANCE.md`

The FVK artifacts must answer:

1. What is the intended public behavior change?
{instance_questions_block}
8. What did v1 get right?
9. What is v1 missing or overgeneralizing?
10. What exact minimal changes are justified for v2?
11. What changes are forbidden because they risk regressions?

## Phase 4: Generate v2 Using FVK Guidance

Use only:

- `fvk/SPEC.md`
- `fvk/FINDINGS.md`
- `fvk/PROOF_OBLIGATIONS.md`
- `fvk/ITERATION_GUIDANCE.md`
- `benchmark/PROMPT.md`
- public repo source files
- `patches/solution_v1.patch`
- `reports/v1_score.md`, aggregate counts only

Do not use:

- gold patch
- hidden `test_patch` content
- hidden test names
- hidden assertions
- hidden failure traces
- private evaluator logs

Modify `repo/` to produce v2.

Be conservative:

- prefer minimal changes;
- avoid broad refactors;
- {unrelated_behavior_bullet}
- preserve public regression behavior unless the issue explicitly requires changing it.

When v2 is complete, save it:

    cd repo
    git diff > ../patches/solution_v2.patch
    cd ..

Write `reports/v2_notes.md` explaining:

- how v2 differs from v1;
- which FVK findings caused the change;
- what regression risks v2 is designed to avoid.

## Phase 5: Evaluate v2 Privately

Use the same evaluator as v1.

Record only aggregate results in `reports/v2_score.md`:

    # v2 Score

    FAIL_TO_PASS: A' / {fail_to_pass_count}
    PASS_TO_PASS: B' / {pass_to_pass_count}
    Resolved: true/false

Do not inspect hidden test names, assertions, failure traces, or private logs.

## Final Report

Write `reports/final_report.md` with this structure:

    # FVK SWE-bench Experiment: {instance_id}

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

    ## Evaluator Shape

    - FAIL_TO_PASS: {fail_to_pass_count}
    - PASS_TO_PASS: {pass_to_pass_count}
    - Official resolved condition: {fail_to_pass_count}/{fail_to_pass_count} FAIL_TO_PASS and {pass_to_pass_count}/{pass_to_pass_count} PASS_TO_PASS

    ## Benchmark Discipline

    - Gold patch inspected: yes/no
    - Hidden test_patch manually inspected: yes/no
    - Hidden test names inspected: yes/no
    - Hidden assertions inspected: yes/no
    - Hidden failure traces inspected: yes/no
    - Private evaluator logs used for v2: yes/no

    ## Public Problem Summary

    Summarize the public issue.

    ## v1 Patch

    - Files changed:
    - Behavioral change:
    - Public tests run:

    ## v1 Score

    FAIL_TO_PASS: A / {fail_to_pass_count}
    PASS_TO_PASS: B / {pass_to_pass_count}
    Resolved: true/false

    ## FVK Artifacts

    - fvk/SPEC.md
    - fvk/FINDINGS.md
    - fvk/PROOF_OBLIGATIONS.md
    - fvk/ITERATION_GUIDANCE.md

    ## Key FVK Findings

    List the findings that influenced v2.

    ## v2 Patch

    - Files changed:
    - Behavioral change:
    - Difference from v1:
    - Why this follows from FVK:

    ## v2 Score

    FAIL_TO_PASS: A' / {fail_to_pass_count}
    PASS_TO_PASS: B' / {pass_to_pass_count}
    Resolved: true/false

    ## Delta

    FAIL_TO_PASS delta: A' - A
    PASS_TO_PASS delta: B' - B
    Resolved delta: improved / worsened / unchanged

    ## Did FVK Help?

    Answer directly:

    1. Did v2 improve the bug-revealing tests?
    2. Did v2 preserve regressions better or worse than v1?
    3. Did v2 get a worse total score?
    4. If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?
    5. Was the v2 change justified by the FVK artifacts?
    6. Did FVK overgeneralize the desired behavior?
    7. What should be changed in the FVK process for regression-heavy SWE-bench tasks?

    ## Artifacts

    - patches/solution_v1.patch
    - patches/solution_v2.patch
    - reports/v1_notes.md
    - reports/v1_score.md
    - reports/v2_notes.md
    - reports/v2_score.md
    - reports/final_report.md

## Final Response

Return only this summary:

    v1:
      FAIL_TO_PASS: A / {fail_to_pass_count}
      PASS_TO_PASS: B / {pass_to_pass_count}
      resolved: true/false

    v2:
      FAIL_TO_PASS: A' / {fail_to_pass_count}
      PASS_TO_PASS: B' / {pass_to_pass_count}
      resolved: true/false

    delta:
      FAIL_TO_PASS: A' - A
      PASS_TO_PASS: B' - B
      v2 better/worse/same:
      reason:

    benchmark discipline:
      preserved: yes/no
      notes:

    artifacts:
      solution_v1.patch: <path>
      solution_v2.patch: <path>
      FVK artifacts: <path>
      final_report.md: <path>

Do not include hidden test names, hidden assertions, hidden failure traces, hidden patch contents, or the gold solution.
