"""Per-instance workspaces for agentic (claude-code) arms, plus the private evaluator.

A workspace is everything one headless Claude Code session may touch:

    fvk_experiments/workspaces/<run_id>/<instance_id>/
      benchmark/public_instance.json   PUBLIC fields only (no patches, no test names)
      benchmark/PROMPT.md              public fields + problem statement + evaluator shape
      repo/                            history-truncated checkout @ base_commit (see below)
      .venv/                           pre-built env: editable repo install + test deps
                                       (repo/.venv is a symlink to it — both the templates'
                                       `.venv/bin/python` and tooling that expects the venv
                                       inside repo/ resolve to the same env)
      patches/  reports/               empty; the protocol writes its outputs here
      scripts/private_eval.py               [phased arms only] aggregate-only evaluator
      fvk/ + formal-verification-kit/       [fvk-replicate only] scratch dir + kit copy
      review/                               [review-control only] scratch dir
      manifest.json                    staged-file shas + provenance

ANSWER-KEY ISOLATION — the full benchmark row (patch, test_patch, FAIL_TO_PASS,
PASS_TO_PASS) is NOT staged into the workspace. It is written to a runner path
OUTSIDE the workspace, under the run dir:

    fvk_experiments/runs/<run_id>/private/<instance_id>/row.json

The phased arms still get scripts/private_eval.py in the workspace, invoked
exactly as `.venv/bin/python scripts/private_eval.py <patch> <label>`; the
script locates the row via an ABSOLUTE path baked into it as a constant at stage
time (ROW_PATH = "<run_dir>/private/<iid>/row.json"). The agent receives
identical aggregate feedback but no longer has a casual in-workspace file to
peek at. HONEST CAVEAT: the row is still on the same filesystem — a determined
bash agent could `find / -name row.json`; true OS-level isolation (separate
user / container) is future work, with the enforcement audit (claude_code.py)
as the backstop that invalidates any instance whose transcript reads the row.

LEAK REMOVAL — the checkout is history-truncated on purpose: the upstream clone
(kept once per repo in workspaces/.cache/<org>__<repo>.git) contains the future
fix commit, so the workspace tree is materialized from base_commit and re-rooted
with `git init && git add -A && git commit -m base`. The fix commit (and all
other history) is PHYSICALLY absent from repo/.git — `git log`/`git show` cannot
reach it. The single base commit is tagged `fvk-base` so the private evaluator
can reconstruct a pristine base tree without trusting the agent's working copy.

The pinned base commit is created AFTER the venv build so that in-place build
artifacts (compiled extensions, generated version.py) are part of `fvk-base`:
the evaluator's temp copies are then test-runnable without rebuilding, and the
agent's `git diff` stays clean. `.venv/` itself is kept out of the commit via
`.git/info/exclude` (untracked ignore — the tracked tree stays byte-identical
to upstream at base_commit, so agent diffs apply cleanly in the official
harness).

ENVIRONMENT BUILD (mirrors the swebench docker images): install specs come from
swebench.harness.constants.MAP_REPO_VERSION_TO_SPECS — for the astropy 4.1–5.2
instances that is python 3.9, a pinned pip list (numpy==1.25.2,
setuptools==68.0.0, the pytest-astropy family, ...), the pyproject
setuptools-pin sed, then `pip install -e .[test]`. Pins solved for this host:
  - the host only ships python 3.12, while astropy 4.x/5.x needs <=3.11
    (cython 0.29.x / numpy 1.2x build constraints): the venv is created with
    `uv venv --seed --python <spec version>`, letting uv fetch a managed
    CPython (one-time download, cached by uv);
  - the truncated history breaks setuptools_scm version detection (no tags),
    so the build exports SETUPTOOLS_SCM_PRETEND_VERSION=<row version>;
  - `python -m pip` from inside the venv does the installs, so the workspace
    needs nothing from the host venv at session time.

SESSION CONTAMINATION: a Claude Code session auto-discovers ancestor CLAUDE.md
files from its cwd, and this repo's CLAUDE.md describes the experiment — so
workspaces must live OUTSIDE the checkout. workspaces_root() therefore DEFAULTS
to ~/.cache/fvk-workspaces (override FVK_WORKSPACES_DIR); nothing about a session
cwd is a repo ancestor. (The complementary leak — user CLAUDE.md / memory /
plugins from the real $HOME — is sealed off separately by agents/profile.py.)

PROTOCOL v2 (45-instance prep; templates prompts/agentic/<arm>-v2.md). Two
infra changes, both keyed on the TEMPLATE's frontmatter `version:` (the
template IS the protocol, so the workspace follows it):

  1. AGENT-BUILT ENV. v2 reverts deviation (b)'s env half: the agent creates
     its own venv and installs the repo in Phase 0 (Grigore's original
     protocol), so most v2 workspaces get NO pre-built .venv. EXCEPT the six
     HARD_VENV_INSTANCES (compiled-dep builds agents struggle with), which
     keep the pre-staged ready .venv. The repo itself stays pre-staged at
     base_commit with truncated history and no remote in every case — the
     no-clone leak fence is not relaxed.

  2. DOCKER-AUTHORITATIVE GRADING. v2's scripts/private_eval.py keeps the
     exact CLI (`python scripts/private_eval.py <patch> <tag>`) and the exact
     three-line aggregate output, but internally grades by replaying the patch
     inside the instance's official prebuilt SWE-bench docker image — the SAME
     eval script and log parsing the official harness uses — instead of a
     local-venv pytest run. The agent's venv is only its scratchpad for public
     tests; it never produces the reported numbers. The eval payload (image
     candidates + the official eval script, which embeds the hidden
     test_patch) is staged into the OUT-OF-WORKSPACE row.json, never into the
     workspace. The workspace builder pre-pulls the image so sessions never
     need registry access at eval time.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from .config import Config, EXP_ROOT

# Parallel workers all build workspaces for the same repo: serialize the
# one-time bare-cache clone (uv serializes its own python downloads).
_CACHE_LOCK = threading.Lock()

# ---------------------------------------------------------------------------
# Arm kinds: which files an arm's workspace gets.
# ---------------------------------------------------------------------------

ARM_BASELINE = "baseline"            # single-pass: no private evaluator, no kit
ARM_REVIEW = "review-control"        # 5-phase protocol, no kit (control for fvk)
ARM_FVK = "fvk-replicate"            # 5-phase protocol + formal-verification-kit

PHASED_KINDS = (ARM_FVK, ARM_REVIEW)
ALL_KINDS = (ARM_BASELINE, ARM_FVK, ARM_REVIEW)

DEFAULT_KIT_DIR = Path("/home/xc/Projects/formal-verification-kit")

# Protocol v2, decision (2): the ONLY instances that get a pre-staged ready
# .venv under v2 (compiled-dependency builds agents demonstrably struggle
# with). Every other v2 instance gets no venv — the agent builds its own in
# Phase 0. Under protocol v1 every workspace keeps its pre-built venv.
HARD_VENV_INSTANCES = frozenset({
    "astropy__astropy-13398",
    "astropy__astropy-13579",
    "astropy__astropy-14369",
    "pydata__xarray-3993",
    "pydata__xarray-6992",
    "scikit-learn__scikit-learn-25102",
})


def protocol_version(cfg: Config) -> int:
    """Protocol major version from the arm template's frontmatter `version:`
    (cfg.prompt_version() -> "v1"/"v2"/...). Anything unparsable is v1: every
    pre-v2 template either says `version: 1` or predates the convention."""
    v = cfg.prompt_version() or ""
    m = re.match(r"v(\d+)", v)
    return int(m.group(1)) if m else 1


def venv_prestaged(cfg: Config, instance_id: str) -> bool:
    """Should this workspace get a pre-built .venv? v1: always (deviation (b)).
    v2: only the HARD_VENV_INSTANCES (decision (1)+(2) of the 45-run design)."""
    if protocol_version(cfg) < 2:
        return True
    return instance_id in HARD_VENV_INSTANCES

# ---------------------------------------------------------------------------
# Per-instance env policy (45-instance multi-repo run; see PREP_NOTES.md)
# ---------------------------------------------------------------------------
# Canonical policy lives just above: HARD_VENV_INSTANCES (the 6 compiled-dep ids
# that keep a pre-built venv under v2) + protocol_version() + venv_prestaged()
# (v1 => always pre-built, preserving the live astropy10 run; v2 => only the
# hard ids, agent self-builds the rest in Phase 0). The names below are stable
# aliases the configs/generator, tests, and PREP_NOTES refer to.
HARD_PREBUILD_IDS = HARD_VENV_INSTANCES


def should_prebuild_env(instance_id: str, override: bool | None = None) -> bool:
    """Default pre-build decision by instance id (override wins when given).

    Thin id-only wrapper over the hard-set membership test, for call sites that
    don't have a cfg in hand (the cfg-aware, protocol-keyed default is
    venv_prestaged(cfg, iid), which build_workspace uses). With override=None:
    the 6 hard compiled-dependency instances => True, everything else => False.
    """
    if override is not None:
        return override
    return instance_id in HARD_VENV_INSTANCES


# Grading backends for scripts/private_eval.py (phased arms). The agent's
# self-built env is only its scratchpad; AUTHORITATIVE grading must use the
# instance's official prebuilt docker image (the existing harness eval path),
# NOT a local temp copy. "local" is the v1 behavior (kept as default so the
# astropy10 run and all current tests are unaffected); "docker" is the v2 draft.
GRADING_LOCAL = "local"
GRADING_DOCKER = "docker"


def arm_kind_for_tag(tag: str) -> str:
    """Map an arm tag to its workspace kind ('fvk-replicate-v2' -> fvk-replicate)."""
    for kind in (ARM_FVK, ARM_REVIEW, ARM_BASELINE):  # longest/most specific first
        if tag == kind or tag.startswith(kind + "-"):
            return kind
    raise ValueError(
        f"cannot derive an agentic arm kind from tag {tag!r} — expected one of "
        f"{ALL_KINDS} (optionally with a -suffix)")


def workspaces_root() -> Path:
    # DEFAULT is out-of-repo: a session cwd under EXP_ROOT/workspaces would have
    # this repo's experiment-describing CLAUDE.md as a discoverable ancestor.
    env = os.environ.get("FVK_WORKSPACES_DIR")
    return Path(env) if env else Path.home() / ".cache" / "fvk-workspaces"


def kit_dir() -> Path:
    env = os.environ.get("FVK_KIT_DIR")
    return Path(env) if env else DEFAULT_KIT_DIR


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str], cwd: Path | None = None, env: dict | None = None,
         log: Path | None = None, timeout: int = 3600) -> None:
    """Run a build step; on failure raise loudly with the tail of its output."""
    proc = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env, timeout=timeout,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if log:
        with log.open("a") as fh:
            fh.write(f"\n$ {' '.join(str(c) for c in cmd)}\n{proc.stdout or ''}")
    if proc.returncode != 0:
        tail = (proc.stdout or "")[-4000:]
        raise RuntimeError(
            f"workspace build step failed ({proc.returncode}): "
            f"{' '.join(str(c) for c in cmd)}\n{tail}")


def listify(value) -> list[str]:
    """F2P/P2P fields arrive as JSON-encoded strings from HF datasets."""
    if isinstance(value, str):
        return json.loads(value)
    return list(value or [])


# ---------------------------------------------------------------------------
# Repo checkout: shared bare cache -> truncated working copy
# ---------------------------------------------------------------------------

def _cache_key(repo: str) -> str:
    return repo.replace("/", "__") + ".git"


def ensure_bare_cache(repo: str, base_commit: str, repo_src: str | None = None,
                      root: Path | None = None) -> Path:
    """Clone (once) a bare cache for `repo`; fetch if base_commit is missing.

    `repo_src` overrides the clone source (local path or URL) — used by tests
    with a local fixture repo so unit tests never touch the network.
    """
    cache = (root or workspaces_root()) / ".cache" / _cache_key(repo)
    src = repo_src or f"https://github.com/{repo}.git"
    with _CACHE_LOCK:
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            _run(["git", "clone", "--bare", src, cache])
    have = subprocess.run(["git", "-C", str(cache), "cat-file", "-e",
                           f"{base_commit}^{{commit}}"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if have.returncode != 0:
        _run(["git", "-C", cache, "fetch", "origin",
              "+refs/heads/*:refs/heads/*", "--tags"])
        have = subprocess.run(["git", "-C", str(cache), "cat-file", "-e",
                               f"{base_commit}^{{commit}}"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if have.returncode != 0:
            raise RuntimeError(f"{base_commit} not found in {src} (cache {cache})")
    return cache


def _checkout_truncated(cache: Path, base_commit: str, repo_dir: Path) -> None:
    """Materialize base_commit into repo_dir with NO upstream history/.git."""
    # --shared keeps this fast (no object copy); the .git is removed right after,
    # so nothing in the workspace references the cache (or any future commit).
    _run(["git", "clone", "-q", "--shared", "--no-checkout", cache, repo_dir])
    _run(["git", "-C", repo_dir, "checkout", "-q", "--detach", base_commit])
    shutil.rmtree(repo_dir / ".git")
    _run(["git", "-C", repo_dir, "init", "-q"])
    exclude = repo_dir / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    # Untracked ignores: keep the venv/build noise out of the base commit while
    # leaving every tracked file byte-identical to upstream@base_commit.
    # (".venv" without a slash: repo/.venv is a SYMLINK, and dir-only patterns
    # would not match it.)
    exclude.write_text(".venv\n__pycache__/\n*.pyc\n*.egg-info/\n.pytest_cache/\n")


def _commit_base(repo_dir: Path) -> str:
    git_id = ["-c", "user.name=fvk-bench", "-c", "user.email=fvk-bench@localhost"]
    _run(["git", "-C", repo_dir, "add", "-A"])
    _run(["git", "-C", repo_dir, *git_id, "commit", "-q", "-m", "base"])
    _run(["git", "-C", repo_dir, "tag", "fvk-base"])
    head = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True)
    return head.stdout.strip()


# ---------------------------------------------------------------------------
# Environment (venv) build — mirrors the swebench image specs
# ---------------------------------------------------------------------------

def _uv() -> str:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv not found on PATH — required to build workspace venvs")
    return uv


def _needs_legacy_pip(spec: dict) -> bool:
    """True when the image spec's install steps use pip options modern pip
    dropped (`--no-use-pep517`, removed in pip 25 — the scikit-learn specs need
    it for their legacy cython in-place builds). The official env images carry
    an era-appropriate pip; our uv-seeded venv gets the latest, so we downgrade
    pip first for exactly these specs (validated on scikit-learn-25102)."""
    lines = [spec.get("install") or ""] + list(spec.get("pre_install") or [])
    return any("--no-use-pep517" in line for line in lines)


def _pipify_conda_pin(token: str) -> str:
    """Translate one conda-style `name==x.y.z` pin to pip `name~=x.y.z` (same
    minor series, wheels permitting); anything else passes through verbatim."""
    name, sep, ver = token.partition("==")
    if sep and re.fullmatch(r"[0-9][0-9.]*", ver):
        return f"{name}~={ver}"
    return token


def build_repo_venv(ws: Path, repo_dir: Path, row: dict, log: Path) -> dict:
    """Create <ws>/.venv mirroring what the swebench image installs for this row,
    plus a repo/.venv symlink to it (the session templates use `.venv/bin/python`
    from the workspace root; the private evaluator accepts either location).

    Returns {"python": ..., "spec_source": ...} for the manifest. Failures raise
    (loud by design — a half-built env would silently bias an arm).
    """
    from swebench.harness.constants import MAP_REPO_VERSION_TO_SPECS

    spec = (MAP_REPO_VERSION_TO_SPECS.get(row["repo"], {}) or {}).get(
        str(row.get("version")), {})
    py_version = spec.get("python", f"{sys.version_info[0]}.{sys.version_info[1]}")
    venv = ws / ".venv"
    # --seed: give the agent a pip inside the venv, like the docker images have.
    # uv fetches the managed CPython if the host lacks it (host has only 3.12).
    _run([_uv(), "venv", "--seed", "--python", py_version, venv], log=log)
    (repo_dir / ".venv").symlink_to(Path("..") / ".venv")
    py = venv / "bin" / "python"

    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    # Truncated history => setuptools_scm cannot derive a version; pretend the
    # dataset's version (PEP440-valid for astropy rows: "4.3", "5.0", ...).
    if row.get("version"):
        env["SETUPTOOLS_SCM_PRETEND_VERSION"] = str(row["version"])

    if _needs_legacy_pip(spec):
        # The spec's install uses --no-use-pep517 (dropped in pip 25); match the
        # era-appropriate pip the official env images carry.
        _run([py, "-m", "pip", "install", "pip<25"], cwd=repo_dir, env=env, log=log)

    for cmd in spec.get("pre_install", []) or []:
        if "apt-get" in cmd:  # host build: no root/apt — images need it for graphviz etc.
            print(f"    [venv] skipping apt-get pre_install step: {cmd!r}", flush=True)
            continue
        _run(["bash", "-c", cmd], cwd=repo_dir, env=env, log=log)

    # spec["packages"]: the env image's conda install line. Three shapes:
    #   - a conda-style package list (often PINNED — scikit-learn pins
    #     cython==3.0.10 etc. here, NOT in pip_packages): pip-install it,
    #     BEFORE pip_packages (whose unpinned names then no-op via pip's
    #     already-satisfied rule, exactly like the image's conda->pip
    #     ordering). Conda `==` pins are relaxed to pip `~=` (same minor
    #     series) with --prefer-binary: conda ships binaries where PyPI has no
    #     wheel for that exact micro (numpy==1.19.2 has no cp39 wheel; ~=
    #     resolves 1.19.5) — the venv is the agent's SCRATCHPAD, grading is in
    #     docker, so era-faithful beats unbuildable. Validated on
    #     scikit-learn-25102.
    #   - "requirements.txt": install the repo's own requirements file.
    #   - "environment.yml": conda-only env file — SKIPPED like the apt-get
    #     steps; for these repos the spec's pip_packages carry the pinned
    #     testing deps (validated on the xarray hard instances).
    packages = (spec.get("packages") or "").strip()
    if packages == "requirements.txt":
        _run([py, "-m", "pip", "install", "-r", "requirements.txt"],
             cwd=repo_dir, env=env, log=log)
    elif packages == "environment.yml":
        print("    [venv] skipping conda environment.yml (pip_packages cover "
              "the testing deps)", flush=True)
    elif packages:
        import shlex
        _run([py, "-m", "pip", "install", "--prefer-binary",
              *(_pipify_conda_pin(tok) for tok in shlex.split(packages))],
             cwd=repo_dir, env=env, log=log)

    pips = spec.get("pip_packages", []) or []
    if pips:
        _run([py, "-m", "pip", "install", *pips], cwd=repo_dir, env=env, log=log)

    install = spec.get("install") or "python -m pip install -e .[test]"
    if install.startswith("python "):
        install = f"{py} " + install[len("python "):]
    try:
        _run(["bash", "-c", install], cwd=repo_dir, env=env, log=log)
    except RuntimeError:
        if spec:  # exact image spec failed — that is fatal, do not improvise
            raise
        _run([py, "-m", "pip", "install", "-e", "."], cwd=repo_dir, env=env, log=log)

    # pytest must be importable or the private evaluator is dead on arrival.
    check = subprocess.run([str(py), "-c", "import pytest"], capture_output=True)
    if check.returncode != 0:
        _run([py, "-m", "pip", "install", "pytest"], cwd=repo_dir, env=env, log=log)
    pyv = subprocess.run([str(py), "--version"], capture_output=True, text=True)
    return {"python": pyv.stdout.strip() or py_version,
            "spec_source": "swebench.MAP_REPO_VERSION_TO_SPECS" if spec else "generic"}


# ---------------------------------------------------------------------------
# Kit copy
# ---------------------------------------------------------------------------

def kit_commit_info(kit_path: Path) -> dict:
    def _git(*args):
        return subprocess.run(["git", "-C", str(kit_path), *args],
                              capture_output=True, text=True)
    sha = _git("rev-parse", "HEAD")
    if sha.returncode != 0:
        return {"kit_commit": None, "kit_dirty": None}
    dirty = _git("status", "--porcelain")
    return {"kit_commit": sha.stdout.strip(),
            "kit_dirty": bool(dirty.stdout.strip())}


def _copy_kit(kit_path: Path, dest: Path) -> dict:
    if not kit_path.is_dir():
        raise FileNotFoundError(f"formal-verification-kit working tree not found: {kit_path}")
    shutil.copytree(kit_path, dest, ignore=shutil.ignore_patterns(".git"))
    return kit_commit_info(kit_path)


# ---------------------------------------------------------------------------
# Docker-authoritative grading (protocol v2): staged eval payload + image pull
# ---------------------------------------------------------------------------
# The v2 private evaluator replays the patch inside the instance's official
# SWE-bench docker image. Everything it needs that involves hidden data (the
# official eval script embeds the test_patch heredoc) is computed here at stage
# time and written into the OUT-OF-WORKSPACE row.json under _staging.eval —
# the in-workspace script stays free of hidden content and stdlib-only.

def _docker_bin() -> str:
    # Test override: hermetic tests point this at a shim that emulates the few
    # docker subcommands the builder/evaluator use.
    return os.environ.get("FVK_DOCKER_BIN", "docker")


def _arch() -> str:
    m = platform.machine()
    return {"aarch64": "arm64", "x86_64": "x86_64"}.get(m, m)


def instance_image_candidates(row: dict, arch: str | None = None) -> list[str]:
    """Local docker image names that can grade this instance, most likely first.

    [0] the Docker-Hub namespaced name the harness pulls with its default
        namespace="swebench" (what `cache_level: instance` leaves behind on this
        host), with the official "__" -> "_1776_" mangling;
    [1] the unnamespaced name a local `--namespace none` build produces.
    Mirrors swebench.harness.test_spec.TestSpec.instance_image_key exactly.
    """
    arch = arch or _arch()
    iid = row["instance_id"].lower()
    base = f"sweb.eval.{arch}.{iid}:latest"
    return [f"swebench/{base}".replace("__", "_1776_"), base]


def supported_eval_parser(repo: str) -> str:
    """The private evaluator's parser id for `repo`, or raise if unsupported.

    The in-workspace evaluator is stdlib-only, so it carries FAITHFUL PORTS of
    the official log parsers (tests/test_agentic_infra.py proves port==official
    on shared samples). The five ports cover all 8 repos of the 45-instance
    Grigore-set: pytest_v2 (astropy, scikit-learn, sphinx), pytest (xarray,
    pytest-dev), pytest_options (pylint), django, sympy.
    """
    from swebench.harness.log_parsers import MAP_REPO_TO_PARSER
    from swebench.harness.log_parsers.python import (parse_log_django,
                                                     parse_log_pytest,
                                                     parse_log_pytest_options,
                                                     parse_log_pytest_v2,
                                                     parse_log_sympy)

    parser_fn = MAP_REPO_TO_PARSER.get(repo)
    by_fn = {
        parse_log_pytest_v2: "pytest_v2",
        parse_log_pytest: "pytest",
        parse_log_pytest_options: "pytest_options",
        parse_log_django: "django",
        parse_log_sympy: "sympy",
    }
    parser = by_fn.get(parser_fn)
    if parser is None:
        raise ValueError(
            f"docker grading unsupported for repo {repo!r}: official parser is "
            f"{getattr(parser_fn, '__name__', None)!r}, which has no port in "
            "the private evaluator")
    return parser


def docker_eval_staging(row: dict, timeout_s: int = 1800) -> dict:
    """The _staging.eval payload for the v2 docker evaluator.

    eval_script is the OFFICIAL harness eval script for this instance
    (swebench make_test_spec: conda activate, reset test files to base, apply
    test_patch, run test_cmd + directives between the official output markers,
    reset again) — so in-session aggregates and the final harness eval are the
    same mechanism. parser names the official log parser for this repo (see
    supported_eval_parser). Raises for repos the official spec map does not
    know — such an instance could not be graded by the final harness either.
    """
    from swebench.harness.test_spec.test_spec import make_test_spec

    parser = supported_eval_parser(row["repo"])
    spec = make_test_spec(row, namespace=None, arch=_arch())
    return {
        "mode": "docker-image",
        "image_candidates": instance_image_candidates(row),
        "eval_script": spec.eval_script,
        "parser": parser,
        "timeout_s": timeout_s,
    }


def ensure_instance_image(row: dict, *, log: Path | None = None,
                          retries: int = 2) -> str:
    """Make the instance's official eval image locally available; return its name.

    Tries the candidates in order with `docker image inspect`; if none exists,
    pulls the namespaced one (with retries — registry-1.docker.io flakes on this
    host). Loud failure: a phased v2 session without its image would hit a
    generic evaluator infra error mid-protocol, which is worse than failing the
    build."""
    candidates = instance_image_candidates(row)
    docker = _docker_bin()

    def _have(name: str) -> bool:
        p = subprocess.run([docker, "image", "inspect", name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.returncode == 0

    for name in candidates:
        if _have(name):
            return name
    last = ""
    for attempt in range(retries + 1):
        p = subprocess.run([docker, "pull", candidates[0]],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True)
        if log:
            with log.open("a") as fh:
                fh.write(f"\n$ {docker} pull {candidates[0]} "
                         f"(attempt {attempt + 1})\n{p.stdout or ''}")
        if p.returncode == 0 and _have(candidates[0]):
            return candidates[0]
        last = (p.stdout or "")[-1000:]
    raise RuntimeError(
        f"cannot obtain official eval image for {row['instance_id']} "
        f"(tried {candidates}, pull failed {retries + 1}x): {last}")


# ---------------------------------------------------------------------------
# The private evaluator (written into <ws>/scripts/private_eval.py, phased arms)
# ---------------------------------------------------------------------------
# Raw string TEMPLATE: emitted into the workspace script with the __ROW_PATH__
# token replaced by the ABSOLUTE path of the out-of-workspace row.json (see
# build_workspace). Stdlib-only on purpose — it must run under any python
# (system 3.12 or the repo venv) with zero installs. It only ever prints
# aggregates: the hidden FAIL_TO_PASS/PASS_TO_PASS test names must not be
# recoverable from its output. The benchmark row lives OUTSIDE the workspace, so
# the agent has no in-workspace answer-key file; the script reaches the row only
# via the constant baked in below.

PRIVATE_EVAL_SCRIPT = r'''#!/usr/bin/env python3
"""Aggregate-only private evaluator for this workspace.

