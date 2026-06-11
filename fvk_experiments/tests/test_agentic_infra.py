"""Agentic (claude-code) infrastructure: config schema, workspace builder,
private evaluator contract, transcript audit, transition tables.

Unit tests are hermetic: the "benchmark repo" is a local fixture git repo built
in tmp, no venv is built (the evaluator gets a shim python), and no network or
claude session is ever touched. The one end-to-end check (real astropy
workspace + gold patch through the private evaluator) is opt-in via
AGENTIC_IT=1 because it clones astropy and builds a real env.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench import agentic
from fvk_bench.agentic import arm_kind_for_tag, build_workspace, workspaces_root
from fvk_bench.agents import claude_code, profile
from fvk_bench.agents.claude_code import (audit_transcript, build_claude_argv,
                                          harvest_workspace, parse_stream,
                                          session_status)
from fvk_bench.agents.profile import ensure_sealed_home, sealed_env
from fvk_bench.config import EXP_ROOT, REPO_ROOT, load_config
from fvk_bench.report import parse_claimed_aggregates, render_transition_table

STREAM_FIXTURE = Path(__file__).parent / "fixtures" / "claude_stream_smoke.jsonl"
IID = "tinypkg__tinypkg-1"
F2P_ID = "tests/test_added.py::test_add_fixed_behavior"
P2P_ID = "tests/test_existing.py::test_mul"
# Deliberately truncated at the parametrization space, exactly as SWE-bench's
# whitespace-split dataset lists arrive (e.g. "...test_non_mapping_init[ceci"):
# the evaluator must still select + count it.
P2P_TRUNCATED_ID = "tests/test_existing.py::test_param[ceci"

_EXISTING_TEST_BASE = """\
import pytest

from tinypkg import mul


def test_mul():
    assert mul(2, 3) == 6


@pytest.mark.parametrize("label", ["ceci n'est pas une mapping"])
def test_param(label):
    assert mul(1, 1) == 1
