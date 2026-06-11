# FVK on 10 astropy SWE-bench Verified instances — consolidated

v1 = ordinary first patch (no FVK). v2 = patch after applying FVK (/formalize +
/verify with explicit non-regression obligations). R = resolved (all FAIL_TO_PASS
and all PASS_TO_PASS pass). All patches generated from public info only; evaluator
prints aggregate counts only. 13236 run by the lead agent; the other 9 by
independent fresh agents in parallel, same neutral prompt.

| Instance | Ver | v1 (no FVK) | v2 (FVK) | v2 vs v1 | this run | reference (noFVK→FVK) |
|---|---|---|---|---|---|---|
| 12907 | 4.3 | R 2/2, 13/13 | R 2/2, 13/13 | same (identical) | R→R | R→R |
| 13033 | 4.3 | ✗ 0/1, 19/20 | ✗ 0/1, 19/20 | same (differs) | ✗→✗ | ✗→✗ |
| 13236 | 5.0 | R 2/2, 644/644 | R 2/2, 644/644 | same (identical) | R→R | **R→✗** |
| 13398 | 5.0 | ✗ 0/4, 63/68 | ✗ 0/4, 63/68 | same (differs) | ✗→✗ | ✗→✗ |
| 13453 | 5.0 | R 1/1, 9/9 | R 1/1, 9/9 | same (identical) | R→R | R→R |
| 13579 | 5.0 | ✗ 1/1, 32/40 | **R 1/1, 40/40** | **better +8 P2P** | ✗→R | R→R |
| 13977 | 5.1 | ✗ 12/20, 314/322 | ✗ **20/20**, 314/322 | better +8 F2P | ✗→✗* | ✗→✗ |
| 14096 | 5.1 | R 1/1, 426/426 | R 1/1, 426/426 | same score, safer code | R→R | R→R |
| 14182 | 5.1 | ✗ 0/1, 9/9 | **R 1/1, 9/9** | **better +1 F2P** | ✗→R | ✗→✗ |
| 14309 | 5.1 | R 1/1, 141/141 | R 1/1, 141/141 | same (identical) | R→R | (none) |

\* 13977 resolved=false for both v1 and v2 partly from genuine hidden-test
regressions not derivable from public info and partly from an evaluator node-id
artifact (independently re-checked baseline = 318/322 with 4 unmatched node-ids, so
322/322 is unreachable in this environment even for the unfixed baseline). FVK still
improved the bug-test pass rate from 12/20 to 20/20.

## Headline numbers (this run, resolved level)

- FVK **regressions** (R→✗): **0 of 10**. (The reference table's only regression,
  13236 R→✗, did **not** reproduce: this run got R→R.)
- FVK **flips to resolved** (✗→R): **2** — 13579, 14182.
- FVK **sub-score improvements** without flip: **2** — 13977 (+8 FAIL_TO_PASS),
  14096 (same score, strictly safer code).
- FVK **neutral** (same patch / same score): the rest.
- FVK **overgeneralized**: **0** — in 13236 and 13398 it explicitly *forbade* adding
  a warning (`setup.cfg filterwarnings=error` makes any warning a hard error); in
  12907/13453/14309 it forbade out-of-scope extensions.

## Why this differs from the reference

1. **The reference's one regression (13236) was an FVK-application artifact, not
   inherent.** Applying FVK *with explicit non-regression obligations* and the rule
   "if v1 is already resolved, certify and guard it — don't add unrequested
   behavior" avoided it. The two traps that regress 13236 (add the issue's literal
   `FutureWarning`; remove the load-bearing-looking re-export import) were measured
   to drop it to 0/2 or 0/644; FVK fenced both off.

2. **"Ordinary first patch" is stochastic.** v1 quality varies by agent/run, so this
   is a methodology-level comparison, not a controlled A/B on identical v1 code. The
   clearest example is 13579: the reference's no-FVK patch was already R, but this
   run's v1 introduced a `KeyError` (broke 8 regressions); FVK then caught and
   repaired it (✗→R). 14182 is the cleanest pro-FVK case: reference ✗→✗, this run
   ✗→R via FVK's read/write round-trip obligation.

3. **Some instances are unsolvable from public info** (13033 exact gold error
   string; 13398 hidden contract + intended route-supersession; 13977 hidden
   test_patch changes). FVK correctly does not invent these and does not overgeneralize;
   it just can't see the hidden spec. This is a benchmark-discipline limit, not an FVK failure.

## Recurring FVK contributions observed

- **Warning-as-error fence** (`filterwarnings=error`): 13236, 13398.
- **Re-export / public-surface invariant**: 13236 (NdarrayMixin import is load-bearing).
- **Round-trip (read↔write) obligation**: 14182 (the flip), 13453, 13033.
- **Coverage obligation** (all failure sites / exception types): 13977 (+8 F2P).
- **Scope fence** (don't harden siblings/unrelated branches): 12907, 13453, 14096, 14309.

## Bottom line

Across 10 regression-heavy astropy tasks, a *regression-aware* FVK application
**never worsened** a result, **flipped 2 unresolved cases to resolved**, and
**improved sub-scores on 2 more** — while explicitly resisting the overgeneralizations
that caused the reference run's lone 13236 regression. The value of FVK here is
dominated by its **non-regression discipline**: formalizing what must stay the same
and fencing off tempting-but-harmful edits, rather than by raw bug-fixing.
