"""Extract a unified-diff patch from a model response. Pure functions, unit-tested."""

from __future__ import annotations

import re

_FENCE_DIFF = re.compile(r"```(?:diff|patch)[ \t]*\n(.*?)```", re.DOTALL)
_PATCH_TAG = re.compile(r"<patch>[ \t]*\n?(.*?)</patch>", re.DOTALL)
_ANY_FENCE = re.compile(r"```[A-Za-z0-9_-]*[ \t]*\n(.*?)```", re.DOTALL)

_DIFF_LINE = re.compile(r"^(diff --git |--- |\+\+\+ |@@ )", re.MULTILINE)
# Lines that may legitimately appear in a unified diff stream.
_DIFF_BODY = re.compile(
    r"^(diff |index |--- |\+\+\+ |@@ |[+\- ]|\\ No newline|new file|deleted file"
    r"|old mode|new mode|similarity|rename |copy |Binary|$)"
)


def _looks_like_diff(s: str) -> bool:
    return bool(_DIFF_LINE.search(s))


def _trim_trailing_prose(s: str) -> str:
    """Drop trailing lines that cannot be part of a diff (explanatory prose)."""
    lines = s.split("\n")
    end = len(lines)
    while end > 0 and not _DIFF_BODY.match(lines[end - 1]):
        end -= 1
    return "\n".join(lines[:end])


def _normalize(s: str) -> str | None:
    s = s.strip("\n")
    if not s:
        return None
    return s + "\n"


def _dedup_concat(blocks: list[str]) -> str:
    seen, out = set(), []
    for b in blocks:
        key = b.strip()
        if key and key not in seen:
            seen.add(key)
            out.append(b.strip("\n"))
    return "\n".join(out)


_HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$")
_FILE_HDR = re.compile(
    r"^(diff --git |index |--- |\+\+\+ |new file|deleted file|old mode|new mode"
    r"|similarity|rename |copy |Binary)"
)


def normalize_patch(patch: str) -> str:
    """Mechanically repair LLM diff bookkeeping without touching content:

    - recompute hunk-header line counts (`@@ -A,B +C,D @@`) from the actual
      hunk body — models routinely get B/D wrong, which is fatal to
      git apply / GNU patch;
    - restore the leading space on blank context lines emitted as fully
      empty lines inside a hunk.
    """
    lines = patch.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = _HUNK.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        body: list[str] = []
        j = i + 1
        while j < len(lines):
            ln = lines[j]
            if _HUNK.match(ln) or _FILE_HDR.match(ln):
                break
            if ln == "" or ln[0] in " +-\\":
                body.append(ln)
                j += 1
                continue
            break  # prose after the hunk — leave for the caller's trimming
        while body and body[-1] == "":
            body.pop()  # separator blanks between sections, not context
        body = [(" " if b == "" else b) for b in body]
        src = sum(1 for b in body if b[0] in " -")
        dst = sum(1 for b in body if b[0] in " +")
        out.append(f"@@ -{m.group(1)},{src} +{m.group(2)},{dst} @@{m.group(3)}")
        out.extend(body)
        i = j
    res = "\n".join(out)
    if patch.endswith("\n") and not res.endswith("\n"):
        res += "\n"
    return res


def extract_diff(text: str | None) -> str | None:
    """Return the patch contained in `text`, or None if no diff is found.

    Strategy families, first non-empty wins (within a family, blocks are
    de-duplicated and concatenated so multi-file patches survive):
      1. ```diff / ```patch fenced blocks
      2. <patch>...</patch> tags
      3. any fenced block that looks like a diff
      4. raw text from the first diff-looking line, trailing prose trimmed

    The result is passed through `normalize_patch` (mechanical hunk-count
    repair, identical for every caller/arm).
    """
    if not text:
        return None
    raw = None
    for pattern in (_FENCE_DIFF, _PATCH_TAG):
        blocks = [b for b in pattern.findall(text) if _looks_like_diff(b)]
        if blocks:
            raw = _dedup_concat(blocks)
            break
    if raw is None:
        blocks = [b for b in _ANY_FENCE.findall(text) if _looks_like_diff(b)]
        if blocks:
            raw = _dedup_concat(blocks)
    if raw is None:
        m = re.search(r"^(?:diff --git .+|--- \S.*)$", text, re.MULTILINE)
        if m:
            raw = _trim_trailing_prose(text[m.start():])
    if raw is None:
        return None
    return _normalize(normalize_patch(raw))
