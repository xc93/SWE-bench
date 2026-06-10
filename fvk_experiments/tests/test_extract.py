import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.extract import extract_diff, normalize_patch

# Hunk counts here are correct (src=4, dst=5), so normalization is the identity
# and exact-equality assertions hold.
DIFF = """--- a/sympy/core/compatibility.py
+++ b/sympy/core/compatibility.py
@@ -209,4 +209,5 @@ class NotIterable:
     calling list() on the instance, for example, would result in
     an infinite loop.
     \"\"\"
+    __slots__ = ()
     pass
"""


def test_fenced_diff_block():
    text = f"Here is the fix:\n```diff\n{DIFF}```\nThis resolves the issue."
    assert extract_diff(text) == DIFF


def test_patch_tags():
    text = f"<patch>\n{DIFF}</patch>"
    assert extract_diff(text) == DIFF


def test_fenced_wins_over_prose_mention():
    text = f"The line `--- a/foo.py` changes.\n```diff\n{DIFF}```"
    assert extract_diff(text) == DIFF


def test_raw_diff_with_trailing_prose():
    text = f"Some analysis first.\n\n{DIFF}\nThis patch adds __slots__ to fix the issue."
    out = extract_diff(text)
    assert out is not None
    assert out.startswith("--- a/sympy")
    assert "This patch adds" not in out


def test_duplicate_blocks_deduped():
    text = f"```diff\n{DIFF}```\nAgain:\n```diff\n{DIFF}```"
    assert extract_diff(text) == DIFF


def test_two_file_patches_concatenated():
    d2 = "--- a/b.py\n+++ b/b.py\n@@ -1 +1 @@\n-x\n+y\n"
    text = f"```diff\n{DIFF}```\nand\n```diff\n{d2}```"
    out = extract_diff(text)
    assert "compatibility.py" in out and "b.py" in out


def test_generic_fence_with_diff_content():
    text = f"```\n{DIFF}```"
    assert extract_diff(text) == DIFF


def test_no_diff_returns_none():
    assert extract_diff("I could not produce a patch, sorry.") is None
    assert extract_diff("") is None
    assert extract_diff(None) is None


def test_non_diff_fence_ignored_falls_back_to_raw():
    text = f"```python\nprint('hi')\n```\ndiff --git a/x.py b/x.py\n{DIFF}"
    out = extract_diff(text)
    assert out.startswith("diff --git a/x.py")


# ---- normalize_patch: mechanical hunk-count repair -------------------------

def test_normalize_fixes_wrong_hunk_counts():
    bad = ("--- a/x.py\n+++ b/x.py\n"
           "@@ -56,16 +56,20 @@ class RST\n ctx1\n-old\n+new\n ctx2\n")
    out = extract_diff(f"```diff\n{bad}```")
    assert "@@ -56,3 +56,3 @@ class RST" in out
    assert "-old\n+new" in out


def test_normalize_restores_blank_context_line():
    bad = "--- a/x.py\n+++ b/x.py\n@@ -1,9 +1,9 @@\n a\n\n+b\n c\n"
    out = extract_diff(f"<patch>\n{bad}</patch>")
    lines = out.split("\n")
    assert lines[4] == " "  # bare blank inside hunk becomes a context blank
    assert lines[2] == "@@ -1,3 +1,4 @@"


def test_normalize_idempotent_on_correct_patch():
    assert normalize_patch(DIFF) == DIFF


def test_normalize_multi_hunk_and_file():
    bad = ("--- a/x.py\n+++ b/x.py\n"
           "@@ -1,9 +1,9 @@\n-a\n+b\n"
           "@@ -10,1 +10,1 @@\n c\n-d\n+e\n"
           "--- a/y.py\n+++ b/y.py\n"
           "@@ -5 +5 @@\n-f\n+g\n")
    out = normalize_patch(bad)
    assert "@@ -1,1 +1,1 @@" in out
    assert "@@ -10,2 +10,2 @@" in out
    assert "@@ -5,1 +5,1 @@" in out


def test_normalize_no_newline_marker_not_counted():
    p = "--- a/x\n+++ b/x\n@@ -1,5 +1,5 @@\n-x\n+y\n\\ No newline at end of file\n"
    out = normalize_patch(p)
    assert "@@ -1,1 +1,1 @@" in out
    assert "\\ No newline at end of file" in out
