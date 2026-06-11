import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench import codex
from fvk_bench.codex import (last_usage, parse_events, resolve_codex_bin,
                             run_codex_exec)
from fvk_bench.inference import compose_codex_prompt

FIXTURE = Path(__file__).parent / "fixtures" / "codex_smoke_events.jsonl"


def _fake_bin(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n")
    path.chmod(0o755)
    return path


def _no_env_no_path(monkeypatch, tmp_path):
    monkeypatch.delenv("CODEX_BIN", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))  # nothing on PATH
    monkeypatch.setenv("HOME", str(tmp_path))            # no extensions yet


# ---- bin resolution ---------------------------------------------------------

def test_resolve_prefers_codex_bin_env(monkeypatch):
    monkeypatch.setenv("CODEX_BIN", "/opt/somewhere/codex")
    assert resolve_codex_bin() == "/opt/somewhere/codex"


def test_resolve_falls_back_to_path(monkeypatch, tmp_path):
    _no_env_no_path(monkeypatch, tmp_path)
    b = _fake_bin(tmp_path / "bin" / "codex")
    monkeypatch.setenv("PATH", str(tmp_path / "bin"))
    assert resolve_codex_bin() == str(b)


def test_resolve_picks_newest_extension_install(monkeypatch, tmp_path):
    _no_env_no_path(monkeypatch, tmp_path)
    ext = tmp_path / ".vscode" / "extensions"
    old = _fake_bin(ext / "openai.chatgpt-26.500.1-linux-x64/bin/linux-x86_64/codex")
    new = _fake_bin(ext / "openai.chatgpt-26.602.71036-linux-x64/bin/linux-x86_64/codex")
    os.utime(old, (1000, 1000))
    os.utime(new, (2000, 2000))
    assert resolve_codex_bin() == str(new)


def test_resolve_missing_raises_with_login_hint(monkeypatch, tmp_path):
    _no_env_no_path(monkeypatch, tmp_path)
    with pytest.raises(FileNotFoundError, match="codex login"):
        resolve_codex_bin()


# ---- event/usage parsing (real smoke-run fixture) ---------------------------

def test_fixture_events_parse():
    events = parse_events(FIXTURE.read_text())
    assert [e["type"] for e in events] == [
        "thread.started", "turn.started", "item.completed", "turn.completed"]
    assert codex._final_from_events(events) == "CODEX_SMOKE_OK"


def test_fixture_usage_from_last_turn_completed():
    events = parse_events(FIXTURE.read_text())
    assert last_usage(events) == {"input_tokens": 22551, "cached_input_tokens": 20352,
                                  "output_tokens": 9, "reasoning_output_tokens": 0}


def test_parse_events_skips_non_json_noise():
    noisy = "warning: something\n" + FIXTURE.read_text() + "\nnot json either\n"
    assert len(parse_events(noisy)) == 4
    assert last_usage([]) is None


# ---- run_codex_exec (mocked subprocess; no real calls) ----------------------

def test_run_codex_exec_mocked(monkeypatch, tmp_path):
    fixture = FIXTURE.read_text()
    seen = {}

    def fake_run(argv, **kw):
        seen["argv"], seen["kw"] = argv, kw
        Path(argv[argv.index("-o") + 1]).write_text("CODEX_SMOKE_OK")
        return subprocess.CompletedProcess(argv, 0, stdout=fixture, stderr="")

    monkeypatch.setattr(codex.subprocess, "run", fake_run)
    scratch = tmp_path / "scratch" / "astropy__astropy-12907"
    res = run_codex_exec("/fake/codex", "the big prompt", "gpt-5.5", "xhigh",
                         timeout_s=60, scratch_dir=scratch)

    assert res["final_message"] == "CODEX_SMOKE_OK"
    assert res["usage"]["input_tokens"] == 22551
    assert res["returncode"] == 0
    assert [e["type"] for e in res["events"]][-1] == "turn.completed"
    argv = res["argv"]
    assert argv[:2] == ["/fake/codex", "exec"]
    assert {"--ignore-user-config", "--ephemeral", "--json"} <= set(argv)
    assert argv[argv.index("-m") + 1] == "gpt-5.5"
    assert argv[argv.index("-c") + 1] == 'model_reasoning_effort="xhigh"'
    assert argv[-1] == "-" and "the big prompt" not in argv  # prompt via stdin only
    assert seen["kw"]["input"] == "the big prompt"
    assert seen["kw"]["timeout"] == 60
    assert Path(seen["kw"]["cwd"]) == scratch
    assert not scratch.exists()  # scratch removed on success


def test_run_codex_exec_raises_on_nonzero_exit(monkeypatch, tmp_path):
    def fake_run(argv, **kw):
        return subprocess.CompletedProcess(argv, 2, stdout="", stderr="auth expired")

    monkeypatch.setattr(codex.subprocess, "run", fake_run)
    scratch = tmp_path / "scratch"
    with pytest.raises(RuntimeError, match="auth expired"):
        run_codex_exec("/fake/codex", "p", "gpt-5.5", None,
                       timeout_s=60, scratch_dir=scratch)
    assert scratch.exists()  # kept for debugging on failure


def test_run_codex_exec_no_effort_omits_config_flag(monkeypatch, tmp_path):
    def fake_run(argv, **kw):
        Path(argv[argv.index("-o") + 1]).write_text("ok")
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(codex.subprocess, "run", fake_run)
    res = run_codex_exec("/fake/codex", "p", "gpt-5.5", None,
                         timeout_s=60, scratch_dir=tmp_path / "s")
    assert "-c" not in res["argv"]
    assert res["usage"] is None  # no turn.completed in stdout


# ---- single-prompt composition ----------------------------------------------

def test_compose_codex_prompt():
    assert compose_codex_prompt("ORACLE", None) == "ORACLE"
    assert compose_codex_prompt("ORACLE", "SYS\nTEXT") == (
        "<experiment_instructions>\nSYS\nTEXT\n</experiment_instructions>\n\nORACLE")
