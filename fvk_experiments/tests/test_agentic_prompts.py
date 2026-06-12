"""Tests for the agentic replication prompt layer (fvk_bench/agentic_prompts.py).

The critical test is fidelity: instantiating prompts/agentic/fvk-replicate.md
for astropy__astropy-13236 must reproduce Grigore Rosu's verbatim
prompts/agentic/source/astropy_13236_fvk_prompt.md byte-for-byte EXCEPT the THREE
declared deviations ((a) kit staged locally instead of fetched from GitHub;
(b) pre-built workspace verified in Phase 0 + pre-staged scripts/private_eval.py
in Phase 2; (c) answer key relocated out of the workspace — the full benchmark
row is not staged and the "Do not manually open ..." rule is replaced by a line
saying scripts/private_eval.py reports only aggregate counts). The expected
residual diff is frozen as a fixture, and a separate region-based check proves
every non-deviation line survives verbatim, in order.

No network: the 13236 row is a fixture (public fields only — gold patch and
test_patch deliberately omitted) carrying its dataset offset.
"""

import difflib
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.agentic_prompts import (
    ARMS,
    CURATED_INSTANCES,
    RECONSTRUCTED_MARKER,
    REGRESSION_HEAVY_P2P,
    TEMPLATE_PATHS,
    fields_for_instance,
    instantiate,
    is_reconstructed,
    load_template,
    render,
)

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
AGENTIC = HERE.parent / "prompts" / "agentic"
HIS_13236 = AGENTIC / "source" / "astropy_13236_fvk_prompt.md"
PREVIEWS = AGENTIC / "preview"

DIFF_FROM = "source/astropy_13236_fvk_prompt.md"
DIFF_TO = "instantiated/fvk-replicate@astropy__astropy-13236"


def _row_13236() -> dict:
    return json.loads((FIXTURES / "astropy_13236_public_row.json").read_text())


def _fields_13236() -> dict:
    row = _row_13236()
    return fields_for_instance(row, row_offset=row["_row_offset"])


def _instantiated(arm: str, fields: dict | None = None) -> str:
    return instantiate(load_template(TEMPLATE_PATHS[arm]), fields or _fields_13236())


# --------------------------------------------------------------- fidelity ---

def test_fidelity_residual_diff_is_exactly_the_frozen_deviations():
    """THE critical check: his file -> our instantiation differs only by the
    frozen residual diff (= the three declared deviations; deviation (c)'s
    one-line wording change folds into the (b) Workspace-Setup hunk, so the
    unified diff still groups into 4 proximity hunks)."""
    his = HIS_13236.read_text()
    ours = _instantiated("fvk-replicate")
    diff = "".join(difflib.unified_diff(
        his.splitlines(keepends=True), ours.splitlines(keepends=True),
        fromfile=DIFF_FROM, tofile=DIFF_TO, n=3))
    expected = (FIXTURES / "astropy_13236_residual.diff").read_text()
    assert diff == expected, "residual diff drifted from the frozen deviation hunks"
    assert sum(1 for l in expected.splitlines() if l.startswith("@@")) == 4


