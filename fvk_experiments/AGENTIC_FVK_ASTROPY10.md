# Agentic FVK reproduction on astropy10 — methodology & results

A controlled, three-arm reproduction of the Formal-Verification-Kit (FVK) "v1 → v2"
experiment, run as headless **Claude Code (Opus 4.6)** coding sessions on the first 10
astropy instances of **SWE-bench_Verified**. Written so the experiment can be reviewed
and reproduced end-to-end.

Companion machine-readable numbers: [RESULTS.md](RESULTS.md). Per-run raw transcripts,
exact prompts, audits, and eval reports live under
`runs/{pilot13236,rest9}__claude-code-opus-4.6__*`.

## 1. What this measures

Three arms, **one variable** — what happens after the agent's first draft:

| arm | protocol |
|---|---|
| **baseline** | one genuine pass: read issue + repo, produce a patch. No review step. |
| **review-control** | draft → self-eval (aggregate score) → **disciplined plain-English review** → revise → re-eval. No FVK. |
| **fvk-replicate** | Grigore Rosu's **verbatim 5-phase FVK protocol**: draft → self-eval → **FVK formalize/verify (spec, proof obligations)** → revise → re-eval. |

`review-control` and `fvk-replicate` are identical except Phase 3 (plain review vs. FVK);
both get the same aggregate-score feedback and the same revise step. The questions:

1. Does the FVK formal content help **beyond disciplined plain review**? (fvk vs review)
2. Does a draft→revise scaffold help **beyond one genuine pass**? (phased vs baseline)

This is the controlled form of Grigore's study, which compared no-FVK-v1 against FVK-v2
with **no plain-review control** and a **single draft that already knew FVK was coming**.

## 2. How it is run (methodology and controls)

- **Model / harness:** Opus 4.6 via headless `claude -p`, ≤200 turns / 90-min per session,
  one instance at a time.
- **Sealed sessions — and why.** Headless Claude Code silently inherits, by default:
  the repo's `CLAUDE.md` (which *describes this experiment*), the user's global memory
  (also FVK-related), and all installed plugins/MCP tools — **including a browser**. Each
  of these would contaminate the comparison and de-blind the baseline; we verified the
  leak with a planted-secret probe. So every session runs in a **sealed profile**: a clean
  `HOME` containing only auth, workspaces relocated outside the repo, and `WebSearch`,
  `WebFetch`, **and the `Skill` tool** denied (the CLI bundles review-flavoured skills —
  `code-review`/`simplify`/`verify` — that would confound the treatment). A re-probe
  confirmed a session sees none of the experiment context and no browser/skill tools.
  Mechanics: `fvk_bench/agents/profile.py`.
- **Leak-safe workspace.** Per instance: the repo at the base commit with **truncated
  history and no git remote** — the upstream fix commit is physically absent, so it can't
  be recovered. FVK is provided as **files** (`formal-verification-kit/`), not a skill.
- **Answer-key isolation.** The gold patch and hidden tests are stored **outside** the
  agent's workspace; the in-session evaluator reads them from there and prints **only
  aggregate counts**. Any session that reads the key or emits a hidden test name before
  grading is **auto-invalidated**. Across all 27 sessions here: **0 contaminated, 0
  invalidated**.
- **Dual-layer grading.** (1) the **in-session aggregate** the agent runs to guide its
  revision = treatment fidelity; (2) the **official SWE-bench docker harness** = the
  reported number. On the pilot these agreed exactly (FAIL_TO_PASS 2/2, PASS_TO_PASS
  644/644). All numbers below are the official harness verdict.
- **Fidelity to Grigore.** For `astropy__astropy-13236` we use **his verbatim prompt**;
  our `fvk-replicate` reproduced **his exact reported result** (resolved, 2/2, 644/644).
  The other 9 prompts are reconstructed from the public issue, labelled as such, with the
  "likely files" hint dropped. Declared deviations from his setup: kit served from a local
  path; environment pre-built; answer key relocated for integrity — all documented in the
  prompt provenance.

## 3. Results

**Final outcome (official harness, 10 instances = pilot 13236 + the other 9):**

