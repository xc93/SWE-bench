"""Per-instance prompt instantiation for the agentic replication arms.

Templates live in fvk_experiments/prompts/agentic/ (fvk-replicate.md,
review-control.md, baseline.md). Each is Grigore Rosu's verbatim
astropy_13236_fvk_prompt.md (see prompts/agentic/source/PROVENANCE.md) with
per-instance values replaced by `{field}` placeholders, plus three declared
deviations marked by whole-line HTML comments:
  (a) the kit is read from the staged local formal-verification-kit/ instead of
      being git-cloned from GitHub;
  (b) the workspace is pre-built and verified in a Phase 0 instead of created by
      the agent, and Phase 2 runs the pre-staged scripts/private_eval.py;
  (c) the answer key (reference solution + hidden tests) is relocated out of the
      agent's workspace: the full benchmark row is not staged, and the original's
      "Do not manually open private_eval/swebench_row_full.json" rule is replaced
      by a faithful line stating that scripts/private_eval.py reports only
      aggregate counts and the reference solution and hidden tests are not in the
      workspace.

Only astropy__astropy-13236 is verbatim. For every other instance the prompt is
a RECONSTRUCTION auto-generated from the public issue: it carries no likely-files
hint and is stamped with an HTML-comment provenance marker (RECONSTRUCTED_MARKER)
near the top, archived in the saved prompt but invisible as instruction text.

Pipeline: render(arm, row) == instantiate(load_template(path), fields) with the
reconstruction marker prepended for non-curated instances, where
fields = fields_for_instance(row). The fidelity test
(tests/test_agentic_prompts.py) asserts that this pipeline applied to the
astropy__astropy-13236 row reproduces his prompt byte-for-byte except the three
declared deviation hunks.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

AGENTIC_DIR = Path(__file__).resolve().parent.parent / "prompts" / "agentic"
ARMS = ("fvk-replicate", "review-control", "baseline")
TEMPLATE_PATHS = {arm: AGENTIC_DIR / f"{arm}.md" for arm in ARMS}

# {field} placeholders: lowercase identifiers only, so literal braces in shell/
# JSON/dict snippets (e.g. `{benchmark,patches}` or `{"k": v}`) never match.
_FIELD_RE = re.compile(r"\{([a-z][a-z0-9_]*)\}")
# Whole-line HTML comments (possibly spanning lines): template-authoring
# metadata (deviation markers), stripped before the prompt reaches an agent.
_COMMENT_RE = re.compile(r"(?ms)^[ \t]*<!--.*?-->[ \t]*\n")
_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

# PASS_TO_PASS count at or above which an instance gets the 13236 prompt's
# "regression-heavy" framing. His sympy sample (19 P2P) had no such note;
# 13236 (644 P2P) did. See PROVENANCE.md "Template ambiguities" item 9.
REGRESSION_HEAVY_P2P = 100

_REGRESSION_NOTE_HEAVY = (
    "This is a regression-heavy task. A v2 patch can be worse than v1 "
    "if it fixes the desired behavior but breaks regressions."
)
_REGRESSION_NOTE_LIGHT = (
    "A v2 patch can be worse than v1 if it fixes the desired behavior "
    "but breaks regressions."
)

# Curated per-instance editorial fields, copied EXACTLY from Rosu's verbatim
# prompt for that instance (prompts/agentic/source/). The fidelity test
# guarantees these stay byte-faithful. Instances without an entry get the
# mechanical derivations below.
_CURATED: dict[str, dict[str, str]] = {
    "astropy__astropy-13236": {
        "public_issue_gist": (
            "The public issue is about structured `np.array` objects being "
            "automatically transformed into `NdarrayMixin` when added to an "
            "Astropy `Table`."
        ),
        # Header + bullets + trailing blank line, copied EXACTLY from his prompt
        # (source lines "Likely relevant public files include:" .. the blank
        # before the gist). Only the curated 13236 prompt carries a likely-files
        # hint; reconstructed instances get an empty block (no file nudge).
        "likely_files_block": (
            "Likely relevant public files include:\n"
            "\n"
            "- `repo/astropy/table/table.py`\n"
            "- `repo/astropy/table/column.py`\n"
            "- `repo/astropy/table/tests/`\n"
            "\n"
        ),
        "instance_questions_block": (
            "2. What is the current behavior around structured `np.ndarray`, "
            "`Column`, `NdarrayMixin`, and `Table` construction?\n"
            "3. What does the public issue imply for Astropy 5.0 / 5.1 / future "
            "5.2 behavior?\n"
            "4. What behavior should remain unchanged for existing `Column` inputs?\n"
            "5. What behavior should remain unchanged for real mixin columns?\n"
            "6. What behavior should remain unchanged for non-structured ndarrays?\n"
            "7. What behavior should remain unchanged for masked columns and metadata?"
        ),
        "unrelated_behavior_bullet": "avoid changing unrelated table construction behavior;",
    },
}

# The only instance whose prompt is Grigore's verbatim wording. Every other
# instance's prompt is a reconstruction (no likely-files hint; provenance-stamped).
CURATED_INSTANCES = frozenset(_CURATED)

# Provenance stamp prepended to every reconstructed (non-curated) prompt. It is a
# whole-line HTML comment: archived in the saved/preview prompt but not agent
# instruction text, and identical across arms so it cancels in the
# fvk-replicate-vs-review-control comparison. (Note it is added AFTER
# load_template — which strips the templates' own deviation comments — so it does
# survive into the instantiated output, by design.)
RECONSTRUCTED_MARKER = (
    "<!-- RECONSTRUCTED PROMPT: auto-generated from the public issue; "
    "NOT Grigore's verbatim. Only astropy-13236 is verbatim. -->"
)


def is_reconstructed(instance_id: str) -> bool:
    """True iff this instance's prompt is a reconstruction (not Grigore's
    verbatim wording). Only the curated instances are verbatim."""
    return instance_id not in CURATED_INSTANCES


def render(template_path: str | Path, row: dict, *,
           row_offset: int | None = None) -> str:
    """Final per-instance prompt for an arm template and dataset `row`.

    Equivalent to instantiate(load_template(template_path),
    fields_for_instance(row)), with the RECONSTRUCTED_MARKER prepended for
    non-curated instances. This is the single entry point the runner
    (cfg.system_prompt_path()) and the preview builder (TEMPLATE_PATHS[arm])
    share, so the provenance stamp lands in every saved prompt identically.
    """
    fields = fields_for_instance(row, row_offset=row_offset)
    body = instantiate(load_template(template_path), fields)
    if is_reconstructed(row["instance_id"]):
        body = f"{RECONSTRUCTED_MARKER}\n\n{body}"
    return body


def load_template(path: str | Path) -> str:
    """Template body ready for instantiation: YAML frontmatter and whole-line
    HTML comments (deviation markers) stripped."""
    text = Path(path).read_text(encoding="utf-8")
    text = _FRONTMATTER_RE.sub("", text, count=1)
    text = _COMMENT_RE.sub("", text)
    return text


def instantiate(template_text: str, fields: dict[str, str]) -> str:
    """Strict `{field}` substitution.

    Every placeholder in the template must have a (string) value in `fields`;
    unknown/missing placeholders raise ValueError listing them. Extra keys in
    `fields` are allowed: fields_for_instance() returns the union of what the
    three arm templates need (baseline uses a subset).
    """
    wanted = set(_FIELD_RE.findall(template_text))
    missing = sorted(wanted - fields.keys())
    if missing:
        raise ValueError(f"template placeholders without field values: {missing}")
    bad = sorted(k for k in wanted if not isinstance(fields[k], str))
    if bad:
        raise ValueError(f"field values must be str: {bad}")
    return _FIELD_RE.sub(lambda m: fields[m.group(1)], template_text)


def fields_for_instance(row: dict, *, row_offset: int | None = None) -> dict[str, str]:
    """Build the template field dict from a SWE-bench_Verified dataset row.

    `row_offset` is the row's index in the test split (for the exact-row URL);
    if None it is looked up from the dataset (requires the HF cache).
    Derivations use only public row fields — never `patch`/`test_patch`.
    """
    instance_id = row["instance_id"]
    repo = row["repo"]
    base_commit = row["base_commit"]
    version = str(row.get("version", ""))
    # `module_name` is the top-level IMPORT name (what the env-verify line does
    # `import {module_name}` on), generalized via the env-spec adapter so it is
    # correct for repos whose distribution/org name differs from the import name
    # (e.g. scikit-learn/scikit-learn -> sklearn, sphinx-doc/sphinx -> sphinx).
    # For astropy this is "astropy", identical to the old `repo.split("/")[-1]`,
    # so the curated-13236 fidelity is unaffected. `repo_title` stays the DISPLAY
    # name from the repo path segment (not the import name), so it never becomes
    # e.g. "Sklearn"; for astropy it remains "Astropy".
    from .env_specs import import_name_for
    module_name = import_name_for(repo)
    repo_title = repo.split("/")[-1].capitalize()
    f2p_count = _count(row["FAIL_TO_PASS"])
    p2p_count = _count(row["PASS_TO_PASS"])
    if row_offset is None:
        row_offset = _lookup_row_offset(instance_id)
    problem = row.get("problem_statement", "")

    curated = _CURATED.get(instance_id, {})
    fields = {
        "instance_id": instance_id,
        "repo": repo,
        "repo_url": f"https://github.com/{repo}.git",
        "base_commit": base_commit,
        "base_commit_url": f"https://github.com/{repo}/commit/{base_commit}",
        "repo_title": repo_title,
        "module_name": module_name,
        "version": version,
        "difficulty": str(row.get("difficulty", "")),
        "fail_to_pass_count": str(f2p_count),
        "pass_to_pass_count": str(p2p_count),
        "row_url": (
            "https://datasets-server.huggingface.co/rows?dataset="
            f"princeton-nlp%2FSWE-bench_Verified&config=default&split=test"
            f"&offset={row_offset}&length=1"
        ),
        "regression_note": (
            _REGRESSION_NOTE_HEAVY if p2p_count >= REGRESSION_HEAVY_P2P
            else _REGRESSION_NOTE_LIGHT
        ),
        "public_issue_gist": curated.get(
            "public_issue_gist", _derive_gist(problem)),
        # Only the curated 13236 prompt carries a "likely relevant files" hint
        # (Grigore's verbatim wording). Reconstructed instances get an empty
        # block: no file-selection nudge. The block, when present, includes its
        # own "Likely relevant public files include:" header, so an empty value
        # drops the header too.
        "likely_files_block": curated.get("likely_files_block", ""),
        "instance_questions_block": curated.get(
            "instance_questions_block",
            _derive_instance_questions(repo_title, version)),
        "unrelated_behavior_bullet": curated.get(
            "unrelated_behavior_bullet",
            "avoid changing behavior unrelated to the public issue;"),
    }
    return fields


# ---------------------------------------------------------------- derivations

def _count(tests) -> int:
    """len() of a FAIL_TO_PASS/PASS_TO_PASS column (JSON-encoded list or list)."""
    if isinstance(tests, str):
        tests = json.loads(tests)
    if not isinstance(tests, list):
        raise ValueError(f"expected test list, got {type(tests).__name__}")
    return len(tests)


def _lookup_row_offset(instance_id: str) -> int:
    from datasets import load_dataset  # lazy: needs HF cache/network

    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    for i, iid in enumerate(ds["instance_id"]):
        if iid == instance_id:
            return i
    raise ValueError(f"{instance_id} not in SWE-bench_Verified:test")


def _derive_gist(problem_statement: str) -> str:
    """One-line gist = the issue title (first non-empty line), quoted."""
    for line in problem_statement.splitlines():
        title = line.strip()
        if title:
            break
    else:
        title = "(no public problem statement)"
    title = title.rstrip(".")
    return f'The public issue is: "{title}".'


def _derive_instance_questions(repo_title: str, version: str) -> str:
    """Generic stand-ins for the 13236 prompt's instance-specific questions
    2-7, preserving its fixed 1..11 numbering and its pattern of one
    current-behavior question, one version-implication question, and four
    'what must remain unchanged' non-regression questions."""
    return "\n".join([
        "2. What is the current behavior in the code paths the public issue implicates?",
        f"3. What does the public issue imply for {_version_span(repo_title, version)} behavior?",
        "4. What behavior should remain unchanged for the public APIs the patch touches?",
        "5. What behavior should remain unchanged for related code paths and their callers?",
        "6. What behavior should remain unchanged for inputs outside the issue's scope?",
        "7. What behavior should remain unchanged for edge cases, error handling, and metadata?",
    ])


def _version_span(repo_title: str, version: str) -> str:
    """'Astropy 5.0 / 5.1 / future 5.2' (the 13236 pattern), or a plain
    fallback when the version is not dotted-numeric."""
    m = re.fullmatch(r"(\d+)\.(\d+)", version)
    if not m:
        return f"{repo_title} {version} and future".strip()
    major, minor = int(m.group(1)), int(m.group(2))
    return (f"{repo_title} {major}.{minor} / {major}.{minor + 1} / "
            f"future {major}.{minor + 2}")
