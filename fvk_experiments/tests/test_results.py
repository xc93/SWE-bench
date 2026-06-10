import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.report import write_results_index


def _summary(run_id, variant_tag, solved, sha=None):
    return {
        "run_id": run_id, "variant_tag": variant_tag, "model": "deepseek-v4-flash",
        "thinking": True, "solved_count": solved, "n_instances": 10,
        "fvk_prompt_version": "v1" if sha else None, "fvk_prompt_sha256": sha,
        "meta": {"started_at": "2026-06-10T09:00:00Z"},
    }


def test_results_index(tmp_path):
    b, f = "astropy10__base__1", "astropy10__fvk__1"
    for rid, s in ((b, _summary(b, "baseline", 3)),
                   (f, _summary(f, "fvk-v1", 4, sha="abc123def4567890"))):
        d = tmp_path / "runs" / rid
        d.mkdir(parents=True)
        (d / "summary.json").write_text(json.dumps(s))
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / f"pair__{b}__VS__{f}.md").write_text("x")
    g = tmp_path / "runs" / "gold-sanity__astropy10__1" / "eval"
    g.mkdir(parents=True)
    (g / "gold.gold-sanity__astropy10__1.json").write_text(
        json.dumps({"resolved_instances": 10, "total_instances": 10}))

    out = write_results_index(tmp_path)
    md = out.read_text()
    assert "baseline: 3/10 vs fvk-v1: 4/10 (Δ +1)" in md
    assert "**3 / 10**" in md and "**4 / 10**" in md
    assert "`v1` (sha `abc123def456`)" in md
    assert "gold patches resolved **10/10**" in md