Usage:  python scripts/private_eval.py <patch_file> <tag>

Applies <patch_file> to a TEMPORARY pristine copy of repo/ (your working tree
is never touched, and hidden tests never run inside it), applies the hidden
test patch, runs the benchmark test groups, and prints EXACTLY three lines:

    FAIL_TO_PASS <passed>/<total>
    PASS_TO_PASS <passed>/<total>
    resolved: <true|false>

No test names, no tracebacks, no logs — aggregates only. <tag> labels the
attempt (e.g. v1, v2) in the local eval log. Exits non-zero with a generic
message if the evaluator itself breaks (infrastructure error).
"""
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(WS, "repo")
# ABSOLUTE path to the full benchmark row, baked in at stage time. The row lives
# OUTSIDE this workspace (under the run dir's private/) so it is not a casual
# in-workspace peek target; only this evaluator reads it.
ROW_PATH = r"__ROW_PATH__"
LOG_PATH = os.path.join(WS, "private_eval", "eval_log.jsonl")
GROUP_TIMEOUT_S = 1500
DEFAULT_TEST_CMD = "pytest --no-header -rA --tb=no -p no:cacheprovider"
STATUSES = ("FAILED", "PASSED", "SKIPPED", "ERROR", "XFAIL")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def infra_fail():
    sys.stderr.write("private_eval: internal error; aggregates unavailable\n")
    sys.exit(2)


def listify(v):
    return json.loads(v) if isinstance(v, str) else list(v or [])


def quiet(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    return p.returncode == 0


def apply_patch(patch_file, cwd):
    if quiet(["git", "apply", "--whitespace=nowarn", patch_file], cwd):
        return True
    return quiet(["patch", "-p1", "--batch", "--fuzz=5", "-i", patch_file], cwd)


def patched_files(diff_text):
    files = set()
    for m in re.finditer(r"^diff --git a/(\S+) b/(\S+)", diff_text, re.M):
        files.update(m.groups())
    for m in re.finditer(r"^(?:---|\+\+\+) [ab]/(\S+)", diff_text, re.M):
        files.add(m.group(1))
    return sorted(files)


def extract_base(work, paths=None):
    """Unpack the pristine `fvk-base` tree (or a subset) into `work`.

    Import semantics of the reconstructed tree (verified on astropy 5.0):
    pure-python modules load from THIS patched copy (cwd is sys.path[0] under
    `python -m pytest`), while compiled extensions — gitignored upstream, so
    absent from fvk-base — fall back to the prebuilt in-place .so files of the
    live repo/ via the venv's PEP-660 editable finder. That mirrors the docker
    harness exactly: patched source + base-build extensions, no rebuild.
    """
    cmd = ["git", "-C", REPO, "archive", "--format=tar", "fvk-base"]
    if paths:
        cmd += ["--"] + list(paths)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if p.returncode != 0:
        return False
    tf = tarfile.open(fileobj=io.BytesIO(p.stdout), mode="r:")
    try:
        tf.extractall(work, filter="tar")
    except TypeError:  # python < 3.12: no filter kwarg
        tf.extractall(work)
    return True


def parse_statuses(out):
    # Mirrors the official harness pytest parser: first token is a status ->
    # token[1] is the test id; old pytest styles put the status last.
    statuses = {}
    for raw in out.split("\n"):
        line = ANSI.sub("", raw).strip()
        toks = line.split()
        if len(toks) < 2:
            continue
        if toks[0] in STATUSES:
            statuses[toks[1]] = toks[0]
        elif toks[-1] in STATUSES:
            statuses[toks[0]] = toks[-1]
    return statuses


def selector(tid):
    # SWE-bench F2P/P2P lists are built by whitespace-splitting pytest output,
    # so a parametrized id containing spaces arrives TRUNCATED in the dataset
    # (e.g. "...::test_non_mapping_init[ceci"). Such an id can never select a
    # test (pytest exits 4 and runs NOTHING) — select its test function instead
    # (a superset). Counting below uses the same whitespace-truncated keys the
    # official harness parser produces, so membership still matches exactly.
    if "[" in tid and not tid.endswith("]"):
        return tid.split("[", 1)[0]
    return tid


def run_group(venv_py, test_cmd, ids, cwd):
    if not ids:
        return 0
    toks = shlex.split(test_cmd)
    if not toks or toks[0] != "pytest":
        toks = shlex.split(DEFAULT_TEST_CMD)
    sels = []
    for t in ids:
        s = selector(t)
        if s not in sels:
            sels.append(s)
    # `python -m pytest` (not bin/pytest): -m puts cwd first on sys.path, so the
    # PATCHED temp copy shadows the editable install that points at repo/.
    cmd = [venv_py, "-m", "pytest"] + toks[1:] + sels
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTEST_ADDOPTS", None)
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                       timeout=GROUP_TIMEOUT_S)  # output captured and DISCARDED
    statuses = parse_statuses(p.stdout or "")
    return sum(1 for t in ids if statuses.get(t) in ("PASSED", "XFAIL"))


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: python scripts/private_eval.py <patch_file> <tag>\n")
        return 2
    patch_file, tag = os.path.abspath(argv[1]), argv[2]
    try:
        with open(ROW_PATH) as fh:
            row = json.load(fh)
        f2p, p2p = listify(row["FAIL_TO_PASS"]), listify(row["PASS_TO_PASS"])
        test_cmd = (row.get("_staging") or {}).get("test_cmd") or DEFAULT_TEST_CMD
        venv_py = os.path.join(WS, ".venv", "bin", "python")  # repo/.venv symlinks here
        if not os.path.exists(venv_py):
            venv_py = os.path.join(REPO, ".venv", "bin", "python")
        if not (os.path.exists(venv_py) and os.path.exists(patch_file)):
            infra_fail()
        with open(patch_file) as fh:
            patch_text = fh.read()

        applied = True
        f2p_pass = p2p_pass = 0
        tmp = tempfile.mkdtemp(prefix="fvk-private-eval-")
        try:
            work = os.path.join(tmp, "repo")
            os.makedirs(work)
            if not extract_base(work):
                infra_fail()
            if patch_text.strip():
                applied = apply_patch(patch_file, work)
            if applied:
                # Hidden tests are evaluated as base + test_patch, exactly like
                # the official harness: discard any model edits to those files.
                tfiles = patched_files(row["test_patch"])
                at_base = [f for f in tfiles
                           if quiet(["git", "-C", REPO, "cat-file", "-e",
                                     "fvk-base:" + f], None)]
                for f in tfiles:
                    if f not in at_base:
                        target = os.path.join(work, f)
                        if os.path.lexists(target):
                            os.remove(target)
                if at_base and not extract_base(work, at_base):
                    infra_fail()
                tp = os.path.join(tmp, "hidden_test.patch")
                with open(tp, "w") as fh:
                    fh.write(row["test_patch"])
                if not apply_patch(tp, work):
                    infra_fail()
                f2p_pass = run_group(venv_py, test_cmd, f2p, work)
                p2p_pass = run_group(venv_py, test_cmd, p2p, work)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        resolved = applied and f2p_pass == len(f2p) and p2p_pass == len(p2p)
        sys.stdout.write("FAIL_TO_PASS %d/%d\n" % (f2p_pass, len(f2p)))
        sys.stdout.write("PASS_TO_PASS %d/%d\n" % (p2p_pass, len(p2p)))
        sys.stdout.write("resolved: %s\n" % ("true" if resolved else "false"))
        if not applied:
            sys.stderr.write("note: patch did not apply cleanly; tests were not run\n")
        try:
            with open(LOG_PATH, "a") as fh:
                fh.write(json.dumps({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "tag": tag, "applied": applied,
                    "FAIL_TO_PASS": "%d/%d" % (f2p_pass, len(f2p)),
                    "PASS_TO_PASS": "%d/%d" % (p2p_pass, len(p2p)),
                    "resolved": resolved}) + "\n")
        except OSError:
            pass
        return 0
    except SystemExit:
        raise
    except BaseException:
        infra_fail()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''


# ---------------------------------------------------------------------------
# The v2 private evaluator: same CLI + same three-line output, but grades by
# replaying the patch inside the instance's OFFICIAL prebuilt SWE-bench docker
# image (decision (3) of the 45-run design). Stdlib-only; docker via subprocess.
# The eval payload (image names, official eval script with the test_patch
# heredoc, parser id, timeout) comes from _staging.eval of the out-of-workspace
# row.json — nothing hidden is in the workspace. All container output is either
# discarded or logged NEXT TO the row (outside the workspace); stdout carries
# only the three aggregate lines.
# ---------------------------------------------------------------------------

PRIVATE_EVAL_SCRIPT_DOCKER = r'''#!/usr/bin/env python3
"""Aggregate-only private evaluator for this workspace.

