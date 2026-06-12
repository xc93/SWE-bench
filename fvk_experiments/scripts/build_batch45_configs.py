#!/usr/bin/env python3
"""Generate the 15 batchN__claude-code-opus46__<arm> configs for the 45-run.

The 45-instance (Grigore-set) run is split into 5 sittings of 9 instances each
(batch1..batch5), times 3 arms (baseline / review-control / fvk-replicate) =
15 configs. The agent self-builds its env (v2 templates); authoritative grading
is via the official docker image. The 6 hard compiled-dependency instances
(3 astropy + 2 xarray + 1 scikit-learn) get a pre-built venv; the other 39 are
repo-only.

Deterministic + reproducible: the batch->id split is hard-coded below and a
self-check asserts union == the 45 unique ids before any file is written. Re-run:

    .venv/bin/python fvk_experiments/scripts/build_batch45_configs.py

Frozen once run; this generator exists so the split is auditable and the 15
files cannot drift apart by hand-editing.
"""

from __future__ import annotations

from pathlib import Path

CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"

ARMS = ("baseline", "review-control", "fvk-replicate")
V2_TEMPLATE = {
    "baseline": "prompts/agentic/baseline-v2.md",
    "review-control": "prompts/agentic/review-control-v2.md",
    "fvk-replicate": "prompts/agentic/fvk-replicate-v2.md",
}

# The 6 hard compiled-dependency instances (pre-built venv from our builder).
HARD = {
    "astropy__astropy-13398", "astropy__astropy-13579", "astropy__astropy-14369",
    "pydata__xarray-3993", "pydata__xarray-6992",
    "scikit-learn__scikit-learn-25102",
}

# The full 45 (Grigore-set), grouped by repo for readability.
ALL45 = [
    "astropy__astropy-13398", "astropy__astropy-13579", "astropy__astropy-14369",
    "django__django-10554", "django__django-11138", "django__django-11400",
    "django__django-11885", "django__django-12325", "django__django-12708",
    "django__django-13128", "django__django-13212", "django__django-13344",
    "django__django-13449", "django__django-13837", "django__django-14007",
    "django__django-14011", "django__django-14631", "django__django-15128",
    "django__django-15268", "django__django-15503", "django__django-15629",
    "django__django-15957", "django__django-16263", "django__django-16560",
    "django__django-16631",
    "pydata__xarray-3993", "pydata__xarray-6992",
    "pylint-dev__pylint-4551", "pylint-dev__pylint-8898",
    "pytest-dev__pytest-10356", "pytest-dev__pytest-5787", "pytest-dev__pytest-6197",
    "scikit-learn__scikit-learn-25102",
    "sphinx-doc__sphinx-11510", "sphinx-doc__sphinx-7590", "sphinx-doc__sphinx-8548",
    "sphinx-doc__sphinx-9229", "sphinx-doc__sphinx-9461",
    "sympy__sympy-12489", "sympy__sympy-13852", "sympy__sympy-13878",
    "sympy__sympy-14248", "sympy__sympy-16597", "sympy__sympy-17630",
    "sympy__sympy-18199",
]

# 5 sittings of 9. Each hard instance is placed in a distinct batch as far as
# possible (astropy 1/2/3 -> batches 1/2/3; xarray -> batches 4 & 5; sklearn ->
# batch 5); the remainder fill by repo to keep each sitting coherent. Order does
# NOT matter for env reasons anymore (agent self-builds), so this is purely an
# organizational split. THE AUTHORITATIVE batch->id mapping is right here.
BATCHES: dict[int, list[str]] = {
    1: ["astropy__astropy-13398",  # hard
        "django__django-10554", "django__django-11138", "django__django-11400",
        "django__django-11885", "django__django-12325", "django__django-12708",
        "django__django-13128", "django__django-13212"],
    2: ["astropy__astropy-13579",  # hard
        "django__django-13344", "django__django-13449", "django__django-13837",
        "django__django-14007", "django__django-14011", "django__django-14631",
        "django__django-15128", "django__django-15268"],
    3: ["astropy__astropy-14369",  # hard
        "django__django-15503", "django__django-15629", "django__django-15957",
        "django__django-16263", "django__django-16560", "django__django-16631",
        "pylint-dev__pylint-4551", "pylint-dev__pylint-8898"],
    4: ["pydata__xarray-3993",  # hard
        "pytest-dev__pytest-10356", "pytest-dev__pytest-5787", "pytest-dev__pytest-6197",
        "sphinx-doc__sphinx-11510", "sphinx-doc__sphinx-7590", "sphinx-doc__sphinx-8548",
        "sphinx-doc__sphinx-9229", "sphinx-doc__sphinx-9461"],
    5: ["pydata__xarray-6992", "scikit-learn__scikit-learn-25102",  # hard, hard
        "sympy__sympy-12489", "sympy__sympy-13852", "sympy__sympy-13878",
        "sympy__sympy-14248", "sympy__sympy-16597", "sympy__sympy-17630",
        "sympy__sympy-18199"],
}