def _deviation_line_indices(his_lines: list[str]) -> set[int]:
    """Indices (in his file) of lines belonging to the THREE DECLARED deviations.

    (a) kit-from-local-path: the kit GitHub URL line, the kit-clone block, and
        the fvk_repo/ paths.
    (b) pre-built-env Phase 0: the Workspace Setup body -- mkdir + HF-row fetch +
        clone -- everything from "Create a clean workspace:" up to "## Phase 1";
        and in Phase 2 the official-harness / write-an-evaluator lines.
    (c) answer-key-relocated wording: the "Do not manually open
        private_eval/swebench_row_full.json. It contains private benchmark
        fields." rule, which is REPLACED by the grading line (so it no longer
        survives verbatim). It sits inside the Workspace Setup span, so the whole
        span (b)+(c) is deviation with no surviving-line exception.
    """
    idx = {line: i for i, line in enumerate(his_lines)}
    dev: set[int] = set()
    # (b) + (c) workspace setup body, entire span (the formerly-kept
    # "Do not manually open ..." line is now deviation (c): replaced wording)
    start = idx["Create a clean workspace:"]
    end = idx["## Phase 1: Generate v1 Without FVK"]
    dev.update(range(start, end))
    # (b) phase 2 harness-or-write-evaluator
    h = idx["Use the official SWE-bench harness if available."]
    w = idx["If the official harness is not available, write a local private evaluator that:"]
    dev.update(range(h, w + 1))
    # (a) kit references
    for i, line in enumerate(his_lines):
        if "grosu/formal-verification-kit" in line or "fvk_repo" in line \
                or line == "Clone the FVK repository:":
            dev.add(i)
    # blank lines sandwiched between deviation lines belong to the region too
    for i, line in enumerate(his_lines):
        if line == "" and (i - 1) in dev and (i + 1) in dev:
            dev.add(i)
    return dev


def test_fidelity_every_non_deviation_line_survives_verbatim_in_order():
    """Independent of the frozen fixture: every line of his prompt that is not
    part of a declared deviation appears verbatim, in order, in our output."""
    his_lines = HIS_13236.read_text().splitlines()
    ours_lines = _instantiated("fvk-replicate").splitlines()
    dev = _deviation_line_indices(his_lines)
    must_survive = [l for i, l in enumerate(his_lines) if i not in dev]
    pos = 0
    for line in must_survive:
        while pos < len(ours_lines) and ours_lines[pos] != line:
            pos += 1
        assert pos < len(ours_lines), f"verbatim line lost or reordered: {line!r}"
        pos += 1
    # cross-check against the frozen diff: every deleted line lies inside a
    # declared deviation region (so the fixture cannot hide extra deviations)
    fixture = (FIXTURES / "astropy_13236_residual.diff").read_text().splitlines()
    deleted = [l[1:] for l in fixture if l.startswith("-") and not l.startswith("---")]
    from collections import Counter
    outside = Counter(deleted) - Counter(his_lines[i] for i in dev)
    assert not outside, f"deleted lines outside declared deviation regions: {outside}"


def test_curated_13236_field_values_are_verbatim_from_his_prompt():
    his = HIS_13236.read_text()
    f = _fields_13236()
    for key in ("public_issue_gist", "likely_files_block",
                "instance_questions_block", "unrelated_behavior_bullet"):
        for line in f[key].splitlines():
            assert line in his, f"{key} line not verbatim in his prompt: {line!r}"


# ----------------------------------------------- reconstruction marker -------

def test_only_13236_is_curated_verbatim():
    assert CURATED_INSTANCES == frozenset({"astropy__astropy-13236"})
    assert not is_reconstructed("astropy__astropy-13236")
    assert is_reconstructed("astropy__astropy-12907")
    assert is_reconstructed("sympy__sympy-17630")


def test_render_curated_13236_has_no_marker_and_equals_instantiation():
    """13236 is verbatim: render() must add no marker and equal the raw
    instantiate(load_template, fields) output (so fidelity is unaffected)."""
    row = _row_13236()
    for arm in ARMS:
        out = render(TEMPLATE_PATHS[arm], row, row_offset=row["_row_offset"])
        assert RECONSTRUCTED_MARKER not in out, arm
        assert out == _instantiated(arm), arm


