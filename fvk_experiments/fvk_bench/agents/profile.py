"""A sealed HOME for headless Claude Code sessions.

WHY THIS EXISTS — a probe proved that a bare `claude -p` launched from this repo
leaks two kinds of context into the experiment, both confounds:

  1. CONTEXT FILES. `claude -p` auto-discovers ancestor CLAUDE.md files (this
     repo's CLAUDE.md literally describes the FVK experiment) and loads the
     user-global auto-memory under ~/.claude/projects/.../memory — so a session
     would "know" it is being graded on SWE-bench astropy instances.
  2. INSTALLED TOOLS. The session inherits the user's installed plugins / MCP
     servers — playwright (a real browser!), vercel, telegram, superpowers —
     which silently reopens web access and adds non-benchmark capabilities.

The fix is to run the session under a HOME that contains ONLY what auth needs
and nothing else. Claude Code reads its user config (CLAUDE.md, memory,
plugins, settings, MCP) from $HOME/.claude (and $CLAUDE_CONFIG_DIR if set); a
HOME whose .claude holds just the OAuth credential file therefore has no
user CLAUDE.md, no projects/ memory, and no plugins/ to discover. We do NOT use
`claude --bare` (which would also disable auto-memory/plugins/CLAUDE.md) because
--bare forces ANTHROPIC_API_KEY-only auth and would break our OAuth login.

The sealed home is reusable across sessions (built once, content-checked on
reuse) and lives OUTSIDE the repo so it is never itself a discoverable ancestor.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path

# Real per-user Claude config (source of the OAuth credential file we copy).
REAL_CLAUDE_DIR = Path.home() / ".claude"
REAL_CREDENTIALS = REAL_CLAUDE_DIR / ".credentials.json"

# Minimal settings for the sealed session. Empty is sufficient — a bare home
# already excludes user memory/plugins/CLAUDE.md — but we set the documented
# attribution off and pin an empty project-memory surface to be explicit. Keys
# Claude Code does not recognize are ignored, so this stays harmless.
SEALED_SETTINGS: dict = {
    "includeCoAuthoredBy": False,
}


def sealed_home_root() -> Path:
    """Where the reusable sealed home lives (override with FVK_AGENT_HOME)."""
    env = os.environ.get("FVK_AGENT_HOME")
    return Path(env) if env else Path.home() / ".cache" / "fvk-agent-home"


def _chmod_600(p: Path) -> None:
    p.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600


def ensure_sealed_home(*, credentials_src: Path | None = None) -> Path:
    """Build (or refresh) a sealed HOME and return its path.

    Layout (and NOTHING else under .claude):
        <home>/.claude/.credentials.json   COPY of the real OAuth file, mode 600
        <home>/.claude/settings.json       minimal settings (SEALED_SETTINGS)

    No CLAUDE.md, no projects/ (memory), no plugins/, no MCP config. `claude`
    is launched with HOME=<home> so this is the only user config it can see.

    `credentials_src` overrides the source credential file (tests). Raises if no
    credential file exists — the sealed session would otherwise fail to auth and
    every instance would be a silent infra error.
    """
    src = credentials_src or REAL_CREDENTIALS
    if not src.is_file():
        raise FileNotFoundError(
            f"no Claude OAuth credentials at {src} — log in once with `claude` "
            "(the sealed agent home copies this file for auth)")

    home = sealed_home_root()
    claude = home / ".claude"
    claude.mkdir(parents=True, exist_ok=True)

    # Refresh the credential copy every time: the real token may have been
    # rotated since the sealed home was first built, and a stale copy would
    # make the sealed session fail to authenticate.
    dst = claude / ".credentials.json"
    shutil.copyfile(src, dst)
    _chmod_600(dst)

    (claude / "settings.json").write_text(json.dumps(SEALED_SETTINGS, indent=2) + "\n")

    # Defensive: a sealed home must never accumulate leak surfaces. Drop any
    # user-config OR prior-session state under .claude (we own this dir). The
    # session files (projects/, sessions/, .claude.json, mcp caches) are written
    # by Claude Code itself during a run; we start every run from a clean slate
    # so nothing — not even an MCP-discovery cache — persists between runs.
    for leak in ("CLAUDE.md", "projects", "memory", "plugins", "commands",
                 "agents", "mcp.json", ".mcp.json", ".claude.json", "sessions",
                 "backups", "mcp-needs-auth-cache.json", ".last-cleanup", "todos",
                 "statsig", "shell-snapshots"):
        p = claude / leak
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        elif p.exists():
            p.unlink()
    # Claude Code also writes $HOME/.claude.json (outside .claude/): clear it too.
    top_state = home / ".claude.json"
    if top_state.exists():
        top_state.unlink()
    return home


# CAVEAT (account-tied remote MCP). A sealed HOME suppresses the user's LOCAL
# config (CLAUDE.md, memory, plugins, local MCP). It cannot suppress remote MCP
# servers tied to the OAuth ACCOUNT (e.g. "claude.ai Gmail"/"Google Calendar"):
# Claude Code learns of those from the credential, not local config. The
# isolation probe confirmed they are NOT advertised as usable tools in a headless
# print-mode session (they sit unauthenticated in mcp-needs-auth-cache.json and
# never surface), so they are inert; --disallowedTools WebSearch,WebFetch remains
# the belt-and-suspenders block on the web reach that matters.


def sealed_env(home: Path, base_env: dict | None = None) -> dict:
    """Process env for a sealed session: HOME (and CLAUDE_CONFIG_DIR) redirected
    to the sealed home, PATH and everything else preserved.

    CLAUDE_CONFIG_DIR is set defensively — if claude 2.1.169 honors it the user
    config is doubly sealed; if it ignores the var, HOME already does the job.
    """
    env = dict(base_env if base_env is not None else os.environ)
    env["HOME"] = str(home)
    env["CLAUDE_CONFIG_DIR"] = str(home / ".claude")
    return env
