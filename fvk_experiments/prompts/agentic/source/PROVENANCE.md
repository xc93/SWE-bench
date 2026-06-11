# Source artifacts — provenance

Verbatim artifacts from Grigore Rosu's own FVK-on-SWE-bench runs, used as the ground
truth for the agentic replication templates in `fvk_experiments/prompts/agentic/`.
Files are copied **unmodified**; the fidelity unit test
(`fvk_experiments/tests/test_agentic_prompts.py`) diffs our instantiated template
against `astropy_13236_fvk_prompt.md` byte-for-byte.

## Origin

- Telegram group **"Fast Verification Positioning"**, sender **Grigore Rosu**.
- Primary copy: Telegram Desktop export
  `~/Downloads/Telegram Desktop/DataExport_2026-06-11/chats/chat_002/files/`
  (chat_002 = "Fast Verification Positioning" in the export's `result.json`).
- `sympy__sympy-17630_PROMPT.md` and `sympy__sympy-17630_public_instance.json` were
  copied from the direct-download copies in `~/Downloads/Telegram Desktop/` (the paths
  given in the task); sha256 verified **byte-identical** to the export copies of the
  same messages. All five files exist in both locations with matching hashes.

## Files

| file | sha256 | sent (msg id, UTC-local export time) | what it is |
|---|---|---|---|
| `astropy_13236_fvk_prompt.md` | `bce576d671d83f47c2219e2a832c13201091bbe2a752e0b4e7c5a7575c01dd38` | 35473, 2026-06-10 22:48:10 | His verbatim per-instance agent prompt for `astropy__astropy-13236` (an instance IN our pinned astropy10 set). **Primary template source** — `fvk-replicate.md` is reversed from this file. |
| `sympy__sympy-17630_fvk_prompt.md` | `a657785a93927d43bb5dc7b4aadc6d40451d32e13b4634e1976f261e62fba354` | 35502, 2026-06-11 04:45:30 | His verbatim per-instance agent prompt for `sympy__sympy-17630` (a later, compact restyling of the same protocol). Used as a structural cross-check only. |
| `CONSOLIDATED_REPORT.md` | `65e161e53945bedb770997a6ce5d8f69a91c258c8c1df7beee3dc5596c58ff44` | 35487, 2026-06-11 02:01:05 | His consolidated results table for the same 10 astropy instances we have pinned (v1 vs v2, per-instance scores, his interpretation). Reference numbers for the replication. |
| `sympy__sympy-17630_PROMPT.md` | `7ca077e3816be01809b90b4800dc996748c65dcf64ec02c92186cfe4a358cc5a` | 35501, 2026-06-11 04:45:30 | His staged `benchmark/PROMPT.md` for the sympy instance: public fields + full problem statement + hints. Shape reference for what the runner stages at `benchmark/PROMPT.md`. |
| `sympy__sympy-17630_public_instance.json` | `f16a0dc2b8896c332bf342b7545fd5768713f4911ef6a59fd0e19782b9025137` | 35500, 2026-06-11 04:45:30 | His staged `benchmark/public_instance.json` for the sympy instance: public row fields only (incl. `hf_offset`, `repo_url`, `base_commit_url`, `language`). Shape reference for the runner's staging. |

## Why 13236 is the template base

The two prompt samples implement the same 5-phase protocol but disagree structurally
(below). Per the experiment design, the template `fvk-replicate.md` follows
**`astropy_13236_fvk_prompt.md` byte-faithfully** — it is the arm we run (astropy
instances) and the sample for an instance inside our pinned set. The sympy sample
informs only (i) the pre-staged-workspace model that our deviation (b) adopts and
(ii) the verbatim-vs-reconstructed split of per-instance fields.

## Declared deviations from his 13236 prompt

The instantiated `fvk-replicate.md` reproduces `astropy_13236_fvk_prompt.md`
byte-for-byte except **three** declared deviations, each marked in-template by a
whole-line HTML comment and frozen by the fidelity test
(`tests/test_agentic_prompts.py` + `tests/fixtures/astropy_13236_residual.diff`):

- **(a) kit from a local path.** The kit is read from the staged
  `formal-verification-kit/` instead of being git-cloned from
  `https://github.com/grosu/formal-verification-kit` (the Instance-section kit
  line and the Phase-3 clone block).
- **(b) pre-built environment, Phase 0.** His "Workspace Setup" (mkdir under
  `/home/openclaw`, fetch the HF row via urllib, `git clone` the repo) is replaced
  by a staged-layout listing + "Phase 0: Verify the Pre-Built Environment"; Phase 2
  runs the pre-staged `scripts/private_eval.py` instead of "official harness if
  available, else write an evaluator" (his five evaluator requirements kept verbatim
  as the description of what the staged evaluator does).