Usage:  python scripts/private_eval.py <patch_file> <tag>

Applies <patch_file> to a TEMPORARY pristine copy of the repository at the base
commit (your working tree is never touched, and hidden tests never run inside
it), applies the hidden test patch, runs the benchmark test groups, and prints
EXACTLY three lines:

    FAIL_TO_PASS <passed>/<total>
    PASS_TO_PASS <passed>/<total>
    resolved: <true|false>

Scores are computed inside the instance's official SWE-bench evaluation image,
so they match the official grader. No test names, no tracebacks, no logs —
aggregates only. <tag> labels the attempt (e.g. v1, v2) in the local eval log.
Exits non-zero with a generic message if the evaluator itself breaks
(infrastructure error).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ABSOLUTE path to the full benchmark row, baked in at stage time. The row lives
# OUTSIDE this workspace (under the run dir's private/) so it is not a casual
# in-workspace peek target; only this evaluator reads it.
ROW_PATH = r"__ROW_PATH__"
LOG_PATH = os.path.join(WS, "private_eval", "eval_log.jsonl")
DOCKER = os.environ.get("FVK_DOCKER_BIN", "docker")
# Model-patch application, exactly the official harness order
# (swebench.harness.run_evaluation.GIT_APPLY_CMDS).
GIT_APPLY_CMDS = ("git apply --verbose", "git apply --verbose --reject",
                  "patch --batch --fuzz=5 -p1 -i")