"""

# Like real SWE-bench rows, the hidden test patch touches every file the
# benchmark will execute (the P2P file gets an extra assert) — the evaluator's
# reset-to-base semantics for test files rely on that, exactly like the harness.
# (Built by concatenation so blank context lines keep their leading space.)
TEST_PATCH = (
    "diff --git a/tests/test_added.py b/tests/test_added.py\n"
    "new file mode 100644\n"
    "--- /dev/null\n"
    "+++ b/tests/test_added.py\n"
    "@@ -0,0 +1,6 @@\n"
    "+from tinypkg import add\n"
    "+\n"
    "+\n"
    "+def test_add_fixed_behavior():\n"
    "+    assert add(2, 3) == 5\n"
    "+    assert add(0, 0) == 0\n"
    "diff --git a/tests/test_existing.py b/tests/test_existing.py\n"
    "--- a/tests/test_existing.py\n"
    "+++ b/tests/test_existing.py\n"
    "@@ -5,5 +5,6 @@\n"
    " \n"
    " def test_mul():\n"
    "     assert mul(2, 3) == 6\n"
    "+    assert mul(1, 5) == 5\n"
    " \n"
    " \n"
)

# Pre-creates the hidden test file with a vacuous body AND sabotages the
# existing P2P test file — the evaluator must void both (base + test_patch wins).
CHEAT_PATCH = (
    "diff --git a/tests/test_added.py b/tests/test_added.py\n"
    "new file mode 100644\n"
    "--- /dev/null\n"
    "+++ b/tests/test_added.py\n"
    "@@ -0,0 +1,2 @@\n"
    "+def test_add_fixed_behavior():\n"
    "+    pass\n"
    "diff --git a/tests/test_existing.py b/tests/test_existing.py\n"
    "--- a/tests/test_existing.py\n"
    "+++ b/tests/test_existing.py\n"
    "@@ -1,12 +1,1 @@\n"
    "-import pytest\n"
    "-\n"
    "-from tinypkg import mul\n"
    "-\n"
    "-\n"
    "-def test_mul():\n"
    "-    assert mul(2, 3) == 6\n"
    "-\n"
    "-\n"
    "-@pytest.mark.parametrize(\"label\", [\"ceci n'est pas une mapping\"])\n"
    "-def test_param(label):\n"
    "-    assert mul(1, 1) == 1\n"
    "+raise RuntimeError(\"sabotaged\")\n"
)


# ---------------------------------------------------------------------------
# helpers / fixtures
# ---------------------------------------------------------------------------

def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _git_out(*args, cwd) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture(scope="module")
def fixture_repo(tmp_path_factory):
    """Local 'upstream': base commit (buggy) + a LATER fix commit that must be
    physically absent from built workspaces."""
    src = tmp_path_factory.mktemp("origin") / "tinypkg"
    src.mkdir()
    (src / "tinypkg.py").write_text(
        "def add(a, b):\n    return a - b  # BUG\n\n\ndef mul(a, b):\n    return a * b\n")
    (src / "tests").mkdir()
    (src / "tests" / "test_existing.py").write_text(_EXISTING_TEST_BASE)
    (src / "README.md").write_text("tiny fixture package\n")
    _git("init", "-q", cwd=src)
    _git("add", "-A", cwd=src)
    _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", cwd=src)
    base = _git_out("rev-parse", "HEAD", cwd=src)
    (src / "tinypkg.py").write_text(
        "def add(a, b):\n    return a + b\n\n\ndef mul(a, b):\n    return a * b\n")
    _git("add", "-A", cwd=src)
    _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "the future fix",
         cwd=src)
    fix = _git_out("rev-parse", "HEAD", cwd=src)
    gold = subprocess.run(["git", "diff", base, fix], cwd=src, check=True,
                          capture_output=True, text=True).stdout
    return {"path": src, "base": base, "fix": fix, "gold_patch": gold}


@pytest.fixture(scope="module")
def fixture_kit(tmp_path_factory):
    kit = tmp_path_factory.mktemp("kitsrc") / "formal-verification-kit"
    (kit / "knowledge").mkdir(parents=True)
    (kit / "README.md").write_text("# kit (fixture)\n")
    (kit / "knowledge" / "k.md").write_text("verify all the things\n")
    _git("init", "-q", cwd=kit)
    _git("add", "-A", cwd=kit)
    _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "kit", cwd=kit)
    return {"path": kit, "sha": _git_out("rev-parse", "HEAD", cwd=kit)}


def _fake_row(fr) -> dict:
    return {
        "instance_id": IID,
        "repo": "fixture/tinypkg",
        "base_commit": fr["base"],
        "version": "0.1",
        "problem_statement": "add() subtracts instead of adding two numbers.",
        "patch": fr["gold_patch"],
        "test_patch": TEST_PATCH,
        "FAIL_TO_PASS": json.dumps([F2P_ID]),
        "PASS_TO_PASS": json.dumps([P2P_ID, P2P_TRUNCATED_ID]),
        "difficulty": "<15 min fix",
        "created_at": "2026-01-01T00:00:00Z",
        "hints_text": "",
        "environment_setup_commit": fr["base"],
    }


def _cc_cfg(tmp_path: Path, tag: str, iid: str = IID):
    template = tmp_path / f"{tag}.md"
    if not template.exists():
        template.write_text(f"---\ntag: {tag}\n---\nDo the task: {{problem_statement}}\n")
    p = tmp_path / f"cfg-{tag}.yaml"
    p.write_text(
        f"run_name: test-cc-{tag}\n"
        f"tag: {tag}\n"
        f"dataset:\n  instance_ids: [{iid}]\n"
        f"model:\n  provider: claude-code\n  name: claude-code-opus-4.6\n"
        f"  cc_model: claude-opus-4-6\n"
        f"prompt:\n  system_prompt: {template}\n")
    return load_config(p)


def _build(tmp_path, fixture_repo, fixture_kit, arm_kind: str, tag: str | None = None):
    cfg = _cc_cfg(tmp_path, tag or arm_kind)
    run_dir = tmp_path / "runs" / f"r-{arm_kind}"
    run_dir.mkdir(parents=True, exist_ok=True)
    ws = build_workspace(cfg, run_dir, _fake_row(fixture_repo), arm_kind,
                         repo_src=str(fixture_repo["path"]),
                         kit_src=fixture_kit["path"], build_venv=False,
                         workspaces_dir=tmp_path / "workspaces")
    return cfg, run_dir, ws


@pytest.fixture(scope="module")
def phased_ws(tmp_path_factory, fixture_repo, fixture_kit):
    tmp = tmp_path_factory.mktemp("ws-fvk")
    _, _, ws = _build(tmp, fixture_repo, fixture_kit, "fvk-replicate")
    # Evaluator contract tests need a runnable .venv python (workspace root,
    # where the templates and real builds put it): shim to the test interpreter
    # (which has pytest) instead of building a real venv.
    vbin = ws / ".venv" / "bin"
    vbin.mkdir(parents=True)
    shim = vbin / "python"
    shim.write_text(f"#!/bin/sh\nexec {sys.executable} \"$@\"\n")
    shim.chmod(0o755)
    return ws


# ---------------------------------------------------------------------------
# 1. config schema + labels
# ---------------------------------------------------------------------------

def test_claude_code_config_loads_and_labels_all_arms(tmp_path):
    for tag in ("fvk-replicate", "review-control", "baseline"):
        cfg = _cc_cfg(tmp_path, tag)
        assert cfg.model.provider == "claude-code"
        assert cfg.model.cc_model == "claude-opus-4-6"
        assert cfg.model.max_turns == 200          # default
        assert cfg.model.session_timeout_s == 5400  # default
        assert cfg.arm_tag() == tag
        # claude-code labels carry no -think suffix
        assert cfg.model_label() == f"claude-code-opus-4.6__{tag}"
        assert arm_kind_for_tag(cfg.arm_tag()) == tag


def test_claude_code_requires_cc_model(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("run_name: x\ndataset:\n  instance_ids: [a]\n"
                 "model:\n  provider: claude-code\n  name: claude-code-opus-4.6\n")
    with pytest.raises(ValueError, match="cc_model"):
        load_config(p)


def test_cc_model_rejected_for_other_providers(tmp_path):
    p = tmp_path / "bad2.yaml"
    p.write_text("run_name: x\ndataset:\n  instance_ids: [a]\n"
                 "model:\n  cc_model: claude-opus-4-6\n")
    with pytest.raises(ValueError, match="cc_model"):
        load_config(p)


def test_arm_kind_mapping_and_suffixes():
    assert arm_kind_for_tag("fvk-replicate-v2") == "fvk-replicate"
    assert arm_kind_for_tag("review-control") == "review-control"
    assert arm_kind_for_tag("baseline-replicate-v7") == "baseline"
    with pytest.raises(ValueError, match="arm kind"):
        arm_kind_for_tag("jointembed-v6")


_TPL_DIR = EXP_ROOT / "prompts" / "agentic"
_TPLS = ["fvk-replicate.md", "review-control.md", "baseline.md"]


@pytest.mark.skipif(not all((_TPL_DIR / t).exists() for t in _TPLS),
                    reason="agentic prompt templates not landed yet (parallel workstream)")
def test_real_agentic_configs_load():
    for arm in ("fvk-replicate", "review-control", "baseline"):
        cfg = load_config(EXP_ROOT / "configs" /
                          f"astropy10__claude-code-opus46__{arm}.yaml")
        assert cfg.arm_tag() == arm
        assert cfg.model_label() == f"claude-code-opus-4.6__{arm}"
        assert len(cfg.dataset.instance_ids) == 10


# ---------------------------------------------------------------------------
# 2. workspace builder (fixture repo, no network, no venv)
# ---------------------------------------------------------------------------

def test_phased_workspace_layout(phased_ws):
    ws = phased_ws
    for d in ("benchmark", "repo", "patches", "reports", "private_eval",
              "scripts", "fvk", "formal-verification-kit"):
        assert (ws / d).is_dir(), d
    assert (ws / "benchmark" / "public_instance.json").is_file()
    assert (ws / "benchmark" / "PROMPT.md").is_file()
    assert (ws / "scripts" / "private_eval.py").is_file()
    assert (ws / "manifest.json").is_file()
    assert not (ws / "review").exists()
    # ANSWER-KEY ISOLATION: the full row is NOT in the workspace; the only thing
    # in private_eval/ is the (eventual) eval log, never the row.
    assert not (ws / "private_eval" / "swebench_row_full.json").exists()
    assert not (ws / "private_eval" / "row.json").exists()
    row_path = Path(json.loads((ws / "manifest.json").read_text())["row_path"])
    assert row_path.is_file()
    assert ws not in row_path.parents  # outside the workspace
    assert row_path.name == "row.json"


def test_public_instance_has_public_fields_only(phased_ws):
    raw = (phased_ws / "benchmark" / "public_instance.json").read_text()
    pub = json.loads(raw)
    # field style mirrors prompts/agentic/source/sympy__sympy-17630_public_instance.json
    assert pub["instance_id"] == IID
    assert pub["dataset"] == "princeton-nlp/SWE-bench_Verified"
    assert pub["split"] == "test"
    assert pub["repo_url"] == "https://github.com/fixture/tinypkg.git"
    assert pub["base_commit_url"].endswith(pub["base_commit"])
    assert pub["hints_text"] == ""
    assert pub["FAIL_TO_PASS_count"] == 1 and pub["PASS_TO_PASS_count"] == 2
    for secret in ("patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"):
        assert secret not in pub
    # no hidden test NAMES anywhere in the public payload
    assert "test_add_fixed_behavior" not in raw and "test_mul" not in raw
    assert "test_param" not in raw
    prompt = (phased_ws / "benchmark" / "PROMPT.md").read_text()
    assert prompt.startswith(f"# SWE-bench Verified instance {IID}")
    assert "- repo: fixture/tinypkg" in prompt
    assert "## Problem statement" in prompt and "## Hints / discussion" in prompt
    assert "Evaluator shape: FAIL_TO_PASS 1, PASS_TO_PASS 2" in prompt
    assert "add() subtracts" in prompt


def test_repo_is_history_truncated_and_fix_absent(phased_ws, fixture_repo):
    repo = phased_ws / "repo"
    log = _git_out("log", "--oneline", cwd=repo)
    assert len(log.splitlines()) == 1  # single synthetic base commit
    # the future fix commit object is PHYSICALLY absent
    gone = subprocess.run(["git", "cat-file", "-e", fixture_repo["fix"]],
                          cwd=repo, capture_output=True)
    assert gone.returncode != 0
    assert "fvk-base" in _git_out("tag", cwd=repo)
    assert "a - b" in (repo / "tinypkg.py").read_text()  # tree @ base (buggy)
    assert _git_out("status", "--porcelain", cwd=repo) == ""  # clean for git diff


def test_baseline_workspace_has_no_private_eval(tmp_path, fixture_repo, fixture_kit):
    _, _, ws = _build(tmp_path, fixture_repo, fixture_kit, "baseline")
    assert (ws / "patches").is_dir() and (ws / "reports").is_dir()
    for d in ("private_eval", "scripts", "fvk", "review", "formal-verification-kit"):
        assert not (ws / d).exists(), d


def test_review_control_gets_review_dir_but_no_kit(tmp_path, fixture_repo, fixture_kit):
    _, run_dir, ws = _build(tmp_path, fixture_repo, fixture_kit, "review-control")
    assert (ws / "review").is_dir()
    assert (ws / "scripts" / "private_eval.py").is_file()
    # row out-of-workspace, under the run dir
    assert not (ws / "private_eval" / "swebench_row_full.json").exists()
    assert (run_dir / "private" / IID / "row.json").is_file()
    assert not (ws / "fvk").exists()
    assert not (ws / "formal-verification-kit").exists()


def test_manifest_records_shas_and_provenance(phased_ws, fixture_repo, fixture_kit):
    m = json.loads((phased_ws / "manifest.json").read_text())
    assert m["base_commit"] == fixture_repo["base"]
    assert m["kit_commit"] == fixture_kit["sha"] and m["kit_dirty"] is False
    assert m["arm_kind"] == "fvk-replicate"
    staged = m["staged"]
    # the row is NO LONGER a staged workspace file
    assert "private_eval/swebench_row_full.json" not in staged
    for path in ("benchmark/public_instance.json", "benchmark/PROMPT.md",
                 "scripts/private_eval.py"):
        assert len(staged[path]) == 64  # sha256 hex
    # provenance for the out-of-workspace row
    assert len(m["row_sha256"]) == 64
    assert m["row_path"].endswith(f"/private/{IID}/row.json")
    assert m["built_at"]


def test_staged_row_lives_outside_workspace_and_normalizes_lists(phased_ws):
    # The full row is written OUTSIDE the workspace (manifest records the path);
    # nothing in the workspace contains it.
    m = json.loads((phased_ws / "manifest.json").read_text())
    row_path = Path(m["row_path"])
    assert phased_ws not in row_path.parents
    row = json.loads(row_path.read_text())
    assert row["FAIL_TO_PASS"] == [F2P_ID]  # lists, not JSON strings
    assert row["PASS_TO_PASS"] == [P2P_ID, P2P_TRUNCATED_ID]
    assert row["patch"] and row["test_patch"]  # full row for the evaluator


# ---------------------------------------------------------------------------
# 3. private evaluator output contract
# ---------------------------------------------------------------------------

def _eval(ws: Path, patch_text: str, tag: str = "v1"):
    pf = ws / "patches" / f"contract-{tag}.patch"
    pf.write_text(patch_text)
    return subprocess.run([sys.executable, str(ws / "scripts" / "private_eval.py"),
                           str(pf), tag], capture_output=True, text=True, timeout=300)


def _assert_no_test_names(proc):
    for stream in (proc.stdout, proc.stderr):
        assert "test_add" not in stream and "test_mul" not in stream
        assert "test_param" not in stream and "ceci" not in stream
        assert "tests/" not in stream and "Traceback" not in stream


def test_private_eval_gold_patch_three_line_contract(phased_ws, fixture_repo):
    # P2P includes a dataset-style whitespace-truncated parametrized id — the
    # evaluator must still run and count it (2/2), like the official harness.
    p = _eval(phased_ws, fixture_repo["gold_patch"], "gold")
    assert p.returncode == 0, p.stderr
    assert p.stdout.splitlines() == [
        "FAIL_TO_PASS 1/1", "PASS_TO_PASS 2/2", "resolved: true"]
    _assert_no_test_names(p)


def test_private_eval_empty_patch_runs_base(phased_ws):
    p = _eval(phased_ws, "", "empty")
    assert p.returncode == 0
    assert p.stdout.splitlines() == [
        "FAIL_TO_PASS 0/1", "PASS_TO_PASS 2/2", "resolved: false"]
    _assert_no_test_names(p)


def test_private_eval_unappliable_patch_reports_zeros(phased_ws):
    bad = ("diff --git a/nope.py b/nope.py\n--- a/nope.py\n+++ b/nope.py\n"
           "@@ -1,1 +1,1 @@\n-x\n+y\n")
    p = _eval(phased_ws, bad, "bad")
    assert p.returncode == 0
    assert p.stdout.splitlines() == [
        "FAIL_TO_PASS 0/1", "PASS_TO_PASS 0/2", "resolved: false"]
    assert "did not apply" in p.stderr
    _assert_no_test_names(p)


def test_private_eval_voids_tampered_tests(phased_ws):
    # Cheating patch: vacuous fake hidden test + sabotaged P2P file. The
    # evaluator grades base + hidden test_patch, so the cheat must not stick.
    p = _eval(phased_ws, CHEAT_PATCH, "cheat")
    assert p.returncode == 0
    assert p.stdout.splitlines() == [
        "FAIL_TO_PASS 0/1", "PASS_TO_PASS 2/2", "resolved: false"]
    _assert_no_test_names(p)


def test_private_eval_infra_error_is_generic_and_nonzero(phased_ws):
    p = subprocess.run([sys.executable, str(phased_ws / "scripts" / "private_eval.py"),
                        str(phased_ws / "patches" / "does-not-exist.patch"), "x"],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode != 0
    assert p.stdout == ""
    assert "internal error" in p.stderr
    _assert_no_test_names(p)


def test_private_eval_logs_aggregates_only(phased_ws):
    log = (phased_ws / "private_eval" / "eval_log.jsonl").read_text()
    assert "FAIL_TO_PASS" in log
    assert "test_add" not in log and "test_mul" not in log


# ---------------------------------------------------------------------------
# 4. claude CLI invocation + transcript audit
# ---------------------------------------------------------------------------

def test_claude_argv_exact_flags(tmp_path):
    cfg = _cc_cfg(tmp_path, "baseline")
    assert build_claude_argv("/fake/claude", cfg) == [
        "/fake/claude", "-p",
        "--model", "claude-opus-4-6",
        "--output-format", "stream-json",
        "--verbose",
        "--max-turns", "200",
        "--disallowedTools", "WebSearch,WebFetch",
        "--permission-mode", "bypassPermissions",
    ]


def test_stream_fixture_audit():
    events = parse_stream(STREAM_FIXTURE)
    assert events[0]["type"] == "system" and events[-1]["type"] == "result"
    audit = audit_transcript(events, [F2P_ID])

    assert audit["counts"]["denied_tool_attempts"] == 1
    assert audit["denied_tool_attempts"][0]["tool"] == "WebFetch"
    assert audit["counts"]["network_bash_commands"] == 1
    assert "curl" in audit["network_bash_commands"][0]
    assert audit["private_row_reads"] == ["Read: /ws/private_eval/swebench_row_full.json"]
    assert audit["private_eval_script_edits"] == ["Edit: /ws/scripts/private_eval.py"]
    assert audit["private_eval_invocations"] == 1
    # name leaked once BEFORE the first in-session eval output, mentioned twice total
    assert audit["counts"]["f2p_leaks_before_eval"] == 1
    assert audit["f2p_leaks_before_eval"][0]["name"] == F2P_ID
    assert "hidden test" in audit["f2p_leaks_before_eval"][0]["line"]
    assert audit["f2p_mentions_total"] == 2
    assert audit["num_turns"] == 6
    assert audit["duration_ms"] == 123456
    assert audit["usage"]["input_tokens"] == 1000
    assert audit["total_cost_usd"] == 1.23


def test_clean_transcript_audits_clean():
    events = [
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "Reading the code now."},
            {"type": "tool_use", "name": "Bash",
             "input": {"command": "python scripts/private_eval.py patches/p.patch v1"}}]}},
        {"type": "result", "subtype": "success", "num_turns": 1},
    ]
    audit = audit_transcript(events, [F2P_ID])
    assert audit["counts"] == {"denied_tool_attempts": 0, "network_bash_commands": 0,
                               "private_row_reads": 0, "private_eval_script_edits": 0,
                               "f2p_leaks_before_eval": 0}
    assert audit["private_eval_invocations"] == 1


def test_session_status_mapping():
    ok = [{"type": "assistant"}, {"type": "result", "subtype": "success"}]
    cap = [{"type": "assistant"}, {"type": "result", "subtype": "error_max_turns"}]
    assert session_status(ok, 0, False) == "ok"
    assert session_status(cap, 0, False) == "turn_cap"
    assert session_status(ok, 0, True) == "timeout"
    assert session_status([], 1, False) == "cli_error"


# ---------------------------------------------------------------------------
# 5. harvest + run_instance glue (mocked session + mocked prompt module)
# ---------------------------------------------------------------------------

def _mk_ws_outputs(ws: Path, v1: str | None, v2: str | None):
    (ws / "patches").mkdir(parents=True, exist_ok=True)
    (ws / "reports").mkdir(parents=True, exist_ok=True)
    if v1 is not None:
        (ws / "patches" / "solution_v1.patch").write_text(v1)
    if v2 is not None:
        (ws / "patches" / "solution_v2.patch").write_text(v2)
    (ws / "reports" / "final_report.md").write_text(
        "## Self-eval\nFAIL_TO_PASS 1/1\nPASS_TO_PASS 1/1\nresolved: true\n")
    (ws / "manifest.json").write_text("{}")


def test_harvest_prefers_v2_and_keeps_v1(tmp_path):
    ws, art = tmp_path / "ws", tmp_path / "art"
    _mk_ws_outputs(ws, v1="V1DIFF\n", v2="V2DIFF\n")
    h = harvest_workspace(ws, "fvk-replicate", art)
    assert h["final_source"] == "v2"
    assert h["final_patch"] == "V2DIFF\n" and h["patch_v1"] == "V1DIFF\n"
    assert (art / "patches" / "solution_v1.patch").exists()
    assert (art / "reports" / "final_report.md").exists()
    assert (art / "manifest.json").exists()


def test_harvest_falls_back_to_v1_then_empty(tmp_path):
    ws1 = tmp_path / "ws1"
    _mk_ws_outputs(ws1, v1="V1ONLY\n", v2=None)
    h1 = harvest_workspace(ws1, "review-control", tmp_path / "a1")
    assert h1["final_source"] == "v1" and h1["final_patch"] == "V1ONLY\n"
    ws2 = tmp_path / "ws2"
    _mk_ws_outputs(ws2, v1=None, v2=None)
    h2 = harvest_workspace(ws2, "review-control", tmp_path / "a2")
    assert h2["final_source"] == "empty" and h2["final_patch"] == ""


def test_harvest_baseline_single_solution(tmp_path):
    ws = tmp_path / "ws"
    (ws / "patches").mkdir(parents=True)
    (ws / "patches" / "solution.patch").write_text("SOLO\n")
    h = harvest_workspace(ws, "baseline", tmp_path / "art")
    assert h["final_source"] == "solution" and h["final_patch"] == "SOLO\n"
    assert h["patch_v1"] is None and h["patch_v2"] is None


def test_run_instance_glue(tmp_path, monkeypatch, fixture_repo, fixture_kit):
    """End-to-end run_instance with a mocked claude session and a mocked
    agentic_prompts module (the parallel-workstream interface contract)."""
    cfg = _cc_cfg(tmp_path, "fvk-replicate")
    run_dir = tmp_path / "runs" / "glue"
    for sub in ("raw", "prompts", "eval", "artifacts", "audit"):
        (run_dir / sub).mkdir(parents=True)
    row = _fake_row(fixture_repo)

    # interface contract: render(template_path, row) == instantiate(
    # load_template(path), fields_for_instance(row)) plus the reconstruction
    # marker for non-curated instances — provided here as a mock module (the real
    # one derives fields via dataset lookups that need real instance ids). This
    # stub renders without the marker; the marker is unit-tested separately.
    import fvk_bench
    stub = types.ModuleType("fvk_bench.agentic_prompts")
    stub.render = lambda path, r, **kw: (
        Path(path).read_text().split("---\n", 2)[-1].format(
            problem_statement=r["problem_statement"]))
    monkeypatch.setitem(sys.modules, "fvk_bench.agentic_prompts", stub)
    monkeypatch.setattr(fvk_bench, "agentic_prompts", stub, raising=False)

    monkeypatch.setattr(claude_code, "build_workspace",
                        lambda cfg, rd, r, kind, **kw: build_workspace(
                            cfg, rd, r, kind, repo_src=str(fixture_repo["path"]),
                            kit_src=fixture_kit["path"], build_venv=False,
                            workspaces_dir=tmp_path / "workspaces"))

    def fake_session(argv, prompt, cwd, timeout_s, stream_path, env=None):
        assert "--permission-mode" in argv and Path(cwd).is_dir()
        assert env is not None and env.get("HOME")  # sealed env is threaded in
        _mk_ws_outputs(Path(cwd), v1="diff --git a/f b/f\n--- a/f\n+++ b/f\n"
                                      "@@ -1,1 +1,1 @@\n-a\n+b\n", v2=None)
        stream_path.write_text(STREAM_FIXTURE.read_text())
        return {"returncode": 0, "timed_out": False, "stderr_tail": "",
                "duration_s": 1.0}

    monkeypatch.setattr(claude_code, "run_claude_session", fake_session)

    rec = claude_code.run_instance(cfg, run_dir, row, claude_bin="/fake/claude",
                                   session_env={"HOME": "/sealed"})
    assert rec["status"] == "ok"
    # The smoke fixture deliberately reads the row AND leaks an F2P name before
    # eval, so enforcement INVALIDATES the scored prediction: model_patch empty,
    # final_source 'contaminated'. The pre-review v1 is still preserved.
    assert rec["contaminated"] is True
    assert rec["final_source"] == "contaminated"
    assert rec["model_patch"] == ""
    assert rec["model_patch_v1"].startswith("diff --git a/f")  # v1 kept, not zeroed
    assert (run_dir / "prompts" / f"{IID}.prompt.txt").read_text() == (
        "Do the task: add() subtracts instead of adding two numbers.\n")
    assert (run_dir / "raw" / f"{IID}.jsonl").exists()
    audit = json.loads((run_dir / "audit" / f"{IID}.json").read_text())
    assert audit["counts"]["private_row_reads"] == 1
    assert audit["contaminated"] is True
    assert (run_dir / "artifacts" / IID / "manifest.json").exists()
    saved = json.loads((run_dir / "raw" / f"{IID}.json").read_text())
    assert saved["workspace_manifest_sha256"]


# ---------------------------------------------------------------------------
# 6. transition table + claimed-aggregate parsing
# ---------------------------------------------------------------------------

def test_parse_claimed_aggregates_takes_last_claim():
    text = ("v1 eval said:\nFAIL_TO_PASS 0/2\nPASS_TO_PASS 39/40\nresolved: false\n"
            "after the v2 fix:\nFAIL_TO_PASS 2/2\nPASS_TO_PASS 40/40\nresolved: true\n")
    c = parse_claimed_aggregates(text)
    assert c == {"FAIL_TO_PASS": "2/2", "PASS_TO_PASS": "40/40", "resolved": True}
    assert parse_claimed_aggregates("no claims here") is None


def test_write_run_report_gains_transition_section(tmp_path):
    """Full report wiring: a phased run with a -v1 harness pass gets the
    transition table + claimed cross-check; the summary/report still render."""
    from fvk_bench.report import write_run_report

    run_id = "agentic-report-test"
    rd = tmp_path / run_id
    (rd / "eval").mkdir(parents=True)
    (rd / "raw").mkdir()
    label = "claude-code-opus-4.6__fvk-replicate"
    ids = ["i-1", "i-2"]
    (rd / "meta.json").write_text(json.dumps({
        "run_id": run_id, "arm": "fvk-replicate", "model_label": label,
        "model": "claude-code-opus-4.6", "provider": "claude-code",
        "thinking": None, "prompt_version": "v1", "prompt_sha256": "ab" * 32,
        "prompt_path": "prompts/agentic/fvk-replicate.md",
        "dataset": "princeton-nlp/SWE-bench_Verified",
        "instance_ids": ids, "started_at": "2026-06-11T00:00:00Z"}))
    (rd / "eval" / f"{label}.{run_id}.json").write_text(json.dumps(
        {"resolved_ids": ["i-1"], "error_ids": [], "empty_patch_ids": []}))
    (rd / "eval" / f"{label}.{run_id}-v1.json").write_text(json.dumps(
        {"resolved_ids": [], "error_ids": []}))
    reports = rd / "artifacts" / "i-1" / "reports"
    reports.mkdir(parents=True)
    (reports / "v2_score.md").write_text(
        "# v2 Score\n\nFAIL_TO_PASS: 2 / 2\nPASS_TO_PASS: 40 / 40\nResolved: true\n")

    md = write_run_report(rd).read_text()
    assert "## Agentic phases: v1 → v2" in md
    assert "**v1 solved 0 / 2** → **v2 solved 1 / 2**" in md
    assert ("| i-1 | ❌ no | ✅ yes | X→R 📈 | F2P 2/2 · P2P 40/40 · "
            "resolved True | ✅ match |") in md
    assert "| i-2 | ❌ no | ❌ no | X→X | — | — |" in md
    # one-shot runs are untouched: no -v1 report file -> no section
    (rd / "eval" / f"{label}.{run_id}-v1.json").unlink()
    assert "Agentic phases" not in write_run_report(rd).read_text()


def test_render_transition_table():
    ids = ["i-a", "i-b", "i-c", "i-d"]
    md = render_transition_table(
        ids, v1_resolved={"i-a", "i-b"}, v2_resolved={"i-b", "i-c"},
        claimed_by_iid={
            "i-a": None,
            "i-b": {"FAIL_TO_PASS": "2/2", "PASS_TO_PASS": "9/9", "resolved": True},
            "i-c": {"FAIL_TO_PASS": "1/2", "PASS_TO_PASS": "9/9", "resolved": False},
            "i-d": None,
        })
    assert "| i-a | ✅ yes | ❌ no | R→X 📉 | — | — |" in md
    assert "R→R" in md and "| i-b |" in md and "✅ match" in md
    assert "X→R 📈" in md and "❌ MISMATCH" in md  # i-c claimed false, official yes
    assert "Transitions: R→R 1 · R→X 1 · X→R 1 · X→X 1" in md


# ---------------------------------------------------------------------------
# 7. opt-in end-to-end: real astropy workspace + GOLD patch (no LLM involved)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not os.environ.get("AGENTIC_IT"),
                    reason="set AGENTIC_IT=1 for the slow astropy workspace+gold "
                           "integration check (network: GitHub clone, pip wheels)")
def test_gold_patch_through_real_workspace(tmp_path):
    from fvk_bench.data import load_full_rows

    iid = "astropy__astropy-13236"
    cfg = _cc_cfg(tmp_path, "fvk-replicate", iid=iid)
    row = load_full_rows(cfg)[iid]
    run_dir = tmp_path / "runs" / "agentic-it"
    run_dir.mkdir(parents=True)
    ws = build_workspace(cfg, run_dir, row, "fvk-replicate", build_venv=True)

    patch = row["patch"] if row["patch"].endswith("\n") else row["patch"] + "\n"
    pf = ws / "patches" / "gold.patch"
    pf.write_text(patch)
    p = subprocess.run([sys.executable, str(ws / "scripts" / "private_eval.py"),
                        str(pf), "gold"], capture_output=True, text=True, timeout=2400)
    print(f"\nprivate_eval stdout:\n{p.stdout}stderr: {p.stderr!r}")
    assert p.returncode == 0, p.stderr
    lines = p.stdout.splitlines()
    assert len(lines) == 3
    assert lines[0] == "FAIL_TO_PASS 2/2"
    assert lines[2] == "resolved: true"


# ---------------------------------------------------------------------------
# 8. isolation hardening: sealed HOME, out-of-repo workspaces, baked row path,
#    enforcement-audit invalidation, patch-harvest git-diff fallback
# ---------------------------------------------------------------------------

def test_sealed_home_has_only_credentials_and_settings(tmp_path, monkeypatch):
    # Fake credential source so the test never touches the real ~/.claude.
    cred = tmp_path / "src_creds.json"
    cred.write_text('{"claudeAiOauth": {"accessToken": "fake"}}')
    sealed_root = tmp_path / "agent-home"
    monkeypatch.setenv("FVK_AGENT_HOME", str(sealed_root))

    home = ensure_sealed_home(credentials_src=cred)
    assert home == sealed_root
    claude = home / ".claude"
    # credentials present (a COPY, mode 600) + minimal settings
    assert (claude / ".credentials.json").read_text() == cred.read_text()
    assert oct((claude / ".credentials.json").stat().st_mode & 0o777) == "0o600"
    assert (claude / "settings.json").is_file()
    # NO CLAUDE.md, NO projects/ (memory), NO plugins/, NO mcp config anywhere
    for leak in ("CLAUDE.md", "projects", "memory", "plugins", "commands",
                 "agents", ".mcp.json", "mcp.json"):
        assert not (claude / leak).exists(), leak
    # only the two expected entries under .claude
    assert sorted(p.name for p in claude.iterdir()) == [".credentials.json",
                                                        "settings.json"]


def test_sealed_home_purges_preexisting_leaks(tmp_path, monkeypatch):
    cred = tmp_path / "c.json"
    cred.write_text("{}")
    sealed_root = tmp_path / "h"
    monkeypatch.setenv("FVK_AGENT_HOME", str(sealed_root))
    # pre-seed leak surfaces a prior/stray build might have left
    claude = sealed_root / ".claude"
    (claude / "plugins").mkdir(parents=True)
    (claude / "CLAUDE.md").parent.mkdir(parents=True, exist_ok=True)
    (claude / "CLAUDE.md").write_text("LEAK: this describes the experiment")
    (claude / "projects").mkdir()
    ensure_sealed_home(credentials_src=cred)
    assert not (claude / "plugins").exists()
    assert not (claude / "CLAUDE.md").exists()
    assert not (claude / "projects").exists()


def test_sealed_home_missing_credentials_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("FVK_AGENT_HOME", str(tmp_path / "h"))
    with pytest.raises(FileNotFoundError, match="credentials"):
        ensure_sealed_home(credentials_src=tmp_path / "nope.json")


def test_sealed_env_redirects_home_preserves_path(tmp_path):
    home = tmp_path / "sealed"
    env = sealed_env(home, base_env={"PATH": "/usr/bin:/bin", "FOO": "bar"})
    assert env["HOME"] == str(home)
    assert env["CLAUDE_CONFIG_DIR"] == str(home / ".claude")
    assert env["PATH"] == "/usr/bin:/bin"  # PATH preserved
    assert env["FOO"] == "bar"


def test_workspaces_root_default_is_outside_repo(monkeypatch):
    monkeypatch.delenv("FVK_WORKSPACES_DIR", raising=False)
    root = workspaces_root()
    # default must NOT be under the repo checkout (no ancestor CLAUDE.md leak)
    assert REPO_ROOT not in root.parents and root != REPO_ROOT
    assert root == Path.home() / ".cache" / "fvk-workspaces"
    # env override still wins
    monkeypatch.setenv("FVK_WORKSPACES_DIR", "/tmp/custom-ws")
    assert workspaces_root() == Path("/tmp/custom-ws")


def test_evaluator_reads_row_from_baked_absolute_path(phased_ws):
    """The staged evaluator must locate the row via the absolute path baked in
    at stage time, NOT via any in-workspace file."""
    script = (phased_ws / "scripts" / "private_eval.py").read_text()
    m = json.loads((phased_ws / "manifest.json").read_text())
    row_path = m["row_path"]
    # the absolute out-of-workspace path is baked in as the ROW_PATH constant
    assert f'ROW_PATH = r"{row_path}"' in script
    # the script never points ROW_PATH back into the workspace
    assert "swebench_row_full" not in script
    assert os.path.isabs(row_path) and phased_ws.name not in row_path.split("/")[:-3]


def test_baseline_gets_no_row_and_no_evaluator(tmp_path, fixture_repo, fixture_kit):
    cfg, run_dir, ws = _build(tmp_path, fixture_repo, fixture_kit, "baseline")
    assert not (run_dir / "private" / IID / "row.json").exists()  # no answer key
    assert not (ws / "scripts").exists()  # no evaluator
    assert not (ws / "private_eval").exists()


def test_audit_flags_python_network_reach():
    """Broadened network detection: python urllib/requests/socket reach, not
    just curl/wget/git/pip."""
    for cmd in ("python -c 'import urllib.request; urllib.request.urlopen(\"http://x\")'",
                "python3 -c \"import requests; requests.get('http://x')\"",
                "python -c 'import socket; socket.create_connection((\"x\",80))'"):
        ev = [{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}]
        audit = audit_transcript(ev, [F2P_ID])
        assert audit["counts"]["network_bash_commands"] == 1, cmd


def test_audit_invalidates_on_row_read_bash():
    """Enforcement: a transcript that cats the out-of-workspace row.json (by its
    absolute path) is contaminated."""
    row_path = "/home/u/.cache/fvk-workspaces/run/iid/../../runs/r/private/iid/row.json"
    ev = [{"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash",
         "input": {"command": f"cat {row_path}"}}]}}]
    audit = audit_transcript(ev, [F2P_ID], row_path=row_path)
    assert audit["contaminated"] is True
    assert audit["counts"]["private_row_reads"] == 1
    assert any("row read" in e for e in audit["contamination_evidence"])


def test_audit_invalidates_on_row_read_python_open():
    row_path = "/runs/r/private/iid/row.json"
    cmd = f"python -c \"import json; print(json.load(open('{row_path}')))\""
    ev = [{"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}]
    audit = audit_transcript(ev, [F2P_ID], row_path=row_path)
    assert audit["contaminated"] is True


def test_audit_invalidates_on_f2p_leak_before_eval():
    ev = [{"type": "assistant", "message": {"content": [
        {"type": "text", "text": f"I peeked: the hidden test is {F2P_ID}"}]}}]
    audit = audit_transcript(ev, [F2P_ID], row_path="/x/row.json")
    assert audit["contaminated"] is True
    assert any("f2p name before eval" in e for e in audit["contamination_evidence"])


def test_audit_clean_when_no_leak():
    ev = [{"type": "assistant", "message": {"content": [
        {"type": "text", "text": "Reading public code."},
        {"type": "tool_use", "name": "Bash",
         "input": {"command": "python scripts/private_eval.py patches/p.patch v1"}}]}}]
    audit = audit_transcript(ev, [F2P_ID], row_path="/x/row.json")
    assert audit["contaminated"] is False
    assert audit["contamination_evidence"] == []


def test_run_instance_invalidates_contaminated(tmp_path, monkeypatch,
                                               fixture_repo, fixture_kit):
    """End-to-end enforcement: a session that reads the row gets its prediction
    emptied, marked contaminated, and stamped in the record + audit file."""
    cfg = _cc_cfg(tmp_path, "fvk-replicate")
    run_dir = tmp_path / "runs" / "contam"
    for sub in ("raw", "prompts", "eval", "artifacts", "audit"):
        (run_dir / sub).mkdir(parents=True)
    row = _fake_row(fixture_repo)

    import fvk_bench
    stub = types.ModuleType("fvk_bench.agentic_prompts")
    stub.render = lambda path, r, **kw: (
        Path(path).read_text().split("---\n", 2)[-1].format(
            problem_statement=r["problem_statement"]))
    monkeypatch.setitem(sys.modules, "fvk_bench.agentic_prompts", stub)
    monkeypatch.setattr(fvk_bench, "agentic_prompts", stub, raising=False)
    monkeypatch.setattr(claude_code, "build_workspace",
                        lambda cfg, rd, r, kind, **kw: build_workspace(
                            cfg, rd, r, kind, repo_src=str(fixture_repo["path"]),
                            kit_src=fixture_kit["path"], build_venv=False,
                            workspaces_dir=tmp_path / "workspaces"))

    # The contaminating session: produces a patch BUT cats the out-of-workspace
    # row (its absolute path is in the freshly built manifest).
    def fake_session(argv, prompt, cwd, timeout_s, stream_path, env=None):
        # capture the baked row_path BEFORE _mk_ws_outputs overwrites manifest.json
        row_path = json.loads((Path(cwd) / "manifest.json").read_text())["row_path"]
        _mk_ws_outputs(Path(cwd), v1="diff --git a/f b/f\n--- a/f\n+++ b/f\n"
                                      "@@ -1,1 +1,1 @@\n-a\n+b\n", v2=None)
        stream_path.write_text(json.dumps({
            "type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash",
                 "input": {"command": f"cat {row_path}"}}]}}) + "\n"
            + json.dumps({"type": "result", "subtype": "success",
                          "num_turns": 1}) + "\n")
        return {"returncode": 0, "timed_out": False, "stderr_tail": "",
                "duration_s": 1.0}

    monkeypatch.setattr(claude_code, "run_claude_session", fake_session)
    rec = claude_code.run_instance(cfg, run_dir, row, claude_bin="/fake/claude",
                                   session_env={"HOME": "/x"})
    assert rec["contaminated"] is True
    assert rec["model_patch"] == ""               # prediction invalidated
    assert rec["final_source"] == "contaminated"
    assert "contaminated" in rec["error"]
    audit = json.loads((run_dir / "audit" / f"{IID}.json").read_text())
    assert audit["contaminated"] is True and audit["contamination_evidence"]


def test_harvest_falls_back_to_git_diff(tmp_path, fixture_repo, fixture_kit):
    """When no patch file is written, harvest recovers the agent's edits from
    repo/ via `git diff` (working tree) — first fallback after the file."""
    cfg, run_dir, ws = _build(tmp_path, fixture_repo, fixture_kit, "fvk-replicate")
    # the agent edited a tracked file but wrote NO patches/solution_v*.patch
    target = ws / "repo" / "tinypkg.py"
    target.write_text(target.read_text().replace("a - b", "a + b"))
    h = harvest_workspace(ws, "fvk-replicate", run_dir / "artifacts" / IID)
    assert h["final_source"] == "git-diff"
    assert "a + b" in h["final_patch"] and "diff --git" in h["final_patch"]


def test_harvest_git_diff_base_fallback(tmp_path, fixture_repo, fixture_kit):
    """If the working tree is clean but a change is committed past fvk-base, the
    diff-vs-base fallback still recovers it."""
    cfg, run_dir, ws = _build(tmp_path, fixture_repo, fixture_kit, "baseline")
    repo = ws / "repo"
    target = repo / "tinypkg.py"
    target.write_text(target.read_text().replace("a - b", "a + b"))
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                    "-c", "user.email=t@t", "commit", "-qm", "agent fix"],
                   check=True, capture_output=True)
    # working tree now clean vs HEAD -> `git diff` empty, but diff vs fvk-base sees it
    h = harvest_workspace(ws, "baseline", run_dir / "artifacts" / f"{IID}-b")
    assert h["final_source"] == "git-diff-base"
    assert "a + b" in h["final_patch"]


def test_report_lists_contaminated_prominently(tmp_path):
    """The per-run report must surface invalidated instances prominently."""
    from fvk_bench.report import write_run_report

    run_id = "contam-report"
    rd = tmp_path / run_id
    (rd / "eval").mkdir(parents=True)
    (rd / "raw").mkdir()
    label = "claude-code-opus-4.6__fvk-replicate"
    ids = ["i-1", "i-2"]
    (rd / "meta.json").write_text(json.dumps({
        "run_id": run_id, "arm": "fvk-replicate", "model_label": label,
        "model": "claude-code-opus-4.6", "provider": "claude-code",
        "thinking": None, "prompt_version": "v1", "prompt_sha256": "ab" * 32,
        "prompt_path": "prompts/agentic/fvk-replicate.md",
        "dataset": "princeton-nlp/SWE-bench_Verified",
        "instance_ids": ids, "started_at": "2026-06-11T00:00:00Z"}))
    (rd / "eval" / f"{label}.{run_id}.json").write_text(json.dumps(
        {"resolved_ids": [], "error_ids": [], "empty_patch_ids": ["i-1"]}))
    # i-1 was invalidated for reading the row
    (rd / "raw" / "i-1.json").write_text(json.dumps({
        "instance_id": "i-1", "model_patch": "", "contaminated": True,
        "contamination_evidence": ["row read: Bash: cat /runs/r/private/i-1/row.json"],
        "samples": []}))
    (rd / "raw" / "i-2.json").write_text(json.dumps({
        "instance_id": "i-2", "model_patch": "diff --git ...", "samples": []}))

    md = write_run_report(rd).read_text()
    assert "INVALIDATED for contamination" in md
    assert "`i-1`" in md and "row read" in md
    assert "i-1 ⚠️ CONTAMINATED" in md
    s = json.loads((rd / "summary.json").read_text())
    assert s["contaminated_ids"] == ["i-1"]
