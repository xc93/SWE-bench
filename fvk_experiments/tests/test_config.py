import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fvk_bench.config import load_config

PROMPT = textwrap.dedent("""\
    ---
    version: 1
    source: https://github.com/grosu/formal-verification-kit
    ---
    # FVK methodology

    Formalize, then verify.
    """)


def _write_cfg(tmp_path: Path, variant: str, fvk_prompt: str | None) -> Path:
    prompt_line = f"  fvk_prompt: {fvk_prompt}" if fvk_prompt else ""
    cfg = textwrap.dedent(f"""\
        run_name: test-run
        variant: {variant}
        dataset:
          instance_ids: [astropy__astropy-12907]
        prompt:
          style: oracle
        {prompt_line}
        """)
    p = tmp_path / "cfg.yaml"
    p.write_text(cfg)
    return p


def test_baseline_config_loads(tmp_path):
    cfg = load_config(_write_cfg(tmp_path, "baseline", None))
    assert cfg.variant_tag() == "baseline"
    assert cfg.model_label() == "deepseek-v4-flash-think__baseline"
    assert cfg.fvk_prompt_body() is None
    assert cfg.model.thinking is True


def test_fvk_config_requires_prompt(tmp_path):
    with pytest.raises(ValueError, match="requires prompt.fvk_prompt"):
        load_config(_write_cfg(tmp_path, "fvk", None))


def test_fvk_prompt_version_and_body(tmp_path):
    prompt_file = tmp_path / "v1.md"
    prompt_file.write_text(PROMPT)
    p = _write_cfg(tmp_path, "fvk", str(prompt_file))
    cfg = load_config(p)
    assert cfg.fvk_prompt_version() == "v1"
    assert cfg.variant_tag() == "fvk-v1"
    assert cfg.fvk_prompt_body().startswith("# FVK methodology")
    assert "version: 1" not in cfg.fvk_prompt_body()
    assert cfg.fvk_prompt_sha()


def test_frontmatter_tag_overrides_variant_tag(tmp_path):
    prompt_file = tmp_path / "v5.md"
    prompt_file.write_text("---\nversion: 5\ntag: review-v5\n---\n# Self-review\n")
    cfg = load_config(_write_cfg(tmp_path, "fvk", str(prompt_file)))
    assert cfg.fvk_prompt_version() == "v5"
    assert cfg.variant_tag() == "review-v5"
    assert cfg.model_label() == "deepseek-v4-flash-think__review-v5"


def test_unknown_key_rejected(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text("run_name: x\nvariant: baseline\n"
                 "dataset: {instance_ids: [a], typo_key: 1}\n")
    with pytest.raises(ValueError, match="typo_key"):
        load_config(p)


def test_missing_instances_rejected(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text("run_name: x\nvariant: baseline\n")
    with pytest.raises(ValueError, match="instance_ids"):
        load_config(p)