def test_render_reconstructed_instance_carries_marker_near_top():
    """Every non-curated instance's rendered prompt is stamped with the
    provenance marker as a whole-line HTML comment at the very top, followed by
    the unchanged instruction body."""
    row = _fake_row()  # sympy__sympy-17630, not curated
    for arm in ARMS:
        out = render(TEMPLATE_PATHS[arm], row, row_offset=0)
        assert out.startswith(RECONSTRUCTED_MARKER + "\n\n"), arm
        # marker is an HTML comment that names 13236 as the only verbatim prompt
        assert out.startswith("<!--") and out.split("\n", 1)[0].endswith("-->")
        assert "Only astropy-13236 is verbatim" in out
        # the body below the marker is exactly the marker-less instantiation
        body = out[len(RECONSTRUCTED_MARKER) + 2:]
        assert body == instantiate(load_template(TEMPLATE_PATHS[arm]),
                                   fields_for_instance(row, row_offset=0)), arm
        # marker carries no agent instruction text and no file-selection nudge
        assert "Likely relevant public files include:" not in out, arm


# ----------------------------------------------------------- instantiator ---

def test_load_template_strips_frontmatter_and_deviation_comments():
    for arm in ARMS:
        body = load_template(TEMPLATE_PATHS[arm])
        assert not body.startswith("---"), arm
        assert "<!--" not in body and "DEVIATION" not in body, arm
        assert body.startswith("# Prompt for Fresh Coding Agent:"), arm


def test_instantiate_errors_on_missing_fields():
    with pytest.raises(ValueError, match=r"\['bar', 'foo'\]"):
        instantiate("x {foo} y {bar} z {foo}", {"baz": "1"})


def test_instantiate_errors_on_non_string_values():
    with pytest.raises(ValueError, match="must be str"):
        instantiate("{n}", {"n": 644})


def test_instantiate_ignores_literal_braces_and_extra_fields():
    tpl = 'mkdir {a,b} json {"k": 1} fmt {Upper} {_x} ok {field}'
    out = instantiate(tpl, {"field": "F", "unused": "U"})
    assert out == 'mkdir {a,b} json {"k": 1} fmt {Upper} {_x} ok F'


def test_instantiation_leaves_no_unresolved_placeholders():
    fields = _fields_13236()
    pat = re.compile(r"\{([a-z][a-z0-9_]*)\}")
    for arm in ARMS:
        out = _instantiated(arm, fields)
        leftover = set(pat.findall(out)) & set(fields)
        assert not leftover, (arm, leftover)


# ----------------------------------------------------- fields_for_instance ---

def test_fields_13236_core_values():
    f = _fields_13236()
    assert f["instance_id"] == "astropy__astropy-13236"
    assert f["repo"] == "astropy/astropy"
    assert f["repo_url"] == "https://github.com/astropy/astropy.git"
    assert f["base_commit"] == "6ed769d58d89380ebaa1ef52b300691eefda8928"
    assert f["base_commit_url"].endswith("/commit/" + f["base_commit"])
    assert (f["repo_title"], f["module_name"]) == ("Astropy", "astropy")
    assert (f["version"], f["difficulty"]) == ("5.0", "15 min - 1 hour")
    assert (f["fail_to_pass_count"], f["pass_to_pass_count"]) == ("2", "644")
    assert f["row_url"].endswith("&offset=2&length=1")
    assert f["regression_note"].startswith("This is a regression-heavy task.")


def _fake_row(**over) -> dict:
    row = {
        "instance_id": "sympy__sympy-17630",
        "repo": "sympy/sympy",
        "base_commit": "58e78209c8577b9890e957b624466e5beed7eb08",
        "version": "1.5",
        "difficulty": "1-4 hours",
        "problem_statement": (
            "Exception when multiplying BlockMatrix containing ZeroMatrix blocks\n"
            "When a block matrix ... see sympy/matrices/expressions/blockmatrix.py\n"
            "and sympy.strategies.core internals.\n"),
        "FAIL_TO_PASS": json.dumps([f"t{i}" for i in range(2)]),
        "PASS_TO_PASS": json.dumps([f"p{i}" for i in range(19)]),
    }
    row.update(over)
    return row


