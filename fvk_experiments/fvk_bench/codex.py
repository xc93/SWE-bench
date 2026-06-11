"""OpenAI Codex CLI backend: one-shot `codex exec` under a ChatGPT subscription.

No API key — auth comes from a one-time `codex login`. The CLI wraps the model in
Codex's own agent harness (its hidden system prompt alone is ~22.5k input tokens),
a black box; acceptable for pair comparisons because every arm shares it.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

_EXEC_FLAGS = ("--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
               "-s", "read-only", "--color", "never", "--json")
_EXT_GLOB = ".vscode/extensions/openai.chatgpt-*/bin/linux-x86_64/codex"


def resolve_codex_bin() -> str:
    """$CODEX_BIN > `codex` on PATH > newest VS Code ChatGPT-extension install.

    Dynamic on purpose: the extension path is version-numbered and rots.
    """
    env = os.environ.get("CODEX_BIN")
    if env:
        return env
    on_path = shutil.which("codex")
    if on_path:
        return on_path
    candidates = list(Path.home().glob(_EXT_GLOB))
    if candidates:
        return str(max(candidates, key=lambda p: p.stat().st_mtime))
    raise FileNotFoundError(
        "codex binary not found — set CODEX_BIN, put `codex` on PATH, or install the "
        "ChatGPT VS Code extension; then authenticate once with `codex login` "
        "(ChatGPT subscription, no API key needed)")


def codex_version(codex_bin: str) -> str:
    out = subprocess.run([codex_bin, "--version"], capture_output=True, text=True,
                         timeout=60, check=True)
    return out.stdout.strip()


def parse_events(stdout: str) -> list[dict]:
    """JSONL events from `codex exec --json`; non-JSON lines are skipped."""
    events = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def last_usage(events: list[dict]) -> dict | None:
    """Usage dict from the last turn.completed event, or None."""
    usages = [e["usage"] for e in events
              if e.get("type") == "turn.completed" and e.get("usage")]
    return usages[-1] if usages else None


def _final_from_events(events: list[dict]) -> str:
    """Last agent_message text — fallback when the `-o` file is missing/empty."""
    texts = []
    for e in events:
        item = e.get("item") or {}
        if e.get("type") == "item.completed" and item.get("type") == "agent_message":
            texts.append(item.get("text") or "")
    return texts[-1] if texts else ""


def run_codex_exec(codex_bin: str, prompt: str, model: str,
                   reasoning_effort: str | None, timeout_s: int,
                   scratch_dir: Path) -> dict:
    """One `codex exec` call. Prompt goes via stdin (`-` arg; ARG_MAX-safe), cwd is
    an empty scratch dir (removed on success). Nonzero exit or timeout raises —
    the caller's retry loop owns recovery.
    """
    scratch_dir = Path(scratch_dir)
    scratch_dir.mkdir(parents=True, exist_ok=True)
    last_msg = scratch_dir / "last_message.txt"
    argv = [codex_bin, "exec", *_EXEC_FLAGS, "-m", model]
    if reasoning_effort:
        argv += ["-c", f'model_reasoning_effort="{reasoning_effort}"']
    argv += ["-o", str(last_msg), "-"]
    t0 = time.monotonic()
    proc = subprocess.run(argv, input=prompt, capture_output=True, text=True,
                          timeout=timeout_s, cwd=scratch_dir)
    duration_s = round(time.monotonic() - t0, 1)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-2000:]
        raise RuntimeError(f"codex exec exited {proc.returncode}: {tail}")
    events = parse_events(proc.stdout or "")
    final = last_msg.read_text() if last_msg.exists() else ""
    if not final.strip():
        final = _final_from_events(events)
    shutil.rmtree(scratch_dir, ignore_errors=True)
    return {
        "final_message": final,
        "events": events,
        "usage": last_usage(events),
        "argv": argv,
        "returncode": proc.returncode,
        "duration_s": duration_s,
    }