START_MARK = ">>>>> Start Test Output"
END_MARK = ">>>>> End Test Output"
STATUSES = ("FAILED", "PASSED", "SKIPPED", "ERROR", "XFAIL")


def infra_fail():
    sys.stderr.write("private_eval: internal error; aggregates unavailable\n")
    sys.exit(2)


def listify(v):
    return json.loads(v) if isinstance(v, str) else list(v or [])


def docker(args, timeout=120, quiet=False):
    """Run one docker CLI call; combined output captured (never to stdout)."""
    p = subprocess.run([DOCKER] + args, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, timeout=timeout)
    return p.returncode, ("" if quiet else (p.stdout or ""))


# --- log parsers: FAITHFUL PORTS of swebench.harness.log_parsers.python ----
# (tests/test_agentic_infra.py proves port == official function on shared
# samples). Keys come out exactly like the official parser's, so membership
# against the dataset's test ids matches the harness. Five ports cover the
# 45-instance Grigore-set: pytest_v2 (astropy, scikit-learn, sphinx), pytest
# (xarray, pytest-dev), pytest_options (pylint), django, sympy.

def _parse_pytest(log):
    statuses = {}
    for line in log.split("\n"):
        if any(line.startswith(s) for s in STATUSES):
            if line.startswith("FAILED"):
                line = line.replace(" - ", " ")
            toks = line.split()
            if len(toks) <= 1:
                continue
            statuses[toks[1]] = toks[0]
    return statuses