def test_generic_derivations_for_uncurated_instance():
    f = fields_for_instance(_fake_row(), row_offset=461)
    assert f["row_url"].endswith("&offset=461&length=1")
    assert (f["repo_title"], f["module_name"]) == ("Sympy", "sympy")
    assert (f["fail_to_pass_count"], f["pass_to_pass_count"]) == ("2", "19")
    # gist = quoted issue title
    assert f["public_issue_gist"] == ('The public issue is: "Exception when '
                                      'multiplying BlockMatrix containing ZeroMatrix blocks".')
    # reconstructed instances get NO likely-files hint (file nudge dropped)
    assert f["likely_files_block"] == ""
    # generic questions keep the fixed 2..7 numbering and the 13236 version pattern
    lines = f["instance_questions_block"].splitlines()
    assert [l.split(".")[0] for l in lines] == ["2", "3", "4", "5", "6", "7"]
    assert "Sympy 1.5 / 1.6 / future 1.7" in lines[1]
    assert f["unrelated_behavior_bullet"].endswith(";")


def test_regression_note_threshold():
    light = fields_for_instance(_fake_row(), row_offset=0)["regression_note"]
    heavy_row = _fake_row(PASS_TO_PASS=json.dumps([f"p{i}" for i in range(REGRESSION_HEAVY_P2P)]))
    heavy = fields_for_instance(heavy_row, row_offset=0)["regression_note"]
    assert heavy.startswith("This is a regression-heavy task. A v2 patch can be worse")
    assert light == "A v2 patch can be worse than v1 if it fixes the desired behavior but breaks regressions."


def test_reconstructed_instances_have_no_likely_files_hint():
    """The likely-files block is curated only for 13236; every reconstructed
    instance gets an empty block (no file-selection nudge), regardless of what
    paths the public problem statement mentions."""
    paths_row = _fake_row()  # problem statement names blockmatrix.py + strategies
    nopaths_row = _fake_row(
        problem_statement="Something is wrong somewhere.\nNo paths here.\n")
    for row in (paths_row, nopaths_row):
        assert fields_for_instance(row, row_offset=0)["likely_files_block"] == ""


def test_counts_accept_lists_and_reject_garbage():
    row = _fake_row(FAIL_TO_PASS=["a", "b", "c"], PASS_TO_PASS=[])
    f = fields_for_instance(row, row_offset=0)
    assert (f["fail_to_pass_count"], f["pass_to_pass_count"]) == ("3", "0")
    with pytest.raises(ValueError, match="test list"):
        fields_for_instance(_fake_row(FAIL_TO_PASS='"x"'), row_offset=0)


# ------------------------------------------------- control-arm invariants ---

def test_control_has_no_fvk_or_formal_method_content():
    body = load_template(TEMPLATE_PATHS["review-control"])
    low = body.lower()
    for tok in ("fvk", "formal", "kit", "proof", "obligation", "invariant",
                "/formalize", "grosu", "specification"):
        assert tok not in low, f"forbidden token in review-control: {tok!r}"
    assert "/verify" not in body  # the slash command; plain 'verify' is fine
    assert not re.search(r"\bK\b", body), "K-framework reference in control"