| arm | resolved | unsolved |
|---|---|---|
| baseline (one pass) | **8 / 10** | 13398, 13977 |
| review-control | **8 / 10** | 13398, 13453 |
| fvk-replicate | **8 / 10** | 13398, 13453 |

All three reach **8/10**. **`review-control` and `fvk-replicate` reach the identical
solved set** — `{12907, 13033, 13236, 13579, 13977, 14096, 14182, 14309}`.

**Within-arm v1 → v2 (the "does the revise step help" signal; official harness):**

| arm | v1 | v2 | rescued (X→R) | regressed (R→X) |
|---|---|---|---|---|
| review-control | 6 / 10 | 8 / 10 | 13033, 13977 | none |
| fvk-replicate | 5 / 10 | 8 / 10 | 13033, 13977, 14182 | none |

Both converge to the **same v2 set**. FVK's larger jump (+3 vs +2) is **only because its
v1 was lazier** — its draft also missed 14182, which review's draft already had; the v2
outcome is identical.

### What the numbers say (honestly)

1. **FVK ≡ plain disciplined review on this set.** Identical final solved sets; the rescued
   instances differ only by v1 noise. The formal-methods content (specs, proof obligations,
   /formalize, /verify) added **nothing measurable** over a plain "review your draft
   carefully, including non-regression" step.
2. **The phased first draft is depressed vs. a genuine single pass — the sandbagged-draft
   effect.** baseline (genuine best effort) = 8/10; the phased arms' v1 = 6/10 (review) and
   5/10 (fvk). An agent that *knows it will revise* writes a weaker first draft. The revise
   step then largely **recovers this self-inflicted deficit** — v2 only **ties** baseline.
3. **No net gain over one genuine pass.** Both phased arms **trade 13453 for 13977** vs.
   baseline: baseline solved 13453 in one pass, but both phased arms' lazy v1 missed it and
   revision couldn't recover; conversely revision rescued 13977, which baseline missed. Net
   zero on count.
4. **"Zero regressions" (R→X 0) is not "never hurts vs. baseline."** No *passing v1* was
   broken by revision — but 13453 shows the scaffold *losing* an instance the baseline got,
   because the weaker draft started too far off for revision to save.
5. **13398** (hard: ITRS-to-observed refraction; the fix is a ~150-line new module)
   is **unsolved by all three**.

### Relation to Grigore's reproducibility study

This is the controlled version of his experiment, and **both confounds we predicted bite**:
with a plain-review control present, **FVK ties review**; and because the phased v1 is
depressed relative to a genuine single pass, his "v1 → v2 improvement" is **largely
recovery, not net gain**. On the one instance where we use his verbatim prompt
(`astropy-13236`) we **reproduce his exact result**, so the divergence is methodological,
not a setup error.

## 4. Caveats

n=10, **single sample per arm**. On this set we have separately measured **±2–4 instance
flips between two *identical* runs**, so the all-three-8/10 convergence and the
13453↔13977 swap sit **within noise**. The within-arm v1→v2 figures are paired (same
instance, same session) and therefore more robust than the cross-arm count comparison.
Replicates would be needed to put error bars on the counts.

## 5. Reproduce

```bash
PY=.venv/bin/python
# any arm (pilot = the 1 verbatim-Grigore instance; rest9 = the other 9):
$PY fvk_experiments/run.py run --config fvk_experiments/configs/rest9__claude-code-opus46__fvk-replicate.yaml
```

- **Configs:** `configs/{pilot13236,rest9}__claude-code-opus46__{baseline,review-control,fvk-replicate}.yaml`
- **Templates (the injected protocols):** `prompts/agentic/{baseline,review-control,fvk-replicate}.md`;
  replicate-vs-control diff in `prompts/agentic/CONTROL_DIFF.md`; Grigore's verbatim source
  in `prompts/agentic/source/`.
- **Run artifacts** (raw stream-json transcripts, exact composed prompt per instance,
  per-session audit, in-session + official eval reports, v1→v2 transition table):
  `runs/{pilot13236,rest9}__claude-code-opus-4.6__*`.
- **Sealing / grading code:** `fvk_bench/agents/profile.py` (sealed session),
  `fvk_bench/agents/claude_code.py` (runner + audit), `fvk_bench/evaluate.py` + the official
  docker harness (grading).
