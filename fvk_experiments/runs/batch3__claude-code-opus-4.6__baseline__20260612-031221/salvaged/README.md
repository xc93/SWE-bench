# Salvaged re-grades (batch3 scoring = WITHOUT-AUDIT, per owner decision 2026-06-12)

Owner decision for batch3: the transcript audit is recorded but SKIPPED AS A
SCORING GATE (a false-positive class was found in its F2P-name rule; the rule
fix is deferred to a separate session). Any prediction the pipeline auto-blanked
is recovered from the session workspace and re-graded by the official harness,
and that result IS MERGED into the arm's reported (without-audit) score.

## pylint-dev__pylint-8898 (baseline)

- Why blanked: audit flagged `test_csv_regex_error` as a hidden-name leak.
  VERIFIED FALSE POSITIVE: that test exists publicly at the base commit
  (tests/config/test_config.py:134); the instance's hidden test_patch modifies
  the existing test rather than adding one, so reading the public test suite
  (allowed) inevitably trips the rule. Session was otherwise fully clean
  (0 network, 0 answer-key reads, 0 denied-tool attempts).
- `pylint-dev__pylint-8898.solution.patch` = the agent's final patch (from its
  workspace), re-graded via the official harness: **resolved: true**
  (run_id `salvage__batch3-baseline-8898`, report in this dir, 0 errors).

## Marked scores (baseline arm)

- **batch3 reported score (without-audit): 3/9**
- pipeline output with audit gate (report.md / eval dir): 2/9 — kept unchanged
  as provenance of what the frozen pipeline did.

At-risk instances identified by the base-commit scan (F2P names public at base):
8898 (1/1), astropy-14369 (3/3, parametrized), pylint-4551 (6/10). Phased arms
get the same salvage+merge treatment if their sessions are auto-blanked.
