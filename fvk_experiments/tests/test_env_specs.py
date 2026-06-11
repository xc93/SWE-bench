"""Tests for the env-recipe adapter (fvk_bench/env_specs.py).

Pure-logic reads of swebench.harness.constants — NO installs, NO docker, NO
network. Covers the import-name map and spec_for() for the Grigore-set repos.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.env_specs import (
    DEFAULT_TEST_CMD,
    REPO_IMPORT_NAME,
    EnvSpec,
    import_name_for,
    spec_for,
)


# ----------------------------------------------------------- import names ----

@pytest.mark.parametrize("repo,want", [
    ("astropy/astropy", "astropy"),
    ("django/django", "django"),
    ("sphinx-doc/sphinx", "sphinx"),            # distribution Sphinx -> import sphinx
    ("sympy/sympy", "sympy"),
    ("pytest-dev/pytest", "pytest"),
    ("pydata/xarray", "xarray"),                # org != import
    ("pylint-dev/pylint", "pylint"),
    ("scikit-learn/scikit-learn", "sklearn"),   # the one the trailing-segment heuristic gets wrong
])
def test_import_name_for_known_repos(repo, want):
    assert import_name_for(repo) == want


def test_import_name_falls_back_to_trailing_segment():
    # Unknown repo: best-effort guess from the path tail (never raises).
    assert import_name_for("someorg/coolpkg") == "coolpkg"
    assert import_name_for("noslash") == "noslash"


def test_all_eight_grigore_repos_are_explicitly_mapped():
    for repo in ("astropy/astropy", "django/django", "sphinx-doc/sphinx",
                 "sympy/sympy", "pytest-dev/pytest", "pydata/xarray",
                 "pylint-dev/pylint", "scikit-learn/scikit-learn"):
        assert repo in REPO_IMPORT_NAME, repo


# --------------------------------------------------------------- spec_for ----

# (repo, version, expected python, expected import). Versions are the ones the
# pinned 45 actually use (verified against the cached dataset).
SAMPLES = [
    ("django/django", "3.2", "3.6", "django"),
    ("django/django", "5.0", "3.11", "django"),
    ("sympy/sympy", "1.1", "3.9", "sympy"),
    ("sphinx-doc/sphinx", "4.2", "3.9", "sphinx"),
    ("astropy/astropy", "5.0", "3.9", "astropy"),
    ("scikit-learn/scikit-learn", "1.3", "3.9", "sklearn"),
    ("pydata/xarray", "0.12", "3.10", "xarray"),
    ("pylint-dev/pylint", "2.9", "3.9", "pylint"),
    ("pytest-dev/pytest", "7.2", "3.9", "pytest"),
]


@pytest.mark.parametrize("repo,version,py,imp", SAMPLES)
def test_spec_for_returns_sane_values(repo, version, py, imp):
    s = spec_for(repo, version)
    assert isinstance(s, EnvSpec)
    assert s.found is True
    assert s.python_version == py
    assert s.repo_import_name == imp
    # test_cmd is a non-empty real command from the constants
    assert isinstance(s.test_cmd, str) and s.test_cmd
    # install_cmds always ends with an install step; every step is a str
    assert s.install_cmds and all(isinstance(c, str) for c in s.install_cmds)
    assert any("install" in c for c in s.install_cmds)


def test_django_install_uses_editable_or_setup():
    # django specs use either `python -m pip install -e .` or setup.py install.
    s = spec_for("django/django", "3.2")
    assert s.install_cmds[-1] in (
        "python -m pip install -e .", "python setup.py install")
    # django test_cmd is the runtests.py driver, not bare pytest
    assert "runtests.py" in s.test_cmd


def test_sklearn_install_carries_no_build_isolation_flag():
    # sklearn needs the cython source build flags from the spec, surfaced verbatim.
    s = spec_for("scikit-learn/scikit-learn", "1.3")
    assert any("--no-build-isolation" in c for c in s.install_cmds)


def test_install_cmds_order_is_pre_install_then_pips_then_install():
    # astropy 5.0 has a pyproject sed pre_install, a big pip_packages list, then
    # the editable install — assert that ordering.
    s = spec_for("astropy/astropy", "5.0")
    cmds = s.install_cmds
    assert "sed" in cmds[0]                       # pre_install first
    assert cmds[-1].startswith("python -m pip install -e .")  # install last
    # the pip_packages install sits between them
    pip_idx = [i for i, c in enumerate(cmds) if c.startswith("python -m pip install ")
               and "-e ." not in c]
    assert pip_idx and 0 < pip_idx[0] < len(cmds) - 1


def test_spec_for_unknown_pair_is_generic_not_found():
    s = spec_for("django/django", "99.99")
    assert s.found is False
    assert s.test_cmd == DEFAULT_TEST_CMD
    # generic editable+test install fallback
    assert s.install_cmds[-1] == "python -m pip install -e .[test]"
    # import name still resolved (mapping is independent of the spec)
    assert s.repo_import_name == "django"


def test_spec_for_accepts_non_string_version():
    # versions sometimes arrive as floats from a dataframe; str() is applied.
    s = spec_for("sympy/sympy", 1.1)  # noqa: only checking str-coercion path
    # 1.1 -> "1.1" which exists; if float repr differed it would be not-found,
    # so just assert it does not crash and returns an EnvSpec.
    assert isinstance(s, EnvSpec)
    assert s.repo_import_name == "sympy"