def test_control_keeps_protocol_and_swaps_only_review_content():
    body = load_template(TEMPLATE_PATHS["review-control"])
    rep = load_template(TEMPLATE_PATHS["fvk-replicate"])
    # same five phases + Phase 0
    for n, name in enumerate(["Verify the Pre-Built Environment", "Generate v1 Without",
                              "Evaluate v1 Privately", "Review the v1 Patch",
                              "Generate v2 Using Review Guidance", "Evaluate v2 Privately"]):
        assert f"## Phase {n}: {name}" in body
    # the explicit non-regression requirement of the experiment design
    assert ("Explicitly check non-regression: identify what must remain unchanged, "
            "and verify the patch does not alter it.") in body
    # review artifacts replace the fvk/ ones
    assert "`review/FINDINGS.md`" in body and "`review/ITERATION_GUIDANCE.md`" in body
    assert "fvk/" not in body
    # discipline, aggregate-only feedback, and report scaffolding kept verbatim
    for verbatim in (
        "2. Do not inspect or use the gold `patch` field.",
        "8. Do not use private evaluator logs or hidden failure traces to guide v2.",
        # deviation (c): answer-key-relocated wording, shared verbatim by both arms
        ("Grading is performed by `scripts/private_eval.py`, which reports only "
         "aggregate pass/fail counts; the reference solution and hidden tests are "
         "not available in this workspace."),
        "    .venv/bin/python scripts/private_eval.py patches/solution_v1.patch v1",
        "Record only aggregate results in `reports/v1_score.md`:",
        "Use the same evaluator as v1.",
        "    FAIL_TO_PASS delta: A' - A",
        "1. What is the intended public behavior change?",
        "11. What changes are forbidden because they risk regressions?",
        "- preserve public regression behavior unless the issue explicitly requires changing it.",
    ):
        assert verbatim in body and verbatim in rep, verbatim
    # comparable length to the replicate template (same protocol, swapped Phase 3)
    assert 0.85 <= len(body) / len(rep) <= 1.15


# ------------------------------------------------ baseline-arm invariants ---

def test_baseline_is_single_pass_and_neutral():
    body = load_template(TEMPLATE_PATHS["baseline"])
    low = body.lower()
    assert "## Phase" not in body
    assert not re.search(r"\bv[12]\b", body), "baseline must not mention v1/v2"
    for tok in ("fvk", "kit", "review", "formal", "self-eval", "revise", "iterate"):
        assert tok not in low, f"non-neutral token in baseline: {tok!r}"
    assert "patches/solution.patch" in body
    assert "solution_v1" not in body and "solution_v2" not in body
    # INFO-PARITY: same shared ground rules as the other two arms, kept verbatim
    # where they apply (public info only; no gold patch; no hidden tests; no web
    # lookup of the original fix/PR/issue; no hidden tests / reference solution).
    for verbatim in (
        "1. You may use only public information for patch generation:",
        "2. Do not inspect or use the gold `patch` field.",
        "3. Do not manually inspect or use the hidden `test_patch` field.",
        "4. Do not inspect hidden test names, hidden assertions, or hidden failure traces.",
        "Generate your best patch using only public information.",
        "You may run public tests already present in the repo.",
        "Do not attempt to access hidden tests or a reference solution",
    ):
        assert verbatim in body, verbatim
    # no evaluator and no answer key in the baseline workspace (single-pass arm):
    # the agent-visible body references none of private_eval/, the full row, or
    # the private evaluator script.
    assert "scripts/private_eval.py" not in body
    assert "private_eval/" not in body
    assert "swebench_row_full.json" not in body
    assert "Do not manually open" not in body


# --------------------------------------------------- interface contract -----

CONTRACT_PATHS = {
    "fvk-replicate": ["benchmark/PROMPT.md", "benchmark/public_instance.json",
                      "private_eval/swebench_row_full.json", "scripts/private_eval.py",
                      "repo/", "patches/solution_v1.patch", "patches/solution_v2.patch",
                      "reports/", "fvk/", "formal-verification-kit/"],
    "review-control": ["benchmark/PROMPT.md", "benchmark/public_instance.json",
                       "private_eval/swebench_row_full.json", "scripts/private_eval.py",
                       "repo/", "patches/solution_v1.patch", "patches/solution_v2.patch",
                       "reports/", "review/"],
    "baseline": ["benchmark/PROMPT.md", "benchmark/public_instance.json",
                 "repo/", "patches/solution.patch", "reports/"],
}


def test_templates_reference_the_contract_workspace_paths():
    for arm, paths in CONTRACT_PATHS.items():
        body = load_template(TEMPLATE_PATHS[arm])
        for p in paths:
            assert p in body, f"{arm} missing contract path {p}"
    assert "formal-verification-kit/" not in load_template(TEMPLATE_PATHS["review-control"])
    assert "formal-verification-kit/" not in load_template(TEMPLATE_PATHS["baseline"])


