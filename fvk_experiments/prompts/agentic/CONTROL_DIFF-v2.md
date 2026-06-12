# fvk-replicate-v2 vs review-control-v2 — template diff

Same rationale as CONTROL_DIFF.md (v1): the control isolates WHAT Phase 3
injects (FVK vs plain expert review) while holding everything else constant —
including the v2 Phase 0 (agent self-build env, Grigore's verbatim fallback
recipe) and the docker-grading disclosure on the deviation-(c) line, which are
byte-identical in both arms.

Diff of the template BODIES as agents see them (frontmatter and HTML deviation
comments stripped; `{field}` placeholders unexpanded). Regenerate with
`.venv/bin/python fvk_experiments/scripts/build_agentic_previews.py`.

```diff
--- fvk-replicate-v2.md
+++ review-control-v2.md
@@ -1,8 +1,8 @@
-# Prompt for Fresh Coding Agent: FVK Reproduction on `{instance_id}`
-
-You are a fresh coding agent. Run a controlled Formal Verification Kit experiment on the SWE-bench Verified instance `{instance_id}`.
-
-Your goal is to determine whether applying the Formal Verification Kit after an ordinary first patch improves, worsens, or does not change the result.
+# Prompt for Fresh Coding Agent: Review Control on `{instance_id}`
+
+You are a fresh coding agent. Run a controlled disciplined-code-review experiment on the SWE-bench Verified instance `{instance_id}`.
+
+Your goal is to determine whether applying a disciplined expert code review after an ordinary first patch improves, worsens, or does not change the result.
 
 ## Instance
 
@@ -14,7 +14,6 @@
 - Base commit URL: `{base_commit_url}`
 - {repo_title} version: `{version}`
 - Difficulty: `{difficulty}`
-- Formal Verification Kit: `formal-verification-kit/` (staged locally in this workspace)
 
 Known evaluator shape:
 
@@ -31,8 +30,7 @@
 1. You may use only public information for patch generation:
    - the public issue statement;
    - the base repository at the base commit;
-   - existing public tests already present in the repository;
-   - the Formal Verification Kit.
+   - existing public tests already present in the repository.
 2. Do not inspect or use the gold `patch` field.
 3. Do not manually inspect or use the hidden `test_patch` field.
 4. Do not inspect hidden test names, hidden assertions, or hidden failure traces.
@@ -53,9 +51,8 @@
     scripts/private_eval.py              # aggregate-only private evaluator
     repo/                                # {repo} checked out at the base commit (truncated history, no remote)
     .venv/                               # MAY be pre-staged (hard compiled-deps only); otherwise you create it in Phase 0
-    formal-verification-kit/             # local copy of the Formal Verification Kit
-
-Use or create: `patches/`, `reports/`, `fvk/`.
+
+Use or create: `patches/`, `reports/`, `review/`.
 
 Grading is performed by `scripts/private_eval.py`, which reports only aggregate pass/fail counts; the reference solution and hidden tests are not available in this workspace. Its scores are computed inside the instance's official SWE-bench evaluation environment, so they match the official grader.
 
@@ -89,7 +86,7 @@
 
 Record what you did and verified in `reports/setup_notes.md`. You are encouraged to run public tests under `repo/` locally and freely throughout this task — building, running, and iterating against the repo's own tests is expected. Do not modify `repo/` source files during setup; only change source as part of your patch in Phases 1 and 4.
 
-## Phase 1: Generate v1 Without FVK
+## Phase 1: Generate v1 Without Review
 
 Read only:
 
@@ -101,7 +98,7 @@
 
 Generate an ordinary first patch, v1, using only public information.
 
-Do not use FVK yet.
+Do not start the review yet.
 
 You may run public tests already present in the repo.
 
@@ -148,25 +145,27 @@
     PASS_TO_PASS: B / {pass_to_pass_count}
     Resolved: true/false
 
-## Phase 3: Apply the Formal Verification Kit
-
-The Formal Verification Kit is staged locally at `formal-verification-kit/`. Do not fetch it from the web.
+## Phase 3: Review the v1 Patch
+
+Perform a disciplined, expert code review of the v1 patch, in plain English.
 
 Read:
 
-- `formal-verification-kit/README.md`
-- `formal-verification-kit/AGENTS.md`
-- `formal-verification-kit/commands/formalize.md`
-- `formal-verification-kit/commands/verify.md`
-
-If `/formalize` and `/verify` slash commands exist in your environment, use them.
-
-If they do not exist, manually follow the workflows in:
-
-- `formal-verification-kit/commands/formalize.md`
-- `formal-verification-kit/commands/verify.md`
-
-Allowed FVK inputs:
+- `benchmark/PROMPT.md`
+- `patches/solution_v1.patch`
+- the public source files the patch touches, and their callers
+- existing public tests near the touched code
+
+Hunt for:
+
+- bugs in the patch as written;
+- edge cases and inputs the patch handles incorrectly or not at all;
+- incompleteness relative to the public issue statement;
+- overreach: changes the public issue does not ask for.
+
+Explicitly check non-regression: identify what must remain unchanged, and verify the patch does not alter it.
+
+Allowed review inputs:
 
 - `benchmark/PROMPT.md`
 - {repo_title} repo at the base commit
@@ -176,7 +175,7 @@
 - `reports/v1_notes.md`
 - `reports/v1_score.md`, aggregate counts only
 
-Forbidden FVK inputs:
+Forbidden review inputs:
 
 - gold patch
 - hidden `test_patch` content
@@ -185,18 +184,16 @@
 - hidden failure traces
 - private evaluator logs
 
-FVK must not silently repair the code. It should accumulate findings and guidance.
-
-Because this task has {fail_to_pass_count} bug tests and {pass_to_pass_count} regression tests, FVK must explicitly include non-regression obligations. Do not only formalize the desired new behavior. Also formalize what must remain unchanged.
+The review must not silently repair the code. It should accumulate findings and guidance.
+
+Because this task has {fail_to_pass_count} bug tests and {pass_to_pass_count} regression tests, the review must explicitly include non-regression checks. Do not only review the desired new behavior. Also state what must remain unchanged.
 
 Write these artifacts:
 
-- `fvk/SPEC.md`
-- `fvk/FINDINGS.md`
-- `fvk/PROOF_OBLIGATIONS.md`
-- `fvk/ITERATION_GUIDANCE.md`
-
-The FVK artifacts must answer:
+- `review/FINDINGS.md`
+- `review/ITERATION_GUIDANCE.md`
+
+The review artifacts must answer:
 
 1. What is the intended public behavior change?
 {instance_questions_block}
@@ -205,14 +202,12 @@
 10. What exact minimal changes are justified for v2?
 11. What changes are forbidden because they risk regressions?
 
-## Phase 4: Generate v2 Using FVK Guidance
+## Phase 4: Generate v2 Using Review Guidance
 
 Use only:
 
-- `fvk/SPEC.md`
-- `fvk/FINDINGS.md`
-- `fvk/PROOF_OBLIGATIONS.md`
-- `fvk/ITERATION_GUIDANCE.md`
+- `review/FINDINGS.md`
+- `review/ITERATION_GUIDANCE.md`
 - `benchmark/PROMPT.md`
 - public repo source files
 - `patches/solution_v1.patch`
@@ -245,7 +240,7 @@
 Write `reports/v2_notes.md` explaining:
 
 - how v2 differs from v1;
-- which FVK findings caused the change;
+- which review findings caused the change;
 - what regression risks v2 is designed to avoid.
 
 ## Phase 5: Evaluate v2 Privately
@@ -266,7 +261,7 @@
 
 Write `reports/final_report.md` with this structure:
 
-    # FVK SWE-bench Experiment: {instance_id}
+    # Review-Control SWE-bench Experiment: {instance_id}
 
     ## Benchmark
 
@@ -311,14 +306,12 @@
     PASS_TO_PASS: B / {pass_to_pass_count}
     Resolved: true/false
 
-    ## FVK Artifacts
-
-    - fvk/SPEC.md
-    - fvk/FINDINGS.md
-    - fvk/PROOF_OBLIGATIONS.md
-    - fvk/ITERATION_GUIDANCE.md
-
-    ## Key FVK Findings
+    ## Review Artifacts
+
+    - review/FINDINGS.md
+    - review/ITERATION_GUIDANCE.md
+
+    ## Key Review Findings
 
     List the findings that influenced v2.
 
@@ -327,7 +320,7 @@
     - Files changed:
     - Behavioral change:
     - Difference from v1:
-    - Why this follows from FVK:
+    - Why this follows from the review:
 
     ## v2 Score
 
@@ -341,7 +334,7 @@
     PASS_TO_PASS delta: B' - B
     Resolved delta: improved / worsened / unchanged
 
-    ## Did FVK Help?
+    ## Did the Review Help?
 
     Answer directly:
 
@@ -349,9 +342,9 @@
     2. Did v2 preserve regressions better or worse than v1?
     3. Did v2 get a worse total score?
     4. If v2 got worse, was it because of FAIL_TO_PASS, PASS_TO_PASS, or both?
-    5. Was the v2 change justified by the FVK artifacts?
-    6. Did FVK overgeneralize the desired behavior?
-    7. What should be changed in the FVK process for regression-heavy SWE-bench tasks?
+    5. Was the v2 change justified by the review artifacts?
+    6. Did the review overgeneralize the desired behavior?
+    7. What should be changed in the review process for regression-heavy SWE-bench tasks?
 
     ## Artifacts
 
@@ -390,7 +383,7 @@
     artifacts:
       solution_v1.patch: <path>
       solution_v2.patch: <path>
-      FVK artifacts: <path>
+      review artifacts: <path>
       final_report.md: <path>
 
 Do not include hidden test names, hidden assertions, hidden failure traces, hidden patch contents, or the gold solution.
```