- **(c) answer key relocated out of the agent workspace for measurement
  integrity.** The full benchmark row (reference solution + hidden tests) is no
  longer staged at `private_eval/swebench_row_full.json`, so it is dropped from the
  staged layout and his rule "Do not manually open
  private_eval/swebench_row_full.json. It contains private benchmark fields." is
  replaced by a faithful line: grading is performed by `scripts/private_eval.py`,
  which reports only aggregate pass/fail counts; the reference solution and hidden
  tests are not available in this workspace. The evaluator is still invoked
  identically (`.venv/bin/python scripts/private_eval.py <patch> <label>`) and the
  identical aggregate feedback that feeds v2 is preserved — it just reads the hidden
  data from a location the agent cannot see. `review-control.md` inherits (b) and
  (c) verbatim and does not apply (a) (no kit); `baseline.md` is single-pass and,
  per the shared contract, makes no reference to `private_eval/`,
  `swebench_row_full.json`, or `scripts/private_eval.py` at all.

## Verbatim vs reconstructed prompts

**Only `astropy__astropy-13236` is verbatim.** It is the single instance for which
we hold Grigore's own per-instance prompt, so its four curated editorial fields
(`public_issue_gist`, `likely_files_block`, `instance_questions_block`,
`unrelated_behavior_bullet`) are copied byte-for-byte from his file and frozen by
the fidelity test.

The other **9 pinned instances are RECONSTRUCTIONS**: their prompts are
auto-generated from the public issue, with the protocol scaffolding identical to
13236 but the editorial fields derived generically. Two consequences:

- **No likely-files hint.** `{likely_files_block}` is **empty** for every
  reconstructed instance — there is no "Likely relevant public files include:"
  block and no file-selection nudge. Only the curated 13236 prompt carries that
  hint (his verbatim wording).