def _parse_pytest_v2(log):
    statuses = {}
    escapes = "".join(chr(c) for c in range(1, 32))
    table = str.maketrans("", "", escapes)
    for line in log.split("\n"):
        line = re.sub(r"\[(\d+)m", "", line).translate(table)
        if any(line.startswith(s) for s in STATUSES):
            if line.startswith("FAILED"):
                line = line.replace(" - ", " ")
            toks = line.split()
            if len(toks) >= 2:
                statuses[toks[1]] = toks[0]
        elif any(line.endswith(s) for s in STATUSES):
            toks = line.split()
            if len(toks) >= 2:
                statuses[toks[0]] = toks[1]
    return statuses


def _parse_pytest_options(log):
    option_pattern = re.compile(r"(.*?)\[(.*)\]")
    statuses = {}
    for line in log.split("\n"):
        if any(line.startswith(s) for s in STATUSES):
            if line.startswith("FAILED"):
                line = line.replace(" - ", " ")
            toks = line.split()
            if len(toks) <= 1:
                continue
            has_option = option_pattern.search(toks[1])
            if has_option:
                main, option = has_option.groups()
                if option.startswith("/") and not option.startswith("//") \
                        and "*" not in option:
                    option = "/" + option.split("/")[-1]
                name = "{}[{}]".format(main, option)
            else:
                name = toks[1]
            statuses[name] = toks[0]
    return statuses


