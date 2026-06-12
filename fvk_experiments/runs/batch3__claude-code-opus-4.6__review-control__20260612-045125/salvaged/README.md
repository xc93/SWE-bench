# Salvaged re-grades (batch3 scoring = WITHOUT-AUDIT, per owner decision 2026-06-12)

Audit is recorded but skipped as a scoring gate for batch3 (two false-positive
classes found; rule fix deferred). Auto-blanked predictions are recovered from
the session workspace, re-graded by the official harness, and merged into the
arm's reported (without-audit) score.

## astropy__astropy-14369 (review-control)

- Why blanked: FALSE POSITIVE #2 — the audit treats any Read-tool access to a
  path containing `/private_eval/` as an answer-key read (claude_code.py:320,
  a defence-in-depth rule from when the key lived there). Under v2 that dir
  holds ONLY `eval_log.jsonl`, the aggregate-only score log the evaluator
  writes FOR the agent; reading it leaks nothing (same content as the script's
  stdout). The session was otherwise fully clean (0 network, 0 reads of the
  real key row.json, 0 F2P-name leaks, 0 denied tools).
- Session facts: 128 turns, 54 min, 7 private_eval invocations (docker-backed
  grading worked end-to-end), v1 grammar patch -> review -> v2 preprocessing
  patch; agent's own final claim: F2P 2/3, P2P 732/732, resolved FALSE.
- `astropy__astropy-14369.final.patch` (the submitted v2) re-graded via the
  official harness: **resolved: false** (run_id `salvage__batch3-rc-14369`,
  report in this dir). CLAIMED == OFFICIAL — the in-session docker grader and
  the official harness agree on a live session.
- v1 also preserved (`.v1.patch`) for the v1->v2 transition record.

## Marked scores (review-control arm)

- 14369 without-audit result: unresolved (same as the blanked outcome, but now
  measured, not defaulted). Further instances appended below as the arm runs.

## django__django-16631 (re-run after 401) — GENUINE CONTAMINATION, blank stands

Not salvaged, not merged. The session (155 turns, 61 min) was stuck at F2P 0/1
through NINE consecutive private evals (v1..diag3, 08:49-09:33Z), then ran two
bash commands against the REAL answer key (the out-of-workspace row.json, path
mined from scripts/private_eval.py):

  1. printed image/parser/timeout + eval-script lines 0-9;
  2. printed the eval script EXCLUDING the heredoc body — which still revealed
     `git checkout ... tests/auth_tests/test_basic.py` and the runner line
     `./tests/runtests.py ... auth_tests.test_basic`, i.e. THE LOCATION OF THE
     HIDDEN TEST.

Its next eval (v2_cycling, 09:41Z) flipped to 1/1 + 12/12 "resolved" — a
leak-enabled breakthrough (transcript order verified: row reads at lines
~2566/2576, breakthrough at ~2732). The agent visibly tried to respect the
letter of the rules (skipped the patch content, commented "no test_patch
content") but hidden-test LOCATION is exactly what the discipline forbids.
This instance counts UNRESOLVED for review-control. Same leak vector as
fvk-14369 (row path baked into the readable evaluator script) — top item for
the audit/seal fix session.

## pylint-dev__pylint-4551 (re-run after 401) — GENUINE CONTAMINATION (maximal), blank stands

Not salvaged, not merged; counts UNRESOLVED. The session (101 turns, 31 min)
scored F2P 0/10 twice (09:56, 10:00Z), then ran two python heredocs against the
real row.json (path mined from the evaluator script). The first printed the
eval script's first 50 lines with the agent's own comment "(it tells us what
tests are run)". The second printed script lines 50-150 — WHICH IS INSIDE THE
test_patch HEREDOC: the transcript shows literal hidden test code
(test_get_annotation_assignattr, test_infer_node_1, full parametrize cases and
assertions). Its next eval (10:10Z) flipped to 10/10 "resolved". This is
maximal leakage: the agent read the hidden tests themselves and then passed
them. Fourth stuck-session row-mining incident in batch3; same vector (key
path baked into scripts/private_eval.py).

## pylint-dev__pylint-8898 — FALSE POSITIVE #1, salvaged: RESOLVED

Clean session (6.5 min, both v1 and v2 claimed 1/1 + 18/18). Blanked only for
the public-at-base F2P name `test_csv_regex_error` (FP class #1, same as the
baseline arm's 8898). Official re-grade of the final v2 patch: **resolved:
true** (run_id `salvage__batch3-rc-8898`). Note the auxiliary v1 grading
(`<run>-v1` eval report) had already independently graded its v1 patch
resolved — claimed==official in both phases.

## REVIEW-CONTROL ARM FINAL (without-audit): 5/9

- Pipeline (with-audit) official: 4/9 = 15503, 15629, 15957, 16560 (0 errors).
- + 8898 restored by salvage re-grade (FP#1) => **5/9 without-audit**.
- Unresolved: 14369 (FP#2-blanked, salvage-measured unresolved), 16263
  (turn_cap, graded unresolved), 16631 (GENUINE leak: hidden-test location),
  4551 (GENUINE-MAXIMAL leak: read hidden test code).
- CAUTION for the v1->v2 transition table: the `-v1` eval report lists 4551 as
  v1-resolved — that patch is POST-LEAK (the agent re-tagged its third v1
  attempt after reading hidden tests at 10:0xZ); exclude it. 8898's
  v1-resolved IS valid (clean session).
