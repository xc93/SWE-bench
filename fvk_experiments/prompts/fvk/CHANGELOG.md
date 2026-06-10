# FVK prompt changelog

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
