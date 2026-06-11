"""Tests for the 45-instance (Grigore-set) batch configs + the v2 env policy.

Covers:
  - all 15 batchN__claude-code-opus46__<arm> configs load, label correctly, and
    point at the v2 templates;
  - the 5 batches partition the 45 ids exactly (union == 45 unique, none
    missing/extra), with the 6 hard instances all present;
  - the per-instance prebuild policy (should_prebuild_env) and the grading
    backend selector in build_workspace, exercised hermetically (a local fixture
    repo, NO venv build, NO docker, NO session).

The generator's own self-check (scripts/build_batch45_configs.py::_check) is the
source of truth for the split; this test re-derives it from the WRITTEN configs
so a stale/hand-edited config file is caught.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench import agentic
from fvk_bench.agentic import (GRADING_DOCKER, GRADING_LOCAL, HARD_PREBUILD_IDS,
                               build_workspace, should_prebuild_env)
from fvk_bench.config import EXP_ROOT, load_config

CONFIGS = EXP_ROOT / "configs"
ARMS = ("baseline", "review-control", "fvk-replicate")
BATCHES = range(1, 6)

# The 45 ids, independently restated here (NOT imported from the generator) so
# the test is a real cross-check of what the configs contain.
ALL45 = {
    "astropy__astropy-13398", "astropy__astropy-13579", "astropy__astropy-14369",
    "django__django-10554", "django__django-11138", "django__django-11400",
    "django__django-11885", "django__django-12325", "django__django-12708",
    "django__django-13128", "django__django-13212", "django__django-13344",
    "django__django-13449", "django__django-13837", "django__django-14007",
    "django__django-14011", "django__django-14631", "django__django-15128",
    "django__django-15268", "django__django-15503", "django__django-15629",
    "django__django-15957", "django__django-16263", "django__django-16560",
    "django__django-16631",
    "pydata__xarray-3993", "pydata__xarray-6992",
    "pylint-dev__pylint-4551", "pylint-dev__pylint-8898",
    "pytest-dev__pytest-10356", "pytest-dev__pytest-5787", "pytest-dev__pytest-6197",
    "scikit-learn__scikit-learn-25102",
    "sphinx-doc__sphinx-11510", "sphinx-doc__sphinx-7590", "sphinx-doc__sphinx-8548",
    "sphinx-doc__sphinx-9229", "sphinx-doc__sphinx-9461",
    "sympy__sympy-12489", "sympy__sympy-13852", "sympy__sympy-13878",
    "sympy__sympy-14248", "sympy__sympy-16597", "sympy__sympy-17630",
    "sympy__sympy-18199",
}


def _cfg_path(batch_n: int, arm: str) -> Path:
    return CONFIGS / f"batch{batch_n}__claude-code-opus46__{arm}.yaml"


# ------------------------------------------------------------- config load ---

def test_all_15_configs_exist_and_load():
    for n in BATCHES:
        for arm in ARMS:
            p = _cfg_path(n, arm)
            assert p.exists(), f"missing config {p.name}"
            cfg = load_config(p)
            assert cfg.model.provider == "claude-code"
            assert cfg.model.name == "claude-code-opus-4.6"
            assert cfg.model.cc_model == "claude-opus-4-6"
            assert cfg.model.max_turns == 200
            assert cfg.model.session_timeout_s == 5400
            assert cfg.inference.max_workers == 1
            assert cfg.arm_tag() == arm
            assert cfg.model_label() == f"claude-code-opus-4.6__{arm}"


def test_configs_point_at_v2_templates():
    for n in BATCHES:
        for arm in ARMS:
            cfg = load_config(_cfg_path(n, arm))
            assert cfg.prompt.system_prompt == f"prompts/agentic/{arm}-v2.md"
            assert cfg.system_prompt_path().exists()
            # frontmatter version is 2 and arm tag resolves to the bare arm
            assert cfg.prompt_version() == "v2"


def test_each_batch_has_nine_ids_and_arms_agree():
    for n in BATCHES:
        per_arm = {arm: tuple(load_config(_cfg_path(n, arm)).dataset.instance_ids)
                   for arm in ARMS}
        for arm in ARMS:
            assert len(per_arm[arm]) == 9, (n, arm, len(per_arm[arm]))
            assert len(set(per_arm[arm])) == 9, f"dupes in batch{n} {arm}"
        # the three arms of a batch run the SAME ids (pair-comparable)
        assert per_arm["baseline"] == per_arm["review-control"] == per_arm["fvk-replicate"], n


def test_batches_partition_the_45_exactly():
    union: set[str] = set()
    for n in BATCHES:
        ids = set(load_config(_cfg_path(n, "baseline")).dataset.instance_ids)
        # batches are disjoint
        assert union.isdisjoint(ids), f"batch{n} overlaps a previous batch: {union & ids}"
        union |= ids
    assert union == ALL45, ("union != the 45",
                            "missing:", ALL45 - union, "extra:", union - ALL45)
    assert len(union) == 45


def test_all_six_hard_instances_are_present_somewhere():
    union: set[str] = set()
    for n in BATCHES:
        union |= set(load_config(_cfg_path(n, "baseline")).dataset.instance_ids)
    assert HARD_PREBUILD_IDS <= union
    assert len(HARD_PREBUILD_IDS) == 6


# ------------------------------------------------------------- env policy ----

def test_should_prebuild_env_defaults_to_hard_set():
    assert should_prebuild_env("astropy__astropy-13398") is True
    assert should_prebuild_env("scikit-learn__scikit-learn-25102") is True
    assert should_prebuild_env("django__django-10554") is False
    assert should_prebuild_env("sympy__sympy-17630") is False


def test_should_prebuild_env_override_wins():
    assert should_prebuild_env("django__django-10554", override=True) is True
    assert should_prebuild_env("astropy__astropy-13398", override=False) is False


def test_hard_set_is_exactly_the_six_compiled_dep_instances():
    assert HARD_PREBUILD_IDS == {
        "astropy__astropy-13398", "astropy__astropy-13579", "astropy__astropy-14369",
        "pydata__xarray-3993", "pydata__xarray-6992",
        "scikit-learn__scikit-learn-25102",
    }


def test_protocol_version_from_template_frontmatter(tmp_path):
    # v1 template => protocol 1; v2 template => protocol 2.
    v1 = _cc_cfg_with_template(tmp_path, "fvk-replicate",
                               "prompts/agentic/fvk-replicate.md")
    v2 = _cc_cfg_with_template(tmp_path, "fvk-replicate",
                               "prompts/agentic/fvk-replicate-v2.md")
    assert agentic.protocol_version(v1) == 1
    assert agentic.protocol_version(v2) == 2


def test_venv_prestaged_v1_always_true_v2_only_hard(tmp_path):
    """THE v1-preservation guarantee: under a v1 template venv_prestaged is True
    for every instance (astropy10 unchanged); under v2 it is True only for the 6
    hard compiled-dependency instances."""
    v1 = _cc_cfg_with_template(tmp_path, "fvk-replicate",
                               "prompts/agentic/fvk-replicate.md")
    v2 = _cc_cfg_with_template(tmp_path, "fvk-replicate",
                               "prompts/agentic/fvk-replicate-v2.md")
    for iid in ("astropy__astropy-12907", "django__django-10554",
                "astropy__astropy-13398", "sympy__sympy-17630"):
        assert agentic.venv_prestaged(v1, iid) is True, ("v1", iid)
    # v2: hard ids prestaged, everything else agent-built
    assert agentic.venv_prestaged(v2, "astropy__astropy-13398") is True
    assert agentic.venv_prestaged(v2, "scikit-learn__scikit-learn-25102") is True
    assert agentic.venv_prestaged(v2, "django__django-10554") is False
    assert agentic.venv_prestaged(v2, "sympy__sympy-17630") is False


# ---------------------------------------- build_workspace plumbing (hermetic)

def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture(scope="module")
def mini_repo(tmp_path_factory):
    src = tmp_path_factory.mktemp("origin45") / "tinypkg"
    (src / "tests").mkdir(parents=True)
    (src / "tinypkg.py").write_text("def add(a, b):\n    return a + b\n")
    (src / "tests" / "test_x.py").write_text(
        "from tinypkg import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n")
    _git("init", "-q", cwd=src)
    _git("add", "-A", cwd=src)
    _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", cwd=src)
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=src, check=True,
                          capture_output=True, text=True).stdout.strip()
    return {"path": src, "base": base}


def _row(mini_repo) -> dict:
    return {
        "instance_id": "fixture__tinypkg-1",
        "repo": "fixture/tinypkg",
        "base_commit": mini_repo["base"],
        "version": "0.1",
        "problem_statement": "add must add.",
        "patch": "",
        "test_patch": ("diff --git a/tests/test_x.py b/tests/test_x.py\n"
                       "--- a/tests/test_x.py\n+++ b/tests/test_x.py\n"
                       "@@ -1,4 +1,5 @@\n from tinypkg import add\n \n \n"
                       " def test_add():\n     assert add(1, 2) == 3\n"),
        "FAIL_TO_PASS": json.dumps(["tests/test_x.py::test_add"]),
        "PASS_TO_PASS": json.dumps([]),
        "hints_text": "",
        "created_at": "2026-01-01T00:00:00Z",
        "environment_setup_commit": mini_repo["base"],
    }


def _cc_cfg(tmp_path: Path, tag: str) -> "object":
    template = tmp_path / f"{tag}.md"
    template.write_text(f"---\ntag: {tag}\n---\nDo: {{problem_statement}}\n")
    p = tmp_path / f"cfg-{tag}.yaml"
    p.write_text(
        f"run_name: test-cc-{tag}\n"
        f"tag: {tag}\n"
        f"dataset:\n  instance_ids: [fixture__tinypkg-1]\n"
        f"model:\n  provider: claude-code\n  name: claude-code-opus-4.6\n"
        f"  cc_model: claude-opus-4-6\n"
        f"prompt:\n  system_prompt: {template}\n")
    return load_config(p)


def _cc_cfg_with_template(tmp_path: Path, tag: str, template_rel: str):
    """A claude-code cfg whose system_prompt points at a REAL repo template (so
    prompt_version()/protocol_version() read its actual frontmatter `version:`)."""
    p = tmp_path / f"cfg-real-{tag}-{Path(template_rel).stem}.yaml"
    p.write_text(
        f"run_name: test-cc-real-{Path(template_rel).stem}\n"
        f"tag: {tag}\n"
        f"dataset:\n  instance_ids: [fixture__tinypkg-1]\n"
        f"model:\n  provider: claude-code\n  name: claude-code-opus-4.6\n"
        f"  cc_model: claude-opus-4-6\n"
        f"prompt:\n  style: oracle\n  system_prompt: {template_rel}\n")
    return load_config(p)


def _build(tmp_path, mini_repo, *, prebuild_env, grading_backend):
    cfg = _cc_cfg(tmp_path, "fvk-replicate")
    run_dir = tmp_path / "runs" / "r"
    run_dir.mkdir(parents=True, exist_ok=True)
    return build_workspace(
        cfg, run_dir, _row(mini_repo), "fvk-replicate",
        repo_src=str(mini_repo["path"]), build_venv=False,
        prebuild_env=prebuild_env, grading_backend=grading_backend,
        ensure_image=False,  # hermetic: never inspect/pull docker images
        workspaces_dir=tmp_path / "workspaces")


def test_repo_only_workspace_skips_venv_and_records_policy(tmp_path, mini_repo):
    # prebuild_env=False => no .venv built; manifest records the policy + backend.
    ws = _build(tmp_path, mini_repo, prebuild_env=False, grading_backend=GRADING_LOCAL)
    manifest = json.loads((ws / "manifest.json").read_text())
    assert manifest["prebuilt_env"] is False
    assert manifest["grading_backend"] == GRADING_LOCAL
    assert manifest["venv"]["python"] is None  # not built
    # repo staged, evaluator present (phased arm)
    assert (ws / "repo").is_dir()
    assert (ws / "scripts" / "private_eval.py").is_file()


def test_local_backend_emits_local_evaluator(tmp_path, mini_repo):
    ws = _build(tmp_path, mini_repo, prebuild_env=False, grading_backend=GRADING_LOCAL)
    script = (ws / "scripts" / "private_eval.py").read_text()
    # local evaluator grades on a local temp copy of the tagged base tree; the
    # ROW_PATH token is substituted (no leftover), no docker image logic.
    assert "__ROW_PATH__" not in script
    assert "fvk-base" in script and "image_candidates" not in script
    # three-line output contract present
    assert 'FAIL_TO_PASS %d/%d' in script and "resolved: %s" in script
    # the out-of-workspace row, local backend: no docker eval payload staged
    manifest = json.loads((ws / "manifest.json").read_text())
    assert manifest["grading_backend"] == GRADING_LOCAL
    row = json.loads(Path(manifest["row_path"]).read_text())
    assert "eval" not in (row.get("_staging") or {})


def test_docker_backend_emits_docker_evaluator(tmp_path, mini_repo, monkeypatch):
    # docker_eval_staging needs real swebench specs (image build + parser); stub
    # it so this test stays hermetic (no docker, no spec map). The wiring under
    # test is: build_workspace stages _staging.eval and writes the docker script.
    stub_payload = {
        "mode": "docker-image",
        "image_candidates": ["swebench/sweb.eval.x86_64.fixture_1776_tinypkg-1:latest",
                             "sweb.eval.x86_64.fixture__tinypkg-1:latest"],
        "eval_script": "#!/bin/bash\necho stub eval script\n",
        "parser": "pytest_v2",
        "timeout_s": 1800,
    }
    monkeypatch.setattr(agentic, "docker_eval_staging",
                        lambda row, timeout_s=1800: dict(stub_payload))
    ws = _build(tmp_path, mini_repo, prebuild_env=False, grading_backend=GRADING_DOCKER)
    script = (ws / "scripts" / "private_eval.py").read_text()
    # canonical docker evaluator: image logic present, no local-copy logic, the
    # ROW_PATH token filled, identical 3-line contract.
    assert "__ROW_PATH__" not in script
    assert "image_candidates" in script and "fvk-base" not in script
    assert 'FAIL_TO_PASS %d/%d' in script and "resolved: %s" in script
    # the docker eval payload (hidden eval_script + image names) is staged with
    # the OUT-OF-WORKSPACE row, never inside the workspace.
    manifest = json.loads((ws / "manifest.json").read_text())
    assert manifest["grading_backend"] == GRADING_DOCKER
    row = json.loads(Path(manifest["row_path"]).read_text())
    ev = row["_staging"]["eval"]
    assert ev["parser"] == "pytest_v2" and ev["image_candidates"]
    # and the hidden eval payload is NOT anywhere under the workspace tree
    for f in ws.rglob("*"):
        if f.is_file():
            assert "stub eval script" not in f.read_text(errors="replace"), f


def test_instance_image_candidates_mangling_is_official():
    # mirrors swebench TestSpec.instance_image_key: namespaced "__"->"_1776_"
    # first, unnamespaced second.
    cands = agentic.instance_image_candidates(
        {"instance_id": "astropy__astropy-13398"}, arch="x86_64")
    assert cands == [
        "swebench/sweb.eval.x86_64.astropy_1776_astropy-13398:latest",
        "sweb.eval.x86_64.astropy__astropy-13398:latest",
    ]


def test_docker_eval_staging_rejects_unsupported_repo():
    # repos without a ported pytest parser cannot be docker-graded by the
    # in-session evaluator; staging must raise loudly rather than mis-grade.
    with pytest.raises(ValueError, match="docker grading unsupported"):
        agentic.docker_eval_staging({"instance_id": "fixture__x-1",
                                     "repo": "fixture/tinypkg", "version": "0.1"})


def test_build_workspace_rejects_unknown_grading_backend(tmp_path, mini_repo):
    with pytest.raises(ValueError, match="grading_backend"):
        _build(tmp_path, mini_repo, prebuild_env=False, grading_backend="nope")