# ------------------------------------------------------------- previews -----

def test_committed_previews_match_runtime_instantiation_for_13236():
    """preview/ files are review copies; they must equal what the runner will
    build. Checked for 13236 (the instance with a no-network fixture row)."""
    fields = _fields_13236()
    for arm in ARMS:
        preview = PREVIEWS / arm / "astropy__astropy-13236.md"
        assert preview.exists(), f"missing preview {preview}"
        assert preview.read_text() == _instantiated(arm, fields), arm


def test_previews_exist_for_all_10_pinned_instances_and_3_arms():
    pinned = ["astropy__astropy-12907", "astropy__astropy-13033", "astropy__astropy-13236",
              "astropy__astropy-13398", "astropy__astropy-13453", "astropy__astropy-13579",
              "astropy__astropy-13977", "astropy__astropy-14096", "astropy__astropy-14182",
              "astropy__astropy-14309"]
    for arm in ARMS:
        for iid in pinned:
            assert (PREVIEWS / arm / f"{iid}.md").exists(), (arm, iid)


# ============================================================================
# v2 multi-repo templates + generalized import name (45-instance run).
# ============================================================================

from fvk_bench.agentic_prompts import AGENTIC_DIR  # noqa: E402
from fvk_bench.env_specs import import_name_for     # noqa: E402

V2_PATHS = {arm: AGENTIC_DIR / f"{arm}-v2.md" for arm in ARMS}

# One representative row per repo of the Grigore-set (public fields only; values
# are plausible but the test only exercises string substitution, never network).
_REPO_ROWS = {
    "django/django": dict(instance_id="django__django-10554", version="3.2"),
    "sympy/sympy": dict(instance_id="sympy__sympy-17630", version="1.5"),
    "sphinx-doc/sphinx": dict(instance_id="sphinx-doc__sphinx-9461", version="4.2"),
    "astropy/astropy": dict(instance_id="astropy__astropy-13398", version="5.0"),
    "pytest-dev/pytest": dict(instance_id="pytest-dev__pytest-5787", version="5.1"),
    "pydata/xarray": dict(instance_id="pydata__xarray-3993", version="0.12"),
    "pylint-dev/pylint": dict(instance_id="pylint-dev__pylint-4551", version="2.9"),
    "scikit-learn/scikit-learn": dict(instance_id="scikit-learn__scikit-learn-25102",
                                      version="1.3"),
}


def _repo_row(repo: str) -> dict:
    meta = _REPO_ROWS[repo]
    return {
        "instance_id": meta["instance_id"],
        "repo": repo,
        "base_commit": "0" * 40,
        "version": meta["version"],
        "difficulty": "15 min - 1 hour",
        "problem_statement": f"Something is wrong in {repo}.\nSee the issue.\n",
        "FAIL_TO_PASS": json.dumps(["t0", "t1"]),
        "PASS_TO_PASS": json.dumps([f"p{i}" for i in range(5)]),
    }


def test_v2_templates_exist_for_all_three_arms():
    for arm in ARMS:
        assert V2_PATHS[arm].exists(), f"missing v2 template {V2_PATHS[arm]}"


def test_v2_templates_instantiate_for_one_instance_per_repo():
    """String-substitution only (row_offset given so no HF lookup). Every
    placeholder resolves and the import-name line is repo-correct."""
    pat = re.compile(r"\{([a-z][a-z0-9_]*)\}")
    for repo in _REPO_ROWS:
        row = _repo_row(repo)
        fields = fields_for_instance(row, row_offset=0)
        for arm in ARMS:
            out = instantiate(load_template(V2_PATHS[arm]), fields)
            leftover = set(pat.findall(out)) & set(fields)
            assert not leftover, (arm, repo, leftover)
            # the env-verify line imports the correct top-level module
            assert f"import {import_name_for(repo)}" in out, (arm, repo)


