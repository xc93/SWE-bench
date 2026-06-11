"""Headless Claude Code backend: one multi-turn agent session per instance.

Each session runs `claude -p` inside a freshly built workspace (fvk_bench.agentic)
with web tools denied; the protocol prompt comes from the arm's template
(fvk_bench.agentic_prompts — built by a parallel workstream against a fixed
interface: render(template_path, row), i.e. instantiate(load_template(path),
fields_for_instance(row)) plus the reconstruction provenance marker for
non-curated instances). The session's full stream-json transcript, the harvested
patches, and a leak/honesty audit are archived per instance.

CLI flags below were verified against `claude --help` of 2.1.169; `--max-turns`
is print-mode only and hidden from help (SDK flag) but accepted — verified in
the 2.1.169 binary's option table.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..agentic import (ARM_BASELINE, PHASED_KINDS, arm_kind_for_tag,
                       build_workspace, kit_commit_info, kit_dir, listify,
                       protocol_version)
from ..config import Config
from ..extract import normalize_patch
from .profile import ensure_sealed_home, sealed_env

# WebSearch/WebFetch: network reach is part of the leak surface.
# Skill: the CLI bundles review-flavored skills (code-review, simplify, verify, debug)
# that overlap with the treatment being measured; deny the Skill tool so no arm can
# invoke them. FVK is delivered to the replicate arm as workspace files, not a skill,
# so nothing of experimental value is lost.
DISALLOWED_TOOLS = "WebSearch,WebFetch,Skill"

# Session statuses recorded per instance (all terminal):
#   ok        — clean exit, result event present
#   turn_cap  — hit --max-turns (result subtype error_max_turns); harvest what exists
#   timeout   — exceeded session_timeout_s; killed, harvest what exists
#   cli_error — claude exited non-zero (after the one infra retry)
TERMINAL_STATUSES = ("ok", "turn_cap", "timeout", "cli_error")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------

def resolve_claude_bin() -> str:
    env = os.environ.get("CLAUDE_BIN")
    if env:
        return env
    on_path = shutil.which("claude")
    if on_path:
        return on_path
    raise FileNotFoundError(
        "claude binary not found — set CLAUDE_BIN or put `claude` on PATH "
        "(install Claude Code and log in once)")


def claude_version(claude_bin: str) -> str:
    out = subprocess.run([claude_bin, "--version"], capture_output=True, text=True,
                         timeout=60, check=True)
    return out.stdout.strip()


def build_claude_argv(claude_bin: str, cfg: Config) -> list[str]:
    """Exact invocation (prompt goes via stdin; cwd is the workspace).

    All flags verified against claude 2.1.169: -p/--print, --model,
    --output-format stream-json (print-only), --verbose (required for
    stream-json in print mode), --max-turns (print-only, hidden from --help),
    --disallowedTools (comma form), --permission-mode bypassPermissions
    (one of the documented choices).
    """
    return [
        claude_bin, "-p",
        "--model", cfg.model.cc_model,
        "--output-format", "stream-json",
        "--verbose",
        "--max-turns", str(cfg.model.max_turns),
        "--disallowedTools", DISALLOWED_TOOLS,
        "--permission-mode", "bypassPermissions",
    ]


def run_claude_session(argv: list[str], prompt: str, cwd: Path, timeout_s: int,
                       stream_path: Path, env: dict | None = None) -> dict:
    """One headless session. stdout (stream-json) is written to stream_path AS IT
    ARRIVES so a timed-out/killed session still leaves a harvestable transcript.

    `env` is the SEALED process environment (HOME redirected to the sealed agent
    home so no user CLAUDE.md / memory / plugins leak); None inherits os.environ.
    """
    t0 = time.monotonic()
    timed_out = False
    with stream_path.open("w") as out:
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=out,
                                stderr=subprocess.PIPE, text=True, cwd=cwd, env=env)
        try:
            _, stderr = proc.communicate(input=prompt, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            _, stderr = proc.communicate()
    return {
        "returncode": proc.returncode,
        "timed_out": timed_out,
        "stderr_tail": (stderr or "")[-4000:],
        "duration_s": round(time.monotonic() - t0, 1),
    }


def parse_stream(path: Path) -> list[dict]:
    """JSONL events from --output-format stream-json; non-JSON lines skipped."""
    events = []
    if not path.exists():
        return events
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(ev, dict):
            events.append(ev)
    return events


def result_event(events: list[dict]) -> dict | None:
    results = [e for e in events if e.get("type") == "result"]
    return results[-1] if results else None


def has_agent_turns(events: list[dict]) -> bool:
    return any(e.get("type") == "assistant" for e in events)


def session_status(events: list[dict], returncode: int, timed_out: bool) -> str:
    if timed_out:
        return "timeout"
    res = result_event(events)
    if res and "max_turns" in str(res.get("subtype", "")):
        return "turn_cap"
    if returncode != 0:
        return "cli_error"
    return "ok"


# ---------------------------------------------------------------------------
# Transcript audit (pure function over parsed events — unit-tested)
# ---------------------------------------------------------------------------

# Network reach is part of the leak surface. Beyond the classic shell fetchers,
# catch python-based reach: `python -c` with urllib/requests/socket, bare
# `import urllib`, `requests.get(`, urlopen, etc. — a bash agent can reopen the
# web through the interpreter even with WebSearch/WebFetch denied.
# `git clone` is flagged here too: the staged repo is the leak fence — a clone
# would resurrect upstream history (the future fix commit).
# NOTE pip/uv installs are NOT in this list: under protocol v2 the agent
# legitimately installs its own environment in Phase 0 (PyPI reach is
# sanctioned), so installer commands are counted separately below.
_NET_RE = re.compile(
    r"\b(curl|wget|git\s+fetch|git\s+pull|git\s+clone|"
    r"urllib|urlopen|requests\.(get|post|request)|import\s+requests|"
    r"import\s+socket|socket\.(socket|create_connection)|httpx|aiohttp|"
    r"nc\s|netcat|ssh\s|scp\s)\b")
# Sanctioned-under-v2 environment installs (pip / uv): recorded for review, not
# treated as suspicious network reach.
_INSTALL_RE = re.compile(
    r"\b(pip3?\s+install|python3?\s+-m\s+pip\s+install|uv\s+pip\s+install|"
    r"uv\s+venv)\b")
# Direct docker use from the agent's bash. The only sanctioned docker path is
# INSIDE scripts/private_eval.py (the docker-grading evaluator drives its own
# containers); a session has no legitimate reason to call docker itself, and a
# determined one could inspect the eval container/image. Counted for review.
_DOCKER_RE = re.compile(r"\bdocker\b")
_EVAL_OUT_RE = re.compile(r"FAIL_TO_PASS \d+/\d+")
_EVAL_INVOKE_RE = re.compile(r"private_eval\.py\s+\S+")
_EDITISH_RE = re.compile(r"(sed\s+-i|\btee\b|>>?\s*\S*private_eval\.py)")
_EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")


def _tool_uses(event: dict):
    for block in (event.get("message") or {}).get("content") or []:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            yield block.get("name") or "", block.get("input") or {}


def _texts(event: dict):
    for block in (event.get("message") or {}).get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            yield block.get("text") or ""


def _tool_result_texts(event: dict):
    for block in (event.get("message") or {}).get("content") or []:
        if isinstance(block, dict) and block.get("type") == "tool_result":
            content = block.get("content")
            if isinstance(content, str):
                yield content
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        yield c.get("text") or ""


def _f2p_needles(f2p_ids: list[str]) -> list[str]:
    """Strings whose appearance in assistant text means the agent knows a hidden
    test: the full pytest id and the bare test name (incl. parametrization)."""
    needles = []
    for tid in f2p_ids:
        needles.append(tid)
        if "::" in tid:
            tail = tid.rsplit("::", 1)[1]
            if tail and tail not in needles:
                needles.append(tail)
    # Longest first so the full id wins over its own tail when both match.
    return sorted(set(needles), key=len, reverse=True)


def _row_needles(row_path: str | None) -> list[str]:
    """Substrings whose appearance in a command/path means the agent reached the
    out-of-workspace answer key: its absolute path, its `row.json` basename, and
    the legacy in-workspace name (defence in depth across older artifacts)."""
    needles = ["swebench_row_full"]
    if row_path:
        needles.append(row_path)
        # basename ("row.json") catches `find ... -name row.json | xargs cat`.
        base = row_path.rsplit("/", 1)[-1]
        if base and base not in needles:
            needles.append(base)
    return needles


def _hits_row(text: str, row_needles: list[str]) -> bool:
    return any(n and n in text for n in row_needles)


def audit_transcript(events: list[dict], f2p_ids: list[str],
                     row_path: str | None = None) -> dict:
    """Honesty/leak audit over one session transcript.

    Flags: denied web-tool attempts, network-reaching Bash (incl. python urllib/
    requests/socket reach), reads of the hidden dataset row (the out-of-workspace
    row.json by absolute path or basename, via bash cat/grep or python open),
    edits of the private evaluator, and hidden FAIL_TO_PASS test names appearing
    in assistant text BEFORE the first in-session eval output (names never appear
    in eval output, so early mentions imply leakage).

    `contaminated` is True iff the transcript read the answer-key row OR a hidden
    FAIL_TO_PASS name leaked before the first eval output. The caller invalidates
    such instances (empty prediction).

    Two informational (non-contaminating) counters support the v2 protocol:
    `installer_bash_commands` (pip/uv — the sanctioned Phase-0 self-build) and
    `docker_bash_commands` (direct docker use outside private_eval.py — never
    needed by an honest session; reviewable evidence if aggregates look off).
    """
    denied, network, private_reads, script_edits = [], [], [], []
    installers, docker_cmds = [], []
    leaks_before, mentions = [], []
    eval_invocations = 0
    eval_seen = False
    needles = _f2p_needles(f2p_ids)
    row_needles = _row_needles(row_path)

    for ev in events:
        etype = ev.get("type")
        if etype == "assistant":
            for text in _texts(ev):
                for needle in needles:
                    if needle in text:
                        line = next((ln for ln in text.splitlines() if needle in ln),
                                    needle)
                        rec = {"name": needle, "line": line.strip()[:500]}
                        mentions.append(rec)
                        if not eval_seen:
                            leaks_before.append(rec)
                        break  # one hit per text block is enough
            for name, inp in _tool_uses(ev):
                if name in ("WebSearch", "WebFetch"):
                    denied.append({"tool": name, "input": inp})
                elif name == "Bash":
                    cmd = str(inp.get("command") or "")
                    if _NET_RE.search(cmd):
                        network.append(cmd[:500])
                    if _INSTALL_RE.search(cmd):
                        installers.append(cmd[:500])
                    if _DOCKER_RE.search(cmd) and "private_eval.py" not in cmd:
                        docker_cmds.append(cmd[:500])
                    if _hits_row(cmd, row_needles):
                        # A bash read of the row: cat/grep/head/python open(...).
                        private_reads.append(f"Bash: {cmd[:500]}")
                    if "private_eval.py" in cmd:
                        if _EVAL_INVOKE_RE.search(cmd) and not _EDITISH_RE.search(cmd):
                            eval_invocations += 1
                        elif _EDITISH_RE.search(cmd):
                            script_edits.append(f"Bash: {cmd[:500]}")
                elif name in ("Read", "NotebookRead"):
                    path = str(inp.get("file_path") or inp.get("notebook_path") or "")
                    if _hits_row(path, row_needles) or "/private_eval/" in path:
                        private_reads.append(f"{name}: {path}")
                elif name in _EDIT_TOOLS:
                    path = str(inp.get("file_path") or inp.get("notebook_path") or "")
                    if "private_eval.py" in path:
                        script_edits.append(f"{name}: {path}")
                    if _hits_row(path, row_needles):
                        private_reads.append(f"{name}: {path}")
        elif etype == "user":
            if not eval_seen:
                for text in _tool_result_texts(ev):
                    if _EVAL_OUT_RE.search(text):
                        eval_seen = True
                        break

    res = result_event(events) or {}
    contamination_evidence = ([f"row read: {r}" for r in private_reads]
                              + [f"f2p name before eval: {m['name']}"
                                 for m in leaks_before])
    contaminated = bool(contamination_evidence)
    return {
        "contaminated": contaminated,
        "contamination_evidence": contamination_evidence,
        "denied_tool_attempts": denied,
        "network_bash_commands": network,
        "installer_bash_commands": installers,
        "docker_bash_commands": docker_cmds,
        "private_row_reads": private_reads,
        "private_eval_script_edits": script_edits,
        "private_eval_invocations": eval_invocations,
        "f2p_leaks_before_eval": leaks_before,
        "f2p_mentions_total": len(mentions),
        "f2p_mentions": mentions,
        "num_turns": res.get("num_turns"),
        "duration_ms": res.get("duration_ms"),
        "usage": res.get("usage"),
        "total_cost_usd": res.get("total_cost_usd"),
        "counts": {
            "denied_tool_attempts": len(denied),
            "network_bash_commands": len(network),
            "installer_bash_commands": len(installers),
            "docker_bash_commands": len(docker_cmds),
            "private_row_reads": len(private_reads),
            "private_eval_script_edits": len(script_edits),
            "f2p_leaks_before_eval": len(leaks_before),
        },
    }


# ---------------------------------------------------------------------------
# Harvest
# ---------------------------------------------------------------------------

def _git_diff(repo: Path, *args: str) -> str | None:
    """`git -C repo diff <args>` text, or None if empty / git failed. Used as the
    patch-harvest fallback when the agent left no usable patch file."""
    if not (repo / ".git").is_dir():
        return None
    try:
        p = subprocess.run(["git", "-C", str(repo), "diff", *args],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    return p.stdout if (p.stdout and p.stdout.strip()) else None


def _harvest_diff_fallback(ws: Path) -> tuple[str | None, str | None]:
    """Recover a patch from repo/ when no patch file was written.

    Order (documented): the patch FILE is tried first by the caller; this is the
    next two fallbacks — the working-tree diff (`git diff`, agent edits to
    tracked files vs the clean base commit), then the diff against the synthetic
    base tag (`git diff fvk-base`, which also catches anything staged). Returns
    (patch_text, source) or (None, None).
    """
    repo = ws / "repo"
    wd = _git_diff(repo)  # working tree vs index — agent's unstaged edits
    if wd:
        return wd, "git-diff"
    base = _git_diff(repo, "fvk-base")  # vs the tagged base (staged + unstaged)
    if base:
        return base, "git-diff-base"
    return None, None


def harvest_workspace(ws: Path, arm_kind: str, art_dir: Path) -> dict:
    """Copy the session's outputs out of the workspace and pick the prediction.

    Final prediction = v2 else v1 else (git-diff fallback) else empty (flagged
    via final_source); baseline arms write a single patches/solution.patch.

    PATCH HARVEST FALLBACK: if the expected patch file is missing/empty, recover
    the agent's work from repo/ — first the working-tree diff (`git -C repo
    diff`), then the diff vs the tagged base (`git -C repo diff fvk-base`). So
    the resolution order is: patch file -> working diff -> diff-vs-base -> empty.
    """
    art_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("patches", "reports", "fvk", "review"):
        src = ws / sub
        if src.is_dir():
            shutil.copytree(src, art_dir / sub, dirs_exist_ok=True)
    for f in ("manifest.json", "private_eval/eval_log.jsonl"):
        src = ws / f
        if src.is_file():
            shutil.copy2(src, art_dir / src.name)

    def _read(name: str) -> str | None:
        p = ws / "patches" / name
        if p.is_file():
            text = p.read_text(errors="replace")
            return text if text.strip() else None
        return None

    if arm_kind == ARM_BASELINE:
        sol = _read("solution.patch")
        if sol:
            return {"patch_v1": None, "patch_v2": None, "final_patch": sol,
                    "final_source": "solution"}
        fb, fb_src = _harvest_diff_fallback(ws)
        return {"patch_v1": None, "patch_v2": None, "final_patch": fb or "",
                "final_source": fb_src or "empty"}
    v1, v2 = _read("solution_v1.patch"), _read("solution_v2.patch")
    if v2:
        final, source = v2, "v2"
    elif v1:
        final, source = v1, "v1"
    else:
        fb, fb_src = _harvest_diff_fallback(ws)
        final, source = (fb, fb_src) if fb else ("", "empty")
    return {"patch_v1": v1, "patch_v2": v2, "final_patch": final or "",
            "final_source": source}


# ---------------------------------------------------------------------------
# Per-instance run
# ---------------------------------------------------------------------------

def _compose_prompt(cfg: Config, row: dict) -> str:
    # Deferred import: fvk_bench.agentic_prompts is produced by a parallel
    # workstream (fixed interface). Tests may inject a mock module.
    from .. import agentic_prompts
    # render() == instantiate(load_template(path), fields_for_instance(row)) plus
    # the reconstruction provenance marker for non-curated instances.
    return agentic_prompts.render(cfg.system_prompt_path(), row)


def run_instance(cfg: Config, run_dir: Path, instance_row: dict,
                 claude_bin: str | None = None,
                 session_env: dict | None = None) -> dict:
    iid = instance_row["instance_id"]
    claude_bin = claude_bin or resolve_claude_bin()
    arm_kind = arm_kind_for_tag(cfg.arm_tag())
    t0 = time.monotonic()

    # Sealed HOME: no user CLAUDE.md / memory / plugins / MCP leak into the
    # session. Build once per process if the caller didn't supply it.
    if session_env is None:
        session_env = sealed_env(ensure_sealed_home())

    ws = build_workspace(cfg, run_dir, instance_row, arm_kind)
    mpath = ws / "manifest.json"
    manifest_sha = hashlib.sha256(mpath.read_bytes()).hexdigest() if mpath.exists() else None
    # The answer-key row lives OUTSIDE the workspace; the audit needs its path to
    # detect any read of it. (None for baseline — no row exists.)
    row_path = None
    if mpath.exists():
        try:
            row_path = json.loads(mpath.read_text()).get("row_path")
        except (OSError, json.JSONDecodeError):
            row_path = None

    prompt = _compose_prompt(cfg, instance_row)
    _atomic_write(run_dir / "prompts" / f"{iid}.prompt.txt", prompt)

    argv = build_claude_argv(claude_bin, cfg)
    stream_path = run_dir / "raw" / f"{iid}.jsonl"
    attempts = []
    for attempt in (1, 2):
        res = run_claude_session(argv, prompt, cwd=ws,
                                 timeout_s=cfg.model.session_timeout_s,
                                 stream_path=stream_path, env=session_env)
        events = parse_stream(stream_path)
        attempts.append({k: res[k] for k in ("returncode", "timed_out",
                                             "duration_s", "stderr_tail")})
        infra = (res["returncode"] != 0 and not res["timed_out"]
                 and not has_agent_turns(events))
        if infra and attempt == 1:
            # Infra failure before any agent turn (auth/spawn/flag errors):
            # retry once; keep the dead transcript for forensics.
            shutil.move(stream_path, stream_path.with_name(f"{iid}.attempt1.jsonl"))
            print(f"    {iid}: claude exited {res['returncode']} before any turn — "
                  f"retrying once ({res['stderr_tail'][-200:]!r})", flush=True)
            continue
        break
    status = session_status(events, res["returncode"], res["timed_out"])

    harvested = harvest_workspace(ws, arm_kind, run_dir / "artifacts" / iid)
    audit = audit_transcript(events, listify(instance_row.get("FAIL_TO_PASS")),
                             row_path=row_path)
    audit["session_status"] = status

    # ENFORCEMENT: a contaminated instance (read the answer-key row, or leaked a
    # hidden FAIL_TO_PASS name before the first eval output) is INVALIDATED — its
    # scored prediction is emptied so the official harness records it unsolved,
    # and the contamination is stamped on the record + audit for the report.
    contaminated = bool(audit.get("contaminated"))
    evidence = audit.get("contamination_evidence") or []
    if contaminated:
        print(f"    {iid}: CONTAMINATED — invalidating prediction "
              f"({'; '.join(evidence)[:300]})", flush=True)
    _atomic_write(run_dir / "audit" / f"{iid}.json", json.dumps(audit, indent=2))

    scored_patch = "" if contaminated else (
        normalize_patch(harvested["final_patch"]) if harvested["final_patch"] else "")

    res_ev = result_event(events) or {}
    usage = res_ev.get("usage") or {}
    rec = {
        "instance_id": iid,
        # Final prediction, mechanically normalized like every other arm. EMPTY
        # if the instance was invalidated for contamination.
        "model_patch": scored_patch,
        "model_patch_v1": (normalize_patch(harvested["patch_v1"])
                           if harvested.get("patch_v1") else ""),
        "final_source": "contaminated" if contaminated else harvested["final_source"],
        "contaminated": contaminated,
        "contamination_evidence": evidence,
        "arm_kind": arm_kind,
        "status": status,
        "error": (f"contaminated: {'; '.join(evidence)[:300]}" if contaminated
                  else (None if status == "ok"
                        else f"session {status}: rc={res['returncode']}")),
        "attempts": attempts,
        "workspace": str(ws),
        "workspace_manifest_sha256": manifest_sha,
        "samples": [{
            "sample": 0,
            "provider": "claude-code",
            "num_turns": res_ev.get("num_turns"),
            "duration_ms": res_ev.get("duration_ms"),
            "total_cost_usd": res_ev.get("total_cost_usd"),
            "usage": {**usage,
                      "prompt_tokens": usage.get("input_tokens"),
                      "completion_tokens": usage.get("output_tokens")} if usage else None,
        }],
        "wall_s": round(time.monotonic() - t0, 1),
        "finished_at": _now(),
    }
    _atomic_write(run_dir / "raw" / f"{iid}.json", json.dumps(rec, indent=2))
    return rec


# ---------------------------------------------------------------------------
# Run loop (the claude-code infer stage)
# ---------------------------------------------------------------------------

def run_agentic_inference(cfg: Config, run_dir: Path, resume: bool = True) -> Path:
    """All configured instances through headless sessions; writes raw/, prompts/,
    artifacts/, audit/, predictions.jsonl (+ predictions_v1.jsonl for phased
    arms), meta.json. Mirrors inference.run_inference's artifact contract."""
    from ..data import load_full_rows

    claude_bin = resolve_claude_bin()
    cc_version = claude_version(claude_bin)
    arm_kind = arm_kind_for_tag(cfg.arm_tag())
    phased = arm_kind in PHASED_KINDS

    # Build the sealed agent HOME once for the whole run (workers share it): no
    # user CLAUDE.md / memory / plugins / MCP leak into any session.
    sealed = ensure_sealed_home()
    session_env = sealed_env(sealed)

    for sub in ("raw", "prompts", "eval", "artifacts", "audit"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    if cfg.source_path:
        _atomic_write(run_dir / "config.snapshot.yaml", cfg.source_path.read_text())

    print(f"[{_now()}] loading dataset rows…", flush=True)
    rows = load_full_rows(cfg)

    meta = {
        "run_id": run_dir.name,
        "arm": cfg.arm_tag(),
        "arm_kind": arm_kind,
        "model_label": cfg.model_label(),
        "model": cfg.model.name,
        "provider": cfg.model.provider,
        "thinking": None,  # not a knob we control for Claude Code sessions
        "prompt_path": cfg.prompt.system_prompt,  # the arm's TEMPLATE file
        "prompt_version": cfg.prompt_version(),
        "prompt_sha256": cfg.system_prompt_sha(),  # template sha
        "cc_model": cfg.model.cc_model,
        "cc_version": cc_version,
        "max_turns": cfg.model.max_turns,
        "session_timeout_s": cfg.model.session_timeout_s,
        # v2 provenance: which protocol the template declares (drives the venv
        # prestage policy + the docker-vs-local grading default per workspace).
        "protocol_version": protocol_version(cfg),
        "disallowed_tools": DISALLOWED_TOOLS,
        "sealed_home": str(sealed),  # isolation provenance
        **({"kit_dir": str(kit_dir()), **kit_commit_info(kit_dir())}
           if arm_kind == "fvk-replicate" else {}),
        "dataset": cfg.dataset.name,
        "split": cfg.dataset.split,
        "instance_ids": cfg.dataset.instance_ids,
        "started_at": _now(),
    }
    _atomic_write(run_dir / "meta.json", json.dumps(meta, indent=2))

    def _one(iid: str) -> dict:
        raw_path = run_dir / "raw" / f"{iid}.json"
        if resume and raw_path.exists():
            rec = json.loads(raw_path.read_text())
            if rec.get("status") in TERMINAL_STATUSES:
                return {**rec, "resumed": True}
        return run_instance(cfg, run_dir, rows[iid], claude_bin=claude_bin,
                            session_env=session_env)

    ids = cfg.dataset.instance_ids
    print(f"[{_now()}] {meta['model_label']}: {len(ids)} agent sessions, "
          f"{cfg.inference.max_workers} workers, max_turns={cfg.model.max_turns}, "
          f"timeout={cfg.model.session_timeout_s}s", flush=True)
    records: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=cfg.inference.max_workers) as pool:
        futs = {pool.submit(_one, iid): iid for iid in ids}
        done = 0
        for fut in as_completed(futs):
            iid = futs[fut]
            rec = fut.result()
            records[iid] = rec
            done += 1
            print(f"[{done}/{len(ids)}] {iid}: status={rec.get('status')}"
                  f" final={rec.get('final_source')}"
                  f"{' (resumed)' if rec.get('resumed') else ''}"
                  f" patch={'yes' if rec.get('model_patch') else 'NO'}"
                  f" wall={rec.get('wall_s', '?')}s", flush=True)

    label = cfg.model_label()
    final_lines = [json.dumps({"instance_id": iid, "model_name_or_path": label,
                               "model_patch": records[iid].get("model_patch", "")})
                   for iid in ids]
    pred_path = run_dir / "predictions.jsonl"
    _atomic_write(pred_path, "\n".join(final_lines) + "\n")
    if phased:
        v1_lines = [json.dumps({"instance_id": iid, "model_name_or_path": label,
                                "model_patch": records[iid].get("model_patch_v1", "")})
                    for iid in ids]
        _atomic_write(run_dir / "predictions_v1.jsonl", "\n".join(v1_lines) + "\n")

    meta["finished_at"] = _now()
    meta["n_with_patch"] = sum(1 for r in records.values() if r.get("model_patch"))
    meta["n_errors"] = sum(1 for r in records.values() if r.get("error"))
    contaminated_ids = sorted(iid for iid in ids
                              if records[iid].get("contaminated"))
    meta["contaminated_ids"] = contaminated_ids
    meta["session_statuses"] = {iid: records[iid].get("status") for iid in ids}
    meta["workspace_manifest_shas"] = {
        iid: records[iid].get("workspace_manifest_sha256") for iid in ids}
    _atomic_write(run_dir / "meta.json", json.dumps(meta, indent=2))
    print(f"[{_now()}] sessions done: {meta['n_with_patch']}/{len(ids)} with patches, "
          f"{meta['n_errors']} session errors"
          f"{f', {len(contaminated_ids)} CONTAMINATED {contaminated_ids}' if contaminated_ids else ''}"
          f" -> {pred_path}", flush=True)
    return pred_path
