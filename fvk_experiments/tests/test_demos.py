import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.demos import build_content, format_demos, load_registry, validate_registry


def _registry(tmp_path, demos, content_file="d.content.json"):
    import yaml
    p = tmp_path / "d.yaml"
    p.write_text(yaml.safe_dump({"version": 1, "content_file": content_file,
                                 "demos": demos}))
    return p


GOOD = {
    "t1": [{"id": "d1", "rationale": "r"}, {"id": "d2", "rationale": "r"},
           {"id": "d3", "rationale": "r"}],
    "t2": [{"id": "d2", "rationale": "r"}, {"id": "d3", "rationale": "r"},
           {"id": "d4", "rationale": "r"}],
}


def test_registry_validates(tmp_path):
    load_registry(_registry(tmp_path, GOOD))


def test_registry_rejects_test_set_leakage(tmp_path):
    bad = {"t1": GOOD["t1"],
           "t2": [{"id": "t1", "rationale": "r"}, {"id": "d3", "rationale": "r"},
                  {"id": "d4", "rationale": "r"}]}
    with pytest.raises(ValueError, match="test set"):
        load_registry(_registry(tmp_path, bad))


def test_registry_rejects_wrong_count_and_dupes(tmp_path):
    with pytest.raises(ValueError, match="exactly 3"):
        load_registry(_registry(tmp_path, {"t1": GOOD["t1"][:2]}))
    dupe = {"t1": [{"id": "d1", "rationale": "r"}] * 3}
    with pytest.raises(ValueError, match="distinct"):
        load_registry(_registry(tmp_path, dupe))


def test_build_content_from_source_and_staleness(tmp_path):
    reg = _registry(tmp_path, GOOD)
    src = tmp_path / "pool.json"
    src.write_text(json.dumps({f"d{i}": {"problem_statement": f"issue {i}",
                                         "patch": f"--- a/f{i}\n+++ b/f{i}\n"}
                               for i in range(1, 5)}))
    out = build_content(reg, source_json=src)
    data = json.loads(out.read_text())
    assert set(data["demos"]) == {"t1", "t2"}
    assert data["demos"]["t1"][0]["problem_statement"] == "issue 1"
    assert data["registry_sha256"]

    text = format_demos(data["demos"]["t1"])
    assert "## Example 1 — d1" in text and "### Patch that fixed it" in text

    # missing demo content -> hard error (dataset fallback disabled for hermeticity)
    src.write_text(json.dumps({"d1": {"problem_statement": "x", "patch": "y"}}))
    bad_reg = _registry(tmp_path, GOOD, content_file="d2.content.json")
    with pytest.raises(ValueError, match="not found"):
        build_content(bad_reg, source_json=src, dataset_fallback=False)