def test_v2_module_name_is_generalized_import_name():
    # scikit-learn is the case the trailing-segment heuristic gets wrong; v2 must
    # emit `import sklearn`, not `import scikit-learn`.
    row = _repo_row("scikit-learn/scikit-learn")
    fields = fields_for_instance(row, row_offset=0)
    assert fields["module_name"] == "sklearn"
    for arm in ARMS:
        out = instantiate(load_template(V2_PATHS[arm]), fields)
        assert "import sklearn" in out
        assert "import scikit-learn" not in out


def test_v2_phase0_is_agent_self_build_not_prebuilt_verify():
    """The ONLY substantive change from v1: Phase 0 / Workspace Setup tells the
    agent to set up (or verify) its OWN env, and encourages ad-hoc local tests."""
    for arm in ARMS:
        body = load_template(V2_PATHS[arm])
        low = body.lower()
        # self-build cue + the no-clone/no-remote leak-safety guard
        assert "do not add a git remote" in low, arm
        assert "may already be staged" in low, arm
        assert "python3 -m venv .venv" in body, arm
        assert "pip install -e ." in body, arm
        # ad-hoc local test running is explicit
        assert ("run the repo's own tests" in low
                or "running the repo's own public tests" in low
                or "freely throughout this task" in low), arm


def test_v2_phased_templates_keep_protocol_and_discipline():
    """v2 fvk/review keep the 5-phase protocol, the benchmark-discipline block,
    the answer-key-out-of-workspace line, and the final report — only Phase 0
    changed."""
    for arm in ("fvk-replicate", "review-control"):
        body = load_template(V2_PATHS[arm])
        for verbatim in (
            "2. Do not inspect or use the gold `patch` field.",
            "8. Do not use private evaluator logs or hidden failure traces to guide v2.",
            ("Grading is performed by `scripts/private_eval.py`, which reports only "
             "aggregate pass/fail counts; the reference solution and hidden tests are "
             "not available in this workspace."),
            "    .venv/bin/python scripts/private_eval.py patches/solution_v1.patch v1",
            "## Phase 5: Evaluate v2 Privately",
            "## Final Report",
        ):
            assert verbatim in body, (arm, verbatim)
        # all five phases + Phase 0 present
        for n in range(0, 6):
            assert f"## Phase {n}:" in body, (arm, n)


def test_v2_fvk_has_kit_and_review_has_no_fvk():
    fvk = load_template(V2_PATHS["fvk-replicate"])
    rev = load_template(V2_PATHS["review-control"])
    assert "formal-verification-kit/" in fvk
    # control arm stays free of FVK/formal-method content (same rule as v1)
    low = rev.lower()
    for tok in ("fvk", "formal", "kit", "proof", "obligation", "/formalize", "grosu"):
        assert tok not in low, f"forbidden token in review-control-v2: {tok!r}"
    assert "`review/FINDINGS.md`" in rev


def test_v2_baseline_is_single_pass_and_neutral():
    body = load_template(V2_PATHS["baseline"])
    low = body.lower()
    assert "## Phase" not in body
    assert not re.search(r"\bv[12]\b", body), "baseline-v2 must not mention v1/v2"
    for tok in ("fvk", "kit", "review", "formal", "self-eval", "revise", "iterate"):
        assert tok not in low, f"non-neutral token in baseline-v2: {tok!r}"
    assert "patches/solution.patch" in body
    assert "scripts/private_eval.py" not in body
    # still self-builds its env
    assert "python3 -m venv .venv" in body


def test_v1_astropy_path_unchanged_by_generalization():
    """Generalizing module_name via the import map must not perturb the curated
    astropy-13236 fidelity: module_name/repo_title are still astropy/Astropy."""
    f = _fields_13236()
    assert f["module_name"] == "astropy"
    assert f["repo_title"] == "Astropy"
    # and the frozen residual-diff fidelity test (defined above) still holds —
    # re-assert the core field here as a guard against import-map drift.
    assert import_name_for("astropy/astropy") == "astropy"