def _parse_django(log):
    statuses = {}
    prev_test = None
    for line in log.split("\n"):
        line = line.strip()
        if "--version is equivalent to version" in line:
            statuses["--version is equivalent to version"] = "PASSED"
        if " ... " in line:
            prev_test = line.split(" ... ")[0]
        for suffix in (" ... ok", " ... OK", " ...  OK"):
            if line.endswith(suffix):
                if line.strip().startswith(
                        "Applying sites.0002_alter_domain_unique...test_no_migrations"):
                    line = line.split("...", 1)[-1].strip()
                statuses[line.rsplit(suffix, 1)[0]] = "PASSED"
                break
        if " ... skipped" in line:
            statuses[line.split(" ... skipped")[0]] = "SKIPPED"
        if line.endswith(" ... FAIL"):
            statuses[line.split(" ... FAIL")[0]] = "FAILED"
        if line.startswith("FAIL:"):
            statuses[line.split()[1].strip()] = "FAILED"
        if line.endswith(" ... ERROR"):
            statuses[line.split(" ... ERROR")[0]] = "ERROR"
        if line.startswith("ERROR:"):
            statuses[line.split()[1].strip()] = "ERROR"
        if line.lstrip().startswith("ok") and prev_test is not None:
            statuses[prev_test] = "PASSED"
    for pattern in (
        r"^(.*?)\s\.\.\.\sTesting\ against\ Django\ installed\ in\ ((?s:.*?))\ silenced\)\.\nok$",
        r"^(.*?)\s\.\.\.\sInternal\ Server\ Error:\ \/(.*)\/\nok$",
        r"^(.*?)\s\.\.\.\sSystem check identified no issues \(0 silenced\)\nok$",
    ):
        for match in re.finditer(pattern, log, re.MULTILINE):
            statuses[match.group(1)] = "PASSED"
    return statuses


def _parse_sympy(log):
    statuses = {}
    for match in re.findall(r"(_*) (.*)\.py:(.*) (_*)", log):
        statuses["{}.py:{}".format(match[1], match[2])] = "FAILED"
    for line in log.split("\n"):
        line = line.strip()
        if line.startswith("test_"):
            if line.endswith(" E"):
                statuses[line.split()[0]] = "ERROR"
            if line.endswith(" F"):
                statuses[line.split()[0]] = "FAILED"
            if line.endswith(" ok"):
                statuses[line.split()[0]] = "PASSED"
    return statuses


PARSERS = {"pytest": _parse_pytest, "pytest_v2": _parse_pytest_v2,
           "pytest_options": _parse_pytest_options, "django": _parse_django,
           "sympy": _parse_sympy}


def parse_statuses(log, kind):
    parse = PARSERS.get(kind)
    if parse is None:
        infra_fail()
    return parse(log)


def test_section(output):
    """The slice between the official output markers (their xtrace lines), with
    the official fallback to the whole output when the marker slice parses to
    nothing (get_logs_eval does the same)."""
    if START_MARK in output and END_MARK in output:
        return output.split(START_MARK)[1].split(END_MARK)[0]
    return None


def passed(tid, statuses):
    # Official grading.test_passed: PASSED or XFAIL.
    return statuses.get(tid) in ("PASSED", "XFAIL")


def failed(tid, statuses):
    # Official grading.test_failed: missing from the map, FAILED, or ERROR.
    return tid not in statuses or statuses[tid] in ("FAILED", "ERROR")


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: python scripts/private_eval.py <patch_file> <tag>\n")
        return 2
    patch_file, tag = os.path.abspath(argv[1]), argv[2]
    try:
        with open(ROW_PATH) as fh:
            row = json.load(fh)
        ev = (row.get("_staging") or {}).get("eval") or {}
        f2p, p2p = listify(row["FAIL_TO_PASS"]), listify(row["PASS_TO_PASS"])
        if not (ev.get("image_candidates") and ev.get("eval_script")
                and os.path.exists(patch_file)):
            infra_fail()
        with open(patch_file) as fh:
            patch_text = fh.read()

        image = None
        for cand in ev["image_candidates"]:
            if docker(["image", "inspect", cand], quiet=True)[0] == 0:
                image = cand
                break
        if image is None:
            # Last resort (the workspace builder pre-pulls, so normally never):
            rc, _ = docker(["pull", ev["image_candidates"][0]], timeout=1800)
            if rc == 0:
                image = ev["image_candidates"][0]
        if image is None:
            infra_fail()

        cname = "fvk-private-eval-" + uuid.uuid4().hex[:12]
        applied = True
        statuses = {}
        forensics = []
        try:
            rc, out = docker(["run", "-d", "--name", cname, image,
                              "tail", "-f", "/dev/null"])
            if rc != 0:
                infra_fail()
            if patch_text.strip():
                rc, _ = docker(["cp", patch_file, cname + ":/tmp/fvk_patch.diff"])
                if rc != 0:
                    infra_fail()
                applied = False
                for cmd in GIT_APPLY_CMDS:
                    rc, out = docker(["exec", cname, "bash", "-c",
                                      "cd /testbed && %s /tmp/fvk_patch.diff" % cmd])
                    forensics.append("$ %s\n%s" % (cmd, out))
                    if rc == 0:
                        applied = True
                        break
            if applied:
                with tempfile.NamedTemporaryFile("w", suffix=".sh",
                                                 delete=False) as fh:
                    fh.write(ev["eval_script"])
                    eval_sh = fh.name
                try:
                    rc, _ = docker(["cp", eval_sh, cname + ":/fvk_eval.sh"])
                    if rc != 0:
                        infra_fail()
                    try:
                        # Combined stdout+stderr: the official markers are bash
                        # xtrace lines (stderr), pytest results are stdout.
                        rc, out = docker(["exec", cname, "/bin/bash", "/fvk_eval.sh"],
                                         timeout=int(ev.get("timeout_s") or 1800))
                    except subprocess.TimeoutExpired:
                        # Official semantics: a test timeout is a FAILED eval
                        # (">>>>> Tests Timed Out"), not an evaluator error.
                        out = ""
                    forensics.append(out)
                    section = test_section(out)
                    if section is not None:
                        statuses = parse_statuses(section, ev.get("parser"))
                        if not statuses:  # official whole-log fallback
                            statuses = parse_statuses(out, ev.get("parser"))
                finally:
                    os.unlink(eval_sh)
        finally:
            docker(["rm", "-f", cname], quiet=True)
            try:
                # Forensics OUTSIDE the workspace, next to the row (one file per
                # tag, overwritten — bounded). Never printed.
                logdir = os.path.join(os.path.dirname(ROW_PATH), "private_eval_logs")
                os.makedirs(logdir, exist_ok=True)
                with open(os.path.join(logdir, "%s.log" % tag), "w") as fh:
                    fh.write("\n".join(forensics)[-400000:])
            except OSError:
                pass

        f2p_pass = sum(1 for t in f2p if passed(t, statuses))
        p2p_pass = sum(1 for t in p2p if passed(t, statuses))
        # Official ResolvedStatus.FULL over success/failure ratios: resolved iff
        # nothing in either group FAILED/ERROR'd or went missing. (Counts below
        # stay passed/total for the stable aggregate interface; in the rare
        # all-SKIPPED corner the official ratio ignores skips, and we follow it.)
        resolved = applied and not any(failed(t, statuses) for t in f2p) \
            and not any(failed(t, statuses) for t in p2p)
        sys.stdout.write("FAIL_TO_PASS %d/%d\n" % (f2p_pass, len(f2p)))
        sys.stdout.write("PASS_TO_PASS %d/%d\n" % (p2p_pass, len(p2p)))
        sys.stdout.write("resolved: %s\n" % ("true" if resolved else "false"))
        if not applied:
            sys.stderr.write("note: patch did not apply cleanly; tests were not run\n")
        try:
            with open(LOG_PATH, "a") as fh:
                fh.write(json.dumps({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "tag": tag, "applied": applied,
                    "FAIL_TO_PASS": "%d/%d" % (f2p_pass, len(f2p)),
                    "PASS_TO_PASS": "%d/%d" % (p2p_pass, len(p2p)),
                    "resolved": resolved}) + "\n")
        except OSError:
            pass
        return 0
    except SystemExit:
        raise
    except BaseException:
        infra_fail()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''


