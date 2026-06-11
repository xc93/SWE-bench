"""Env-recipe adapter over SWE-bench's per-repo/version install specs.

The agentic workspaces (fvk_bench.agentic) and the per-instance prompt
instantiator (fvk_bench.agentic_prompts) need a few per-instance facts that the
docker images encode: which Python the row was built with, how the repo is
installed, how its tests are run, and what name to `import` to sanity-check the
environment. SWE-bench stores all of that (except the import name) in
`swebench.harness.constants.MAP_REPO_VERSION_TO_SPECS`, a {repo: {version: spec}}
dict whose spec values carry keys like ``python``, ``install``, ``pip_packages``,
``pre_install``, ``packages``, ``test_cmd``.

This module is the single read-only adapter the rest of fvk_bench uses, so the
constants layout is referenced in exactly one place. It performs NO installs,
NO docker, NO network — it only reads the constant dict and a small static
repo->import-name table. The 45-instance multi-repo run (see PREP_NOTES.md) uses
it to: (1) drive the agent self-build env-verify line per repo, and (2) let the
private evaluator pick the right ``test_cmd`` for non-astropy repos.

The import name is NOT in the SWE-bench constants (the images never need to
`import` the package by hand), so it is maintained here as REPO_IMPORT_NAME. It
covers the eight repos of the Grigore-set plus a few neighbours; unknown repos
fall back to the last path segment of ``repo`` (e.g. "foo/bar" -> "bar"), which
is correct for the common case and only wrong for the handful of repos whose
distribution name differs from their import name (sphinx, scikit-learn, xarray,
pylint, pytest — all explicitly mapped below).
"""

from __future__ import annotations

from dataclasses import dataclass

# Repo (org/name) -> top-level import package name. Only repos whose import name
# differs from the trailing path segment STRICTLY need an entry, but the eight
# Grigore-set repos are all listed for clarity and test-coverage. Keep this in
# sync with the prompt instantiator's needs; new repos: add a row.
REPO_IMPORT_NAME: dict[str, str] = {
    "astropy/astropy": "astropy",
    "django/django": "django",
    "sphinx-doc/sphinx": "sphinx",            # distribution "Sphinx" -> import "sphinx"
    "sympy/sympy": "sympy",
    "pytest-dev/pytest": "pytest",            # distribution "pytest", package "_pytest"/"pytest"
    "pydata/xarray": "xarray",                # org != import name
    "pylint-dev/pylint": "pylint",
    "scikit-learn/scikit-learn": "sklearn",   # distribution "scikit-learn" -> import "sklearn"
    # neighbours that occasionally show up in this benchmark family:
    "matplotlib/matplotlib": "matplotlib",
    "mwaskom/seaborn": "seaborn",
    "psf/requests": "requests",
    "pallets/flask": "flask",
    "scikit-learn/scikit-image": "skimage",
}

# Mirrors swebench's own fallback when no row test_cmd is known (private_eval.py
# uses the same string). Kept here so callers never hard-code it twice.
DEFAULT_TEST_CMD = "pytest --no-header -rA --tb=no -p no:cacheprovider"


@dataclass(frozen=True)
class EnvSpec:
    """The per-instance env facts the agentic layer consumes.

    `install_cmds` is the ordered list of shell commands that reproduce what the
    docker image installs, as PLAIN strings (no docker/conda assumptions): the
    spec's ``pre_install`` steps, then a ``pip install`` of ``pip_packages`` (if
    any), then the spec's ``install`` line. apt-get steps are surfaced verbatim
    (the agent self-build path decides whether it can run them) — callers that
    cannot become root should skip lines containing 'apt-get', exactly as the
    existing venv builder does. ``found`` is False when the (repo, version) pair
    is not in the constants, in which case the fields carry generic fallbacks.
    """

    repo: str
    version: str
    python_version: str
    install_cmds: tuple[str, ...]
    test_cmd: str
    repo_import_name: str
    found: bool
    # The raw spec dict (empty when not found), for callers that need extras
    # (e.g. ``no_use_env``, ``eval_commands``) without re-reading the constants.
    raw: dict


def import_name_for(repo: str) -> str:
    """Top-level import package for `repo` (org/name).

    Mapped repos win; otherwise fall back to the trailing path segment. Never
    raises — an unknown repo yields a best-effort guess so the env-verify line
    is still emittable.
    """
    if repo in REPO_IMPORT_NAME:
        return REPO_IMPORT_NAME[repo]
    return repo.split("/")[-1]


def _spec_dict(repo: str, version) -> dict:
    """Raw spec dict for (repo, version) from the SWE-bench constants, or {}.

    Lazy import so this module imports cheaply and tests that only touch the
    import-name map do not pull in the (large) constants module.
    """
    from swebench.harness.constants import MAP_REPO_VERSION_TO_SPECS

    by_version = MAP_REPO_VERSION_TO_SPECS.get(repo, {}) or {}
    return by_version.get(str(version), {}) or {}


def _install_cmds(spec: dict) -> tuple[str, ...]:
    """Ordered plain-shell install steps derived from a spec dict.

    Order mirrors fvk_bench.agentic.build_repo_venv: pre_install, then a single
    ``pip install`` of all pip_packages, then the spec's ``install`` line (or a
    generic editable+test fallback when the spec omits one). 'python ...' lines
    are left as-is; the caller substitutes its own interpreter, exactly as the
    venv builder already does.
    """
    cmds: list[str] = []
    cmds.extend(spec.get("pre_install", []) or [])
    pips = spec.get("pip_packages", []) or []
    if pips:
        cmds.append("python -m pip install " + " ".join(pips))
    install = spec.get("install") or "python -m pip install -e .[test]"
    cmds.append(install)
    return tuple(cmds)


def spec_for(repo: str, version) -> EnvSpec:
    """Env recipe for one SWE-bench (repo, version).

    Reads MAP_REPO_VERSION_TO_SPECS. When the pair is present, returns the row's
    python, derived install command list, test_cmd, and import name. When it is
    ABSENT (unexpected for the pinned 45, but handled), returns a generic spec
    (python = the host's, generic editable install, default pytest) with
    ``found=False`` so callers can warn instead of silently mis-building.

    Pure read: no installs, no docker, no network.
    """
    spec = _spec_dict(repo, version)
    found = bool(spec)
    import sys

    python_version = spec.get(
        "python", f"{sys.version_info[0]}.{sys.version_info[1]}")
    test_cmd = spec.get("test_cmd") or DEFAULT_TEST_CMD
    return EnvSpec(
        repo=repo,
        version=str(version),
        python_version=str(python_version),
        install_cmds=_install_cmds(spec),
        test_cmd=test_cmd,
        repo_import_name=import_name_for(repo),
        found=found,
        raw=spec,
    )
