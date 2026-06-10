import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.report import write_pair_report


def _run_dir(tmp_path, run_id, model_label, resolved_by_iid, legacy_keys=False):
    d = tmp_path / run_id
    d.mkdir()
    arm_key = "variant_tag" if legacy_keys else "arm"
    (d / "summary.json").write_text(json.dumps({
        "run_id": run_id, "model_label": model_label,
        arm_key: model_label.split("__")[1],
        "model": model_label.split("-think")[0], "n_instances": len(resolved_by_iid),
        "solved_count": sum(resolved_by_iid.values()),
        "prompt_version": "v1", "prompt_sha256": "ab" * 32,
        "instances": [{"instance_id": k, "resolved": v} for k, v in resolved_by_iid.items()],
    }))
    return d


def test_same_model_pair_has_no_banner(tmp_path):
    b = _run_dir(tmp_path, "b", "deepseek-v4-pro-think__baseline", {"i1": False, "i2": True})
    t = _run_dir(tmp_path, "t", "deepseek-v4-pro-think__fvk-v1", {"i1": True, "i2": True})
    out = write_pair_report(b, t, tmp_path / "pair.md")
    md = out.read_text()
    assert "Cross-model" not in md
    assert "solved_count_baseline = 1" in md and "solved_count_treatment = 2" in md
    assert "only by fvk-v1" in md


def test_cross_model_pair_gets_banner(tmp_path):
    b = _run_dir(tmp_path, "b", "deepseek-v4-flash-think__baseline", {"i1": False})
    t = _run_dir(tmp_path, "t", "deepseek-v4-pro-think__baseline", {"i1": True})
    md = write_pair_report(b, t, tmp_path / "pair.md").read_text()
    assert "Cross-model comparison" in md
    assert "deepseek-v4-flash-think" in md and "deepseek-v4-pro-think" in md


def test_legacy_summary_keys_still_render(tmp_path):
    b = _run_dir(tmp_path, "b", "deepseek-v4-pro-think__baseline", {"i1": False},
                 legacy_keys=True)
    t = _run_dir(tmp_path, "t", "deepseek-v4-pro-think__fvk-v1", {"i1": True},
                 legacy_keys=True)
    md = write_pair_report(b, t, tmp_path / "pair.md").read_text()
    assert "baseline vs fvk-v1" in md