def test_v2_phase0_restores_grigores_verbatim_install_recipe():
    """Owner decision (1): Phase 0's fallback recipe is Grigore's verbatim
    sympy-sample Phase 0 (uv venv 3.9 || 3.11 || stdlib venv; pip bootstrap;
    editable install; pytest; 'Install enough public test dependencies'),
    adapted only by (a) installing the STAGED repo and (b) the
    SETUPTOOLS_SCM_PRETEND_VERSION export compensating for our
    truncated-history staging. Identical across all three arms (info parity).
    """
    his = (AGENTIC_DIR / "source" / "sympy__sympy-17630_fvk_prompt.md").read_text()
    # the recipe lines that must come from his prompt verbatim
    for verbatim in (
        "uv venv --python 3.9 .venv || uv venv --python 3.11 .venv || python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install -U pip setuptools wheel",
        "python -m pip install pytest || true",
        "Install enough public test dependencies to run relevant tests.",
    ):
        assert verbatim in his, f"not actually in his prompt: {verbatim!r}"
    blocks = {}
    for arm in ARMS:
        body = load_template(V2_PATHS[arm])
        for verbatim in (
            "uv venv --python 3.9 .venv || uv venv --python 3.11 .venv || python3 -m venv .venv",
            "source .venv/bin/activate",
            "python -m pip install -U pip setuptools wheel",
            "python -m pip install pytest || true",
            "Install enough public test dependencies to run relevant tests.",
            # the two declared adaptations
            "(cd repo && python -m pip install -e .) || true",
            "export SETUPTOOLS_SCM_PRETEND_VERSION={version}",
            # the owner-specified prestaged-venv line
            "If `.venv/` is already staged and works, verify it and use it.",
        ):
            assert verbatim in body, (arm, verbatim)
        # info parity: the whole fallback block is byte-identical across arms
        start = body.index("If `.venv/` is already staged and works")
        end = body.index("Install enough public test dependencies")
        blocks[arm] = body[start:end]
    assert blocks["fvk-replicate"] == blocks["review-control"] == blocks["baseline"]


def test_v2_phased_grading_line_notes_official_image():
    """Decision (3) disclosure: the deviation-(c) grading line carries the
    official-evaluation-environment note in both phased v2 arms (baseline has
    no evaluator and must not mention grading at all)."""
    note = ("Its scores are computed inside the instance's official SWE-bench "
            "evaluation environment, so they match the official grader.")
    for arm in ("fvk-replicate", "review-control"):
        assert note in load_template(V2_PATHS[arm]), arm
    base = load_template(V2_PATHS["baseline"])
    assert "Grading" not in base and "official grader" not in base


def test_v2_previews_and_control_diff_exist():
    """Committed v2 review artifacts: one preview per Grigore-set repo per arm
    (8 x 3) and the v2 control diff. Regenerate via
    scripts/build_agentic_previews.py; content correctness is covered by the
    instantiation tests above (previews are for human review)."""
    per_repo = [
        "django__django-10554", "sympy__sympy-17630", "sphinx-doc__sphinx-9461",
        "astropy__astropy-13398", "pytest-dev__pytest-5787", "pydata__xarray-3993",
        "pylint-dev__pylint-4551", "scikit-learn__scikit-learn-25102",
    ]
    for arm in ARMS:
        for iid in per_repo:
            assert (PREVIEWS / f"{arm}-v2" / f"{iid}.md").exists(), (arm, iid)
    diff = (AGENTIC_DIR / "CONTROL_DIFF-v2.md").read_text()
    assert diff.startswith("# fvk-replicate-v2 vs review-control-v2")
    # the v2-shared Phase 0 must NOT appear in the arm diff (identical by design)
    assert "uv venv --python 3.9" not in diff
    assert "SETUPTOOLS_SCM_PRETEND_VERSION" not in diff
