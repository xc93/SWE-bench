# FVK prompt changelog

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