def _check() -> None:
    assert len(ALL45) == 45 == len(set(ALL45)), "ALL45 is not 45 unique ids"
    union: set[str] = set()
    for n in range(1, 6):
        b = BATCHES[n]
        assert len(b) == 9 == len(set(b)), f"batch{n} is not 9 unique ids"
        union |= set(b)
    assert union == set(ALL45), (
        "batch union != the 45", union ^ set(ALL45))
    covered = set().union(*(set(b) & HARD for b in BATCHES.values()))
    assert covered == HARD, ("hard instances not all covered", HARD ^ covered)


def _config_text(batch_n: int, arm: str) -> str:
    ids = BATCHES[batch_n]
    hard_here = [i for i in ids if i in HARD]
    id_lines = "\n".join(f"    - {i}" for i in ids)
    hard_note = (", ".join(hard_here) if hard_here else "(none)")
    return f"""\
# 45-instance (Grigore-set) run — batch {batch_n}/5, arm `{arm}`.
#
# This is one sitting of 9 of the 45 SWE-bench_Verified instances spanning 8
# repos (django, sympy, sphinx-doc, astropy, pytest-dev, pydata/xarray,
# pylint-dev, scikit-learn). Headless Claude Code (Opus 4.6) sessions, one per
# instance. Unlike the astropy10 (v1) run, the AGENT SELF-BUILDS its working
# env in Phase 0 (v2 templates): repo/ is staged history-truncated with no
# remote, and for the 39 repo-only instances no .venv is pre-built. The 6 hard
# compiled-dependency instances (3 astropy + 2 xarray + 1 scikit-learn) DO get a
# pre-built venv from our builder. AUTHORITATIVE grading (in-session and final)
# uses each instance's official prebuilt docker image via the harness eval path
# — the agent's self-built env is only its iterating scratchpad.
#
# 5 batches x 3 arms = 15 configs; the 45 ids partition exactly across the 5
# batches (see fvk_experiments/scripts/build_batch45_configs.py for the split).
# Hard (pre-built-venv) instances in THIS batch: {hard_note}.
#
# Pair-compare arms WITHIN a batch (same model, same harness). Generated by
# scripts/build_batch45_configs.py — edit there and regenerate, do not hand-edit.
# Rerun:
#   .venv/bin/python fvk_experiments/run.py run --config fvk_experiments/configs/batch{batch_n}__claude-code-opus46__{arm}.yaml
run_name: batch{batch_n}__claude-code-opus-4.6__{arm}
tag: {arm}

dataset:
  name: princeton-nlp/SWE-bench_Verified
  split: test
  oracle_text_dataset: princeton-nlp/SWE-bench_oracle
  # Batch {batch_n} of the 45 (Grigore-set); union of all 5 batches == the 45 unique ids.
  instance_ids:
{id_lines}

model:
  provider: claude-code        # headless multi-turn `claude -p` sessions (CLI login, no API key here)
  name: claude-code-opus-4.6   # must match the other claude-code arms for a valid pair
  cc_model: claude-opus-4-6    # the `claude --model` value
  max_turns: 200               # per-session agentic turn cap (claude --max-turns)
  session_timeout_s: 5400      # 90 min wall-clock kill switch per session

inference:
  max_workers: 1               # one agent session at a time (multi-repo env builds are heavyweight)

eval:
  max_workers: 4
  timeout_s: 1800

prompt:
  style: oracle
  system_prompt: {V2_TEMPLATE[arm]}   # v2 (multi-repo, agent self-build) session template
"""


def main() -> None:
    _check()
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for batch_n in range(1, 6):
        for arm in ARMS:
            path = CONFIGS_DIR / f"batch{batch_n}__claude-code-opus46__{arm}.yaml"
            path.write_text(_config_text(batch_n, arm))
            written.append(path.name)
    print(f"wrote {len(written)} configs to {CONFIGS_DIR}:")
    for n in written:
        print("  " + n)


if __name__ == "__main__":
    main()
