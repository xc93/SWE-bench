#!/usr/bin/env python
"""Build prompts/fvk/v3.md: the ENTIRE formal-verification-kit repo, verbatim,
concatenated behind a thin one-shot adaptation wrapper. No distillation.

Reads blobs from the vendored submodule at a pinned commit via `git show`, so the
output is reproducible byte-for-byte from the recorded ref.

Usage (from anywhere):
    .venv/bin/python fvk_experiments/scripts/build_v3_verbatim.py [--ref <sha>]
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

EXP_ROOT = Path(__file__).resolve().parent.parent
SUBMODULE = EXP_ROOT / "vendor" / "formal-verification-kit"
DEFAULT_REF = "d0d07bad2d500467f7e1e9ccc4a3aa2af638a38d"
OUT = EXP_ROOT / "prompts" / "fvk" / "v3.md"

SEP = "========== FILE: {path} =========="

# Reading order: orientation docs first, then theory, then the commands the
# directive cites, then examples and everything else.
GROUP_ORDER = ("README.md", "AGENTS.md", "LICENSE", "knowledge/", "commands/",
               "examples/", "docs/")

WRAPPER = """# FVK Methodology Directive (v3 — full kit, verbatim)

You are repairing a GitHub issue. You receive the issue text plus the full text of the relevant source files, and you must produce a unified-diff patch that fixes the issue.

Below is the COMPLETE content of the Formal Verification Kit (FVK) repository (github.com/grosu/formal-verification-kit @ {ref_short}) — every file verbatim, each introduced by a `{sep_example}` header. Apply its methodology before patching.

Adaptation to this one-shot setting (this section overrides any kit instruction it conflicts with):

- You have **no** K toolchain (`kompile`/`krun`/`kprove`), no slash commands, no filesystem, and no multi-iteration loop. Wherever the kit says to run `/formalize` or `/verify`, or to emit artifact files (FINDINGS.md, SPEC.md, PROOF.md, `.k` files), do the equivalent work **inline, in your reasoning and visible answer**.
- Required order, without exception: **(1) FORMALIZE** the program fragment the issue implicates, per `commands/formalize.md` — state the *intended* contracts as K-style reachability claims, one generalized circularity claim per loop or recursive function (with soundness side conditions), and enumerate boundary conditions; **(2) VERIFY** your candidate fix against those specs, per `commands/verify.md` — hand-executed symbolic execution, case-split every guard, discharge every circularity with guardedness and every verification condition, and check a termination measure; if verification fails on any path or obligation, treat it as a finding, revise the fix, and re-verify; **(3) PATCH** — only after verification succeeds, emit the final unified-diff patch implementing exactly the fix you verified, nothing more.
- Keep the formalization proportionate: specify the code the issue touches and its immediate dependencies, not the whole codebase.
- Skip entirely: the kit's report/test-redundancy outputs, repo onboarding, and installation instructions.
- **Output format**: the task instructions in the user message govern the final answer's formatting — the patch format, any wrappers, and all output constraints. They take precedence over anything in this directive or in the kit files below.

"""


def git_show(ref: str, path: str) -> str:
    out = subprocess.run(["git", "-C", str(SUBMODULE), "show", f"{ref}:{path}"],
                         capture_output=True, check=True)
    return out.stdout.decode("utf-8")  # strict: all kit files must be utf-8 text


def list_files(ref: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(SUBMODULE), "ls-tree", "-r", "--name-only", ref],
                         capture_output=True, check=True, text=True)
    return [line for line in out.stdout.splitlines() if line]


def ordered(files: list[str]) -> list[str]:
    result, seen = [], set()
    for group in GROUP_ORDER:
        members = sorted(f for f in files if (f == group or f.startswith(group)) and f not in seen)
        result.extend(members)
        seen.update(members)
    leftovers = sorted(f for f in files if f not in seen)
    result.extend(leftovers)
    assert len(result) == len(files), "grouping lost or duplicated files"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", default=DEFAULT_REF)
    args = ap.parse_args()

    files = ordered(list_files(args.ref))
    parts, total_bytes = [], 0
    for path in files:
        content = git_show(args.ref, path)
        assert SEP.format(path="") .strip("=: ") not in content or True
        assert "========== FILE:" not in content, f"separator collision in {path}"
        total_bytes += len(content.encode())
        parts.append(SEP.format(path=path) + "\n\n" + content.rstrip("\n") + "\n")

    body = WRAPPER.format(ref_short=args.ref[:7],
                          sep_example=SEP.format(path="<path>")) + "\n".join(parts)
    frontmatter = f"""---
version: 3
date: {dt.date.today().isoformat()}
source: https://github.com/grosu/formal-verification-kit
source_commit: {args.ref}
method: >
  Verbatim concatenation of the ENTIRE kit repo ({len(files)} files, {total_bytes}
  bytes) at the pinned commit — no distillation — behind a thin one-shot adaptation
  wrapper (no toolchain/slash commands/artifact files; formalize -> verify -> patch
  order; task output format takes precedence). Generated reproducibly by
  scripts/build_v3_verbatim.py.
---
"""
    OUT.write_text(frontmatter + body)
    est_tokens = int(len(body) / 3.8)
    print(f"wrote {OUT}: {len(files)} files, body {len(body):,} chars (~{est_tokens:,} tokens est)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