- **Provenance marker.** Every reconstructed instance's generated prompt is stamped
  near the top with a whole-line HTML comment,
  `<!-- RECONSTRUCTED PROMPT: auto-generated from the public issue; NOT Grigore's
  verbatim. Only astropy-13236 is verbatim. -->`. It is archived in the saved
  prompt (`runs/<id>/prompts/<iid>.system.txt`) and in the committed previews, but
  it is an HTML comment (not agent instruction text) and is identical across all
  three arms for a given instance, so it cancels in the fvk-replicate-vs-control
  comparison. The marker is added by `agentic_prompts.render()` after
  `load_template` (which strips the templates' own deviation comments), so unlike
  those it does survive into the instantiated output — by design.

## Template ambiguities (where the sympy sample differs from 13236)

Every structural difference between the two samples, and what the template does:

1. **Problem statement placement.** sympy inlines the full problem statement and a
   "Public hints / discussion text" block in the prompt; 13236 leaves it in
   `benchmark/PROMPT.md` and instead gives a one-sentence gist ("The public issue is
   about ...") plus a "Likely relevant public files include:" list in Phase 1.
   → Template follows 13236: per-instance fields `{public_issue_gist}` and
   `{likely_files_block}` (the latter curated to his exact text — header +
   bullets — **only for 13236**; **empty for every other instance**, see
   "Verbatim vs reconstructed" below).
2. **Workspace staging.** sympy's workspace is pre-staged (`benchmark/`,
   `private_eval/swebench_row_full.json`, `scripts/private_eval.py` already exist) and
   has an explicit `Phase 0: clone/setup` that clones the repo and builds a venv;
   13236 has an unlabeled "Workspace Setup" section that mkdirs, fetches the HF row
   itself, and clones the repo (no venv/install step at all).
   → Template keeps 13236's "Workspace Setup" heading but adopts the pre-staged model
   (= our declared deviation (b)), adding a `Phase 0: Verify the Pre-Built
   Environment` that keeps the setup-sanity intent and sympy's
   `reports/setup_notes.md` artifact. Note that under deviation (c) the full row is
   NOT staged: the workspace lists `benchmark/`, `scripts/private_eval.py`, `repo/`,
   `.venv/`, and (replicate only) `formal-verification-kit/`, but no
   `private_eval/swebench_row_full.json`.
3. **Evaluator.** 13236 says "Use the official SWE-bench harness if available", else
   *write* a local private evaluator meeting five requirements; sympy *runs the
   pre-staged* `scripts/private_eval.py <patch> vN`.
   → Template adopts the sympy/staged model (second occurrence of deviation (b)),
   keeping 13236's five evaluator requirements verbatim as the description of what
   `scripts/private_eval.py` does.
4. **FVK artifacts.** sympy adds an optional `fvk/PROOF.md` "if useful"; 13236
   requires exactly `fvk/SPEC.md`, `fvk/FINDINGS.md`, `fvk/PROOF_OBLIGATIONS.md`,
   `fvk/ITERATION_GUIDANCE.md`. → Template keeps 13236's four required artifacts.
5. **Discipline list.** sympy's discipline adds "no private JUnit XML", an explicit
   "do NOT search the web/Hugging Face/GitHub PRs/issues for ... `sympy__sympy-17630`"
   (13236 only forbids searching for the original PR/solution), and folds the
   "FVK must accumulate findings" rule into the discipline list. → Template keeps
   13236's 8-rule list verbatim.
6. **Final response format.** sympy asks for "compact YAML"; 13236 gives a fixed
   indented summary template. → Template keeps 13236's fixed summary.
7. **Metadata lines.** sympy: combined repo line (`owner/name` + URL), `Version:`,
   `Language: Python`, offset stated as "HF row offset 461", no base-commit URL,
   kit line labeled `FVK:`. 13236: separate Repository/Base-commit/Base-commit-URL
   lines, `Astropy version:` (project name capitalized), full datasets-server row URL,
   kit line labeled `Formal Verification Kit:`. → Template keeps 13236's lines, with
   `{repo_title} version:` and `{row_url}` as fields; no Language line.
8. **Evaluator-shape heading.** sympy: "Evaluator shape, counts only:"; 13236:
   "Known evaluator shape:". → 13236 kept.
9. **Regression-heavy note.** 13236 (644 PASS_TO_PASS) has "This is a
   regression-heavy task. A v2 patch can be worse than v1 ..."; sympy (19
   PASS_TO_PASS) has no such note. → Modeled as the per-instance field
   `{regression_note}`: instances with ≥ 100 PASS_TO_PASS tests get his exact 13236
   sentence pair; smaller instances get only the second (instance-independent)
   sentence. Threshold documented in `fvk_bench/agentic_prompts.py`.
10. **Phase headings/tone.** sympy uses compact lowercase headings ("Phase 1: v1
    without FVK") and fenced code blocks; 13236 uses long headings ("Phase 1:
    Generate v1 Without FVK") and 4-space-indented blocks. → 13236 kept throughout
    (including in the two deviation blocks, which use indented blocks).

Two further 13236-internal notes (not sympy differences):

- 13236's Phase-3 question list (1–11): items 2–7 are instance-specific (NdarrayMixin,
  Astropy 5.0/5.1/5.2, Column/mixin/ndarray/masked invariants); items 1 and 8–11 are
  generic. Modeled as field `{instance_questions_block}` covering items 2.–7. with
  fixed outer numbering, so every instance gets the same 11-slot structure.
- 13236's Phase-4 "Be conservative" list has one instance-specific bullet ("avoid
  changing unrelated table construction behavior;") → field
  `{unrelated_behavior_bullet}`.
- The final report's question 7 ("What should be changed in the FVK process for
  regression-heavy SWE-bench tasks?") is kept static even for low-PASS_TO_PASS
  instances: it asks about the process in general, and parametrizing it would deviate
  from his text for 13236.
