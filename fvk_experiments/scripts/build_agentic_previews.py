#!/usr/bin/env python
"""Regenerate the agentic-arm prompt previews and CONTROL_DIFF.md.

Previews (prompts/agentic/preview/<arm>/<instance_id>.md) are review copies of
the exact per-instance prompts the runner will stage, instantiated from the
real SWE-bench_Verified rows for the 10 pinned astropy instances; runtime
instantiation happens in the runner via the same fvk_bench.agentic_prompts
pipeline (tests assert preview == runtime instantiation for 13236).

CONTROL_DIFF.md is the human-readable unified diff of the fvk-replicate vs
review-control template bodies (frontmatter + deviation comments stripped),
for the experiment owner and for Grigore.

Usage:
    .venv/bin/python fvk_experiments/scripts/build_agentic_previews.py
HF network flake: retry, or HF_ENDPOINT=https://hf-mirror.com
"""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.agentic_prompts import (  # noqa: E402
    AGENTIC_DIR,
    ARMS,
    TEMPLATE_PATHS,
    load_template,
    render,
)

# The pinned astropy10 subject set (same ids as every astropy10__*.yaml config).
PINNED = [
    "astropy__astropy-12907", "astropy__astropy-13033", "astropy__astropy-13236",
    "astropy__astropy-13398", "astropy__astropy-13453", "astropy__astropy-13579",
    "astropy__astropy-13977", "astropy__astropy-14096", "astropy__astropy-14182",
    "astropy__astropy-14309",
]

CONTROL_DIFF_HEADER = """\
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
"""


def build_control_diff() -> None:
    rep = load_template(TEMPLATE_PATHS["fvk-replicate"]).splitlines(keepends=True)
    ctl = load_template(TEMPLATE_PATHS["review-control"]).splitlines(keepends=True)
    diff = "".join(difflib.unified_diff(
        rep, ctl, fromfile="fvk-replicate.md", tofile="review-control.md", n=3))
    out = AGENTIC_DIR / "CONTROL_DIFF.md"
    out.write_text(CONTROL_DIFF_HEADER + diff + "```\n")
    changed = sum(1 for l in diff.splitlines() if l[:1] in "+-" and l[:3] not in ("+++", "---"))
    print(f"wrote {out} ({changed} changed lines)")


def build_previews() -> None:
    from datasets import load_dataset

    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    offsets = {iid: i for i, iid in enumerate(ds["instance_id"])}
    for arm in ARMS:
        outdir = AGENTIC_DIR / "preview" / arm
        outdir.mkdir(parents=True, exist_ok=True)
        for iid in PINNED:
            row = ds[offsets[iid]]
            # render() == instantiate(load_template, fields) plus the
            # reconstruction marker for non-curated instances (all but 13236).
            (outdir / f"{iid}.md").write_text(
                render(TEMPLATE_PATHS[arm], row, row_offset=offsets[iid]))
        print(f"wrote {len(PINNED)} previews under {outdir}")


# ---------------------------------------------------------------- v2 -------
# v2 (45-instance multi-repo) previews: one REPRESENTATIVE instance per repo of
# the Grigore-set (8 repos; includes 3 of the 6 hard compiled-dep ids), per arm,
# under preview/<arm>-v2/. Bounded on purpose — the full 45 would be 135 files;
# rendering is unit-tested, previews exist for human review of exact wording.

V2_TEMPLATE_PATHS = {arm: AGENTIC_DIR / f"{arm}-v2.md" for arm in ARMS}

PINNED_V2_PER_REPO = [
    "django__django-10554",                  # django (22 of the 45)
    "sympy__sympy-17630",                    # sympy (Grigore's own sample)
    "sphinx-doc__sphinx-9461",               # sphinx-doc
    "astropy__astropy-13398",                # astropy [hard: pre-built venv]
    "pytest-dev__pytest-5787",               # pytest-dev (setuptools-scm repo)
    "pydata__xarray-3993",                   # xarray [hard]
    "pylint-dev__pylint-4551",               # pylint-dev
    "scikit-learn__scikit-learn-25102",      # scikit-learn [hard]
]

CONTROL_DIFF_V2_HEADER = """\
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
"""


def build_control_diff_v2() -> None:
    rep = load_template(V2_TEMPLATE_PATHS["fvk-replicate"]).splitlines(keepends=True)
    ctl = load_template(V2_TEMPLATE_PATHS["review-control"]).splitlines(keepends=True)
    diff = "".join(difflib.unified_diff(
        rep, ctl, fromfile="fvk-replicate-v2.md", tofile="review-control-v2.md", n=3))
    out = AGENTIC_DIR / "CONTROL_DIFF-v2.md"
    out.write_text(CONTROL_DIFF_V2_HEADER + diff + "```\n")
    changed = sum(1 for l in diff.splitlines() if l[:1] in "+-" and l[:3] not in ("+++", "---"))
    print(f"wrote {out} ({changed} changed lines)")


def build_previews_v2() -> None:
    from datasets import load_dataset

    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    offsets = {iid: i for i, iid in enumerate(ds["instance_id"])}
    for arm in ARMS:
        outdir = AGENTIC_DIR / "preview" / f"{arm}-v2"
        outdir.mkdir(parents=True, exist_ok=True)
        for iid in PINNED_V2_PER_REPO:
            row = ds[offsets[iid]]
            (outdir / f"{iid}.md").write_text(
                render(V2_TEMPLATE_PATHS[arm], row, row_offset=offsets[iid]))
        print(f"wrote {len(PINNED_V2_PER_REPO)} previews under {outdir}")


if __name__ == "__main__":
    build_control_diff()
    build_previews()
    build_control_diff_v2()
    build_previews_v2()