# ---------------------------------------------------------------------------
# Workspace builder
# ---------------------------------------------------------------------------

def _public_instance(cfg: Config, row: dict, f2p_n: int, p2p_n: int) -> dict:
    """PUBLIC fields only — no patch, no test_patch, no test NAMES (counts only).

    Field style mirrors prompts/agentic/source/sympy__sympy-17630_public_instance.json
    (the reference staged file the prompt templates were authored against), plus
    the F2P/P2P aggregate COUNTS the protocol discloses.
    """
    repo = row["repo"]
    pub = {
        "dataset": cfg.dataset.name,
        "split": cfg.dataset.split,
        "repo": repo,
        "repo_url": f"https://github.com/{repo}.git",
        "instance_id": row["instance_id"],
        "base_commit": row["base_commit"],
        "base_commit_url": f"https://github.com/{repo}/commit/{row['base_commit']}",
        "problem_statement": row["problem_statement"],
        "hints_text": row.get("hints_text", ""),
        "created_at": row.get("created_at"),
        "version": row.get("version"),
        "difficulty": row.get("difficulty"),
        "environment_setup_commit": row.get("environment_setup_commit"),
        "FAIL_TO_PASS_count": f2p_n,
        "PASS_TO_PASS_count": p2p_n,
    }
    if row.get("_hf_offset") is not None:
        pub["hf_offset"] = row["_hf_offset"]
    if row.get("language"):
        pub["language"] = row["language"]
    return {k: v for k, v in pub.items() if v is not None}


def _prompt_md(row: dict, f2p_n: int, p2p_n: int) -> str:
    """Mirrors prompts/agentic/source/sympy__sympy-17630_PROMPT.md, plus the
    evaluator-shape line (the aggregate counts the protocol discloses)."""
    repo = row["repo"]
    bullets = [f"- repo: {repo}",
               f"- repo_url: https://github.com/{repo}.git",
               f"- base_commit: {row['base_commit']}"]
    for key in ("created_at", "version", "difficulty", "environment_setup_commit"):
        if row.get(key):
            bullets.append(f"- {key}: {row[key]}")
    return (f"# SWE-bench Verified instance {row['instance_id']}\n\n"
            + "\n".join(bullets) + "\n\n"
            f"## Problem statement\n\n```text\n{row['problem_statement'].strip()}\n```\n\n"
            f"## Hints / discussion\n\n```text\n{(row.get('hints_text') or '').strip()}\n```\n\n"
            f"## Evaluation\n\n"
            f"Evaluator shape: FAIL_TO_PASS {f2p_n}, PASS_TO_PASS {p2p_n}\n")


def _staging_extras(row: dict, grading_backend: str = GRADING_LOCAL,
                    eval_timeout_s: int = 1800) -> dict:
    """Derived keys staged alongside the OUT-OF-WORKSPACE row for the evaluator
    (underscored to distinguish them from real dataset fields).

    `test_cmd` (the spec's pytest command) feeds the LOCAL evaluator. For the
    DOCKER backend we additionally stage `eval`: the docker_eval_staging payload
    (official image candidates + the official eval_script that embeds the hidden
    test_patch + the parser name + the eval timeout, mirroring cfg.eval.timeout_s
    so in-session grading gets the same budget as the final harness eval). That
    hidden-bearing payload lives ONLY here, next to the row outside the
    workspace — never in the staged workspace.
    """
    test_cmd = None
    try:
        from swebench.harness.constants import MAP_REPO_VERSION_TO_SPECS
        spec = (MAP_REPO_VERSION_TO_SPECS.get(row["repo"], {}) or {}).get(
            str(row.get("version")), {})
        test_cmd = spec.get("test_cmd")
    except Exception:  # noqa: BLE001 - evaluator has its own default
        pass
    extras = {"test_cmd": test_cmd, "staged_at": _now()}
    if grading_backend == GRADING_DOCKER:
        # Hidden test_patch is embedded in eval_script here (outside the
        # workspace).
        extras["eval"] = docker_eval_staging(row, timeout_s=eval_timeout_s)
    return extras


def _render_private_eval(cfg: Config, row: dict, row_path: str,
                         grading_backend: str) -> str:
    """The scripts/private_eval.py body for the chosen grading backend.

    Both backends bake in exactly ONE token, __ROW_PATH__ (the absolute path of
    the out-of-workspace row.json); everything else either is stdlib-derived in
    the script or — for docker — comes from the row's `_staging.eval` payload
    (image_candidates, the official eval_script, the parser), staged by
    build_workspace via docker_eval_staging(). The two scripts share the exact
    three-line aggregate output contract.

    "local" (v1 default): grade on a local temp copy of the base tree. Fully
    validated + unit-tested.

    "docker" (v2, UNVALIDATED): grade inside the instance's official prebuilt
    SWE-bench image. See PRIVATE_EVAL_SCRIPT_DOCKER + PREP_NOTES.md.
    """
    if grading_backend == GRADING_LOCAL:
        return PRIVATE_EVAL_SCRIPT.replace("__ROW_PATH__", row_path)
    # grading_backend == GRADING_DOCKER (validated upstream by build_workspace).
    # TODO(validate): exercise on a host with docker + the prebuilt image.
    return PRIVATE_EVAL_SCRIPT_DOCKER.replace("__ROW_PATH__", row_path)


