# FVK prompt changelog

## agentic baseline — 2026-06-11 (`../agentic/baseline.md`, tag `baseline`)

Single-pass control for the agentic family: read `benchmark/PROMPT.md` + `repo/`,
produce one best-effort patch at `patches/solution.patch`, brief final report.
Same instance metadata, same pre-built workspace, and the **same shared ground
rules as the other two arms** (public info only; no gold patch; no hidden tests;
no web lookup of the original fix/PR/issue) — but **no phases, no review, no
evaluator**.

**Revised 2026-06-11 (info-parity cleanup; not yet run).** Per the shared
locked-answer-key contract the full benchmark row is not staged and the baseline
has no evaluator, so all references to `private_eval/`, `swebench_row_full.json`,
and `scripts/private_eval.py` were removed (the old "do not run the evaluator" /
"do not open the row" prohibitions are gone — there is nothing to prohibit). Net:
a clean single-pass arm with the same ground rules as the other two arms, just no
review/eval/phases.

## agentic review-control — 2026-06-11 (`../agentic/review-control.md`, tag `review-control`)

Control arm for `fvk-replicate.md` (the agentic analogue of v5-vs-v4): identical
5-phase protocol, workspace, discipline, aggregate-only feedback, conservatism
rules, 11-question checklist, and report scaffolding — but Phase 3 is a
**disciplined plain-English expert code review** of the v1 patch with an explicit
non-regression check ("identify what must remain unchanged, and verify the patch
does not alter it"), writing `review/FINDINGS.md` + `review/ITERATION_GUIDANCE.md`
instead of the four `fvk/` artifacts; Phase 4's allowed inputs updated accordingly.
Zero FVK/formal-methods/kit references (test-enforced). Exact divergence:
`../agentic/CONTROL_DIFF.md`.

**Revised 2026-06-11 (not yet run).** Inherits the new deviation (c) from the
replicate template (answer key relocated out of the workspace: the full row is not
staged, and the "Do not manually open ..." rule is replaced by the aggregate-only
grading line). The grading line is byte-identical in both arms, so it stays a
shared context line in `CONTROL_DIFF.md` and does not perturb the comparison. The
reconstructed-instance changes below (empty likely-files + provenance marker) apply
to this arm too.

## agentic fvk-replicate — 2026-06-11 (`../agentic/fvk-replicate.md`, tag `fvk-replicate`)

First **agentic** prompt: a per-instance `{field}` template reversed from Grigore
Rosu's verbatim `astropy_13236_fvk_prompt.md` (Telegram "Fast Verification
Positioning", 2026-06-10; copies + sha256s + sympy cross-sample divergences in
`../agentic/source/PROVENANCE.md`). One Claude Code session per instance runs his
5-phase protocol: Phase 0 env check → v1 patch (public info only) → aggregate-only
private eval → FVK (`/formalize`+`/verify`, findings + proof obligations, explicit
non-regression) → v2 from findings + v1 aggregate score → re-eval + final report.
17 per-instance fields (4 of them curated to his exact 13236 wording —
`fvk_bench/agentic_prompts.py`). Three declared deviations, HTML-comment-marked:
(a) kit read from the staged local `formal-verification-kit/` instead of
git-cloning from GitHub; (b) pre-built workspace (repo/ at base_commit, ready
.venv, staged benchmark/, `scripts/private_eval.py`) verified in Phase 0 instead of
fetched/cloned, and Phase 2 runs the staged evaluator; (c) answer key relocated out
of the agent workspace (the full row is not staged, and the "Do not manually open
private_eval/swebench_row_full.json" rule is replaced by a line stating that
`scripts/private_eval.py` reports only aggregate counts and the reference solution
and hidden tests are not in the workspace). Fidelity is test-frozen: instantiating
for `astropy__astropy-13236` reproduces his file byte-for-byte except the frozen
deviation hunks (`tests/test_agentic_prompts.py` +
`tests/fixtures/astropy_13236_residual.diff`).

