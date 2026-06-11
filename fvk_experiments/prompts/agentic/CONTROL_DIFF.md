# fvk-replicate vs review-control — template diff

Rationale (5 lines):
1. The control isolates WHAT Phase 3 injects (FVK vs plain expert review) while holding the 5-phase protocol, workspace, discipline, and aggregate-only feedback constant.
2. Everything outside Phase 3 and the FVK-naming lines is byte-identical, so any outcome delta attributes to the review-vs-FVK content, not to prompt drift.
3. Phase 3 swaps kit reading + /formalize + /verify for a disciplined plain-English review with an EXPLICIT non-regression check ("identify what must remain unchanged, and verify the patch does not alter it").
4. Artifacts shrink from fvk/{SPEC,FINDINGS,PROOF_OBLIGATIONS,ITERATION_GUIDANCE}.md to review/{FINDINGS,ITERATION_GUIDANCE}.md; Phase 4's allowed-inputs list changes correspondingly and nothing else.
5. The 11-question checklist, conservatism rules, score formats, and report scaffolding are shared verbatim, so both arms answer the same questions about the same v1 under the same rules.

Diff of the template BODIES as agents see them (frontmatter and HTML deviation
comments stripped; `{field}` placeholders unexpanded). Regenerate with
`.venv/bin/python fvk_experiments/scripts/build_agentic_previews.py`.

```diff
--- fvk-replicate.md
+++ review-control.md
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
     repo/                                # {repo} checked out at the base commit
     .venv/                               # ready Python environment with repo/ installed
-    formal-verification-kit/             # local copy of the Formal Verification Kit
-
-Use or create: `patches/`, `reports/`, `fvk/`.
+
+Use or create: `patches/`, `reports/`, `review/`.
 
 Grading is performed by `scripts/private_eval.py`, which reports only aggregate pass/fail counts; the reference solution and hidden tests are not available in this workspace.
 
@@ -77,7 +74,7 @@
 
 Record what you verified in `reports/setup_notes.md`. If something is broken, repair the environment without changing `repo/` source files, and note what you did.
 
-## Phase 1: Generate v1 Without FVK
+## Phase 1: Generate v1 Without Review
 
 Read only:
 
@@ -89,7 +86,7 @@
 
 Generate an ordinary first patch, v1, using only public information.
 
-Do not use FVK yet.
+Do not start the review yet.
 
 You may run public tests already present in the repo.
 
@@ -136,25 +133,27 @@
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
@@ -164,7 +163,7 @@
 - `reports/v1_notes.md`
 - `reports/v1_score.md`, aggregate counts only
 
-Forbidden FVK inputs:
+Forbidden review inputs:
 
 - gold patch
 - hidden `test_patch` content
@@ -173,18 +172,16 @@
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
@@ -193,14 +190,12 @@
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
@@ -233,7 +228,7 @@
 Write `reports/v2_notes.md` explaining:
 
 - how v2 differs from v1;
-- which FVK findings caused the change;
+- which review findings caused the change;
 - what regression risks v2 is designed to avoid.
 
 ## Phase 5: Evaluate v2 Privately
@@ -254,7 +249,7 @@
 
 Write `reports/final_report.md` with this structure:
 
-    # FVK SWE-bench Experiment: {instance_id}
+    # Review-Control SWE-bench Experiment: {instance_id}
 
     ## Benchmark
 
@@ -299,14 +294,12 @@
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
 
@@ -315,7 +308,7 @@
     - Files changed:
     - Behavioral change:
     - Difference from v1:
-    - Why this follows from FVK:
+    - Why this follows from the review:
 
     ## v2 Score
 
@@ -329,7 +322,7 @@
     PASS_TO_PASS delta: B' - B
     Resolved delta: improved / worsened / unchanged
 
-    ## Did FVK Help?
+    ## Did the Review Help?
 
     Answer directly:
 
@@ -337,9 +330,9 @@
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
 
@@ -378,7 +371,7 @@
     artifacts:
       solution_v1.patch: <path>
       solution_v2.patch: <path>
-      FVK artifacts: <path>
+      review artifacts: <path>
       final_report.md: <path>
 
 Do not include hidden test names, hidden assertions, hidden failure traces, hidden patch contents, or the gold solution.
```