def build_workspace(cfg: Config, run_dir: Path, instance_row: dict, arm_kind: str,
                    *, repo_src: str | None = None, kit_src: Path | None = None,
                    build_venv: bool = True,
                    prebuild_env: bool | None = None,
                    grading_backend: str | None = None,
                    ensure_image: bool | None = None,
                    workspaces_dir: Path | None = None) -> Path:
    """Build (or rebuild from scratch) the workspace for one instance.

    Keyword knobs exist for hermetic tests only: `repo_src` (local fixture repo
    instead of GitHub), `kit_src`, `build_venv=False` (skip the env build),
    `ensure_image=False` (skip the docker image inspect/pull),
    `workspaces_dir` (tmp dir instead of fvk_experiments/workspaces/).

    `prebuild_env` (45-instance multi-repo run; see PREP_NOTES.md): per-instance
    OVERRIDE of whether to pre-build a venv. When None (default) the decision is
    the protocol-aware venv_prestaged(cfg, iid): v1 => always True (astropy10 and
    every existing caller UNCHANGED), v2 => only the 6 hard compiled-dependency
    instances (HARD_VENV_INSTANCES), the other 39 staged repo-only so the AGENT
    self-builds its env in Phase 0. `build_venv=False` still hard-skips the build
    regardless (hermetic tests) — it ANDs with the above.

    `grading_backend` selects scripts/private_eval.py's grading path: "local"
    (v1 — grade on a local temp copy; fully tested) or "docker" (v2 — grade
    inside the instance's official prebuilt image). When None (default) it
    follows the PROTOCOL: docker for phased arms under a v2+ template, local
    otherwise — so run_instance needs no extra wiring and v1 configs are
    byte-for-byte unchanged.

    `ensure_image`: pre-pull/verify the official eval image at build time
    (default: exactly when the docker backend is in play), so the session never
    needs registry access mid-protocol.
    """
    if arm_kind not in ALL_KINDS:
        raise ValueError(f"unknown arm_kind {arm_kind!r} (expected one of {ALL_KINDS})")
    row = instance_row
    iid = row["instance_id"]
    phased = arm_kind in PHASED_KINDS
    if grading_backend is None:
        grading_backend = (GRADING_DOCKER if phased and protocol_version(cfg) >= 2
                           else GRADING_LOCAL)
    if grading_backend not in (GRADING_LOCAL, GRADING_DOCKER):
        raise ValueError(
            f"unknown grading_backend {grading_backend!r} "
            f"(expected {GRADING_LOCAL!r} or {GRADING_DOCKER!r})")
    docker_grading = phased and grading_backend == GRADING_DOCKER
    if ensure_image is None:
        ensure_image = docker_grading
    f2p = listify(row.get("FAIL_TO_PASS"))
    p2p = listify(row.get("PASS_TO_PASS"))
    # Effective venv decision: hermetic build_venv=False always wins (skip), else
    # the per-instance override, else the protocol-aware default venv_prestaged()
    # (v1: build for everyone -> astropy10 + tests unchanged; v2: hard ids only).
    want_venv = venv_prestaged(cfg, iid) if prebuild_env is None else prebuild_env
    do_build_venv = build_venv and want_venv

    root = workspaces_dir or workspaces_root()
    ws = root / run_dir.name / iid
    if ws.exists():
        shutil.rmtree(ws)  # deterministic rebuild — never trust a stale tree
    ws.mkdir(parents=True)

    # --- benchmark/ (public), scratch dirs --------------------------------
    bench = ws / "benchmark"
    bench.mkdir()
    (bench / "public_instance.json").write_text(
        json.dumps(_public_instance(cfg, row, len(f2p), len(p2p)), indent=2) + "\n")
    (bench / "PROMPT.md").write_text(_prompt_md(row, len(f2p), len(p2p)))
    (ws / "patches").mkdir()
    (ws / "reports").mkdir()
    if arm_kind == ARM_FVK:
        (ws / "fvk").mkdir()
    elif arm_kind == ARM_REVIEW:
        (ws / "review").mkdir()

    # --- private evaluator (phased arms only — baseline gets NO oracle) ---
    # The answer key (full row) is written OUTSIDE the workspace, under the run
    # dir; the evaluator stays in the workspace but reaches the row only via an
    # absolute path baked into it. The agent has no in-workspace row file.
    row_path = None
    if phased:
        priv_out = run_dir / "private" / iid
        priv_out.mkdir(parents=True, exist_ok=True)
        full = {**row,
                "FAIL_TO_PASS": f2p, "PASS_TO_PASS": p2p,
                "_staging": _staging_extras(row, grading_backend,
                                            eval_timeout_s=cfg.eval.timeout_s)}
        row_path = (priv_out / "row.json").resolve()
        row_path.write_text(json.dumps(full, indent=2) + "\n")
        # private_eval/ in the workspace now holds ONLY the local eval log the
        # script appends to (no row); keep the dir so logging never fails.
        (ws / "private_eval").mkdir()
        scripts = ws / "scripts"
        scripts.mkdir()
        ev = scripts / "private_eval.py"
        ev.write_text(_render_private_eval(cfg, row, str(row_path), grading_backend))
        ev.chmod(0o755)

    # --- kit (fvk-replicate only) ------------------------------------------
    kit_info = {"kit_commit": None, "kit_dirty": None}
    if arm_kind == ARM_FVK:
        kit_info = _copy_kit(kit_src or kit_dir(), ws / "formal-verification-kit")

    # --- official eval image (docker grading only): present BEFORE the session
    # starts, so scripts/private_eval.py never needs registry access mid-run.
    instance_image = None
    if docker_grading and ensure_image:
        build_dir = ws / ".build"
        build_dir.mkdir(exist_ok=True)
        instance_image = ensure_instance_image(row, log=build_dir / "image.log")

    # --- repo: truncated checkout, venv, then the synthetic base commit ----
    repo_dir = ws / "repo"
    cache = ensure_bare_cache(row["repo"], row["base_commit"], repo_src=repo_src,
                              root=root)
    _checkout_truncated(cache, row["base_commit"], repo_dir)
    venv_info = {"python": None, "spec_source": None}
    if do_build_venv:
        build_dir = ws / ".build"
        build_dir.mkdir(exist_ok=True)
        venv_info = build_repo_venv(ws, repo_dir, row, log=build_dir / "venv.log")
    local_head = _commit_base(repo_dir)

    # --- manifest -----------------------------------------------------------
    staged = {}
    for sub in ("benchmark", "private_eval", "scripts"):
        d = ws / sub
        if d.is_dir():
            for f in sorted(d.rglob("*")):
                if f.is_file():
                    staged[str(f.relative_to(ws))] = _sha256_file(f)
    manifest = {
        "instance_id": iid,
        "arm_kind": arm_kind,
        "built_at": _now(),
        "base_commit": row["base_commit"],
        "repo_source": repo_src or f"https://github.com/{row['repo']}.git",
        "repo_local_head": local_head,
        "venv": venv_info,
        # v2 multi-repo provenance: whether we pre-built the env (vs agent
        # self-build in Phase 0), which grading backend the evaluator uses, the
        # protocol version it was derived from, and (docker backend) the local
        # name of the official eval image that was verified/pulled at build time.
        "prebuilt_env": do_build_venv,
        "grading_backend": grading_backend,
        "protocol_version": protocol_version(cfg),
        "instance_image": instance_image,
        **kit_info,
        "staged": staged,
        # Provenance for the out-of-workspace answer key (NOT inside ws).
        "row_path": str(row_path) if row_path else None,
        "row_sha256": _sha256_file(row_path) if row_path else None,
    }
    (ws / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return ws