**Revised 2026-06-11 (not yet run).** Added deviation (c) above (locked answer key,
mirroring the runner workstream that relocated the full row out of the workspace).
Also: **only `astropy__astropy-13236` is verbatim**; the other 9 pinned instances
are RECONSTRUCTIONS auto-generated from the public issue — they now carry **no
likely-files hint** (`{likely_files_block}` is empty; the "Likely relevant public
files include:" block belongs to the curated 13236 prompt only) and are stamped with
a provenance HTML comment near the top (`RECONSTRUCTED PROMPT: ... Only astropy-13236
is verbatim.`), archived in the saved prompt but identical across arms (so it cancels
in the comparison). Added by `agentic_prompts.render()`, the shared runner/preview
entry point. Instantiated previews for all 10 pinned instances × 3 arms:
`../agentic/preview/` (regenerate via `scripts/build_agentic_previews.py`).

## v7 — 2026-06-10 (no prompt file; arm `baseline-replicate-v7`)

Not a prompt: an independent **replicate of the pro baseline** (oracle prompt only, no
system message) to measure run-to-run sampling variance behind all the pair deltas.
Implemented via the config-level `tag:` override
(`configs/astropy10__v4-pro__baseline-replicate-v7.yaml`); the original baseline run
and its numbers are untouched.

## v5 — 2026-06-10 (`v5.md`, tag `review-v5`)

**Control arm for v4** — the same fully-automatic draft → critique → regenerate
three-phase structure, but Phase 2 is a plain careful code review (correctness trace,
edge cases, regressions, intent fit, consistency) with zero FVK/formal-methods content.
Any v4 − v5 delta isolates the FVK content from the structure; any v5 − baseline delta
measures the structure itself. Frontmatter `tag: review-v5` keeps run labels honest
(this is not an fvk-* arm).

## v4 — 2026-06-10 (`v4.md`)

Draft-first FVK loop, fully automatic in one response: **(1) DRAFT** a candidate fix
`c`, **(2) FVK it** — emulate `/formalize` (intended contracts, generalized loop
claims, circularities, boundary list) then `/verify` ON `c` (path walk, claim
discharge with guardedness, side conditions, termination measure, repro case),
recording findings, **(3) REGENERATE** the final fix from the findings and re-verify
before emitting the patch. "The kit, in brief" section reused verbatim from v1
(already fidelity-checked); same kit commit `d0d07ba`. Differs from v1 in being
draft-first (v1 is spec-first: formalize → verify → patch with no committed draft).

## v3 — 2026-06-10 (`v3.md`)

No distillation: the **entire kit repo verbatim** — all 117 files (806,655 chars,
~212k tokens) at the same pinned commit `d0d07ba`, concatenated with per-file
`========== FILE: <path> ==========` headers behind a thin one-shot adaptation wrapper
(no toolchain/slash commands/artifact files — emulate inline; FORMALIZE → VERIFY →
PATCH order preserved from v1/v2; task output-format instructions take precedence).
Generated mechanically and reproducibly by `scripts/build_v3_verbatim.py` reading the
vendored submodule via `git show` — no LLM in the loop, so no fidelity risk.
Fits easily in DeepSeek V4's 1M context; relies on prefix caching for cost.

## v2 — 2026-06-10 (`v2.md`)

Comprehensive ~10k-token distillation (36.9k chars vs v1's 6.4k) from the same kit
commit `d0d07ba`, read via `git show` from the vendored submodule clone. Includes
essentially everything in the kit **except** the report/findings machinery, tool
invocation (kompile/krun/kprove), and the examples/ library:

- Part I — full K knowledge base: K framework + configurations/cells, matching logic
  (patterns, definedness ladder, mu-logic fixpoints), rewrite rules + heating/cooling,
  reachability claims as specs, function contracts, invariants as generalized loop
  claims with soundness side conditions, the seven-rule reachability proof system,
  circularities + guardedness, nested loops/recursion, two-tier VC discharge with
  `[simplification]` lemmas, lists/spec-only abstractions, partial correctness +
  termination, escalation discipline.
- Part II — the v1 three-step procedure (FORMALIZE → VERIFY → PATCH) enriched to demand
  actual K-style claims and hand-executed symbolic verification.

Produced by a 7-agent workflow (4 parallel cluster extracts → assembly on the v1
skeleton → coverage+size and fidelity critics, both PASS); 3 minor fidelity fixes
applied editorially (strict(2) gloss, definedness-braced naming, ensures/post-store
phrasing).

## v1 — 2026-06-10 (`v1.md`)

Initial distillation from [grosu/formal-verification-kit](https://github.com/grosu/formal-verification-kit)
@ `d0d07ba`, produced by an 8-agent workflow (repo map → 4 parallel cluster extracts →
synthesis → completeness + fidelity critics, both PASS → finalize). Four minor critic
findings applied editorially before freezing:

1. "(terminating)" qualifier + partial-correctness caveat, and an explicit
   termination-measure check in VERIFY (a diverging fix must not pass).
2. Loop-claim discharge phrased in the kit's reachability-claim terms instead of the
   classical Hoare invariant trio the kit positions itself against.
3. "overflow" restored to the kit's canonical boundary-condition list.
4. Intro qualified so "visible answer" cannot be read as overriding patch-only output
   instructions.

Design intent: the target model has no K toolchain or kit files, so the prompt makes it
*emulate* `/formalize` → `/verify` → patch, in that order, inside a single response.
