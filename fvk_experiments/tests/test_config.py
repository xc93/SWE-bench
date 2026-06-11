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


def _write_cfg(tmp_path: Path, body: str = "") -> Path:
    cfg = "run_name: test-run\ndataset:\n  instance_ids: [astropy__astropy-12907]\n" + body
    p = tmp_path / "cfg.yaml"
    p.write_text(cfg)
    return p


def test_baseline_is_derived_from_absence_of_injection(tmp_path):
    cfg = load_config(_write_cfg(tmp_path))
    assert cfg.is_baseline()
    assert cfg.arm_tag() == "baseline"
    assert cfg.model_label() == "deepseek-v4-flash-think__baseline"
    assert cfg.system_prompt_body() is None
    assert cfg.model.thinking is True


def test_prompt_arm_gets_fvk_version_label(tmp_path):
    prompt_file = tmp_path / "v1.md"
    prompt_file.write_text(PROMPT)
    cfg = load_config(_write_cfg(tmp_path, f"prompt:\n  system_prompt: {prompt_file}\n"))
    assert not cfg.is_baseline()
    assert cfg.prompt_version() == "v1"
    assert cfg.arm_tag() == "fvk-v1"
    assert cfg.system_prompt_body().startswith("# FVK methodology")
    assert "version: 1" not in cfg.system_prompt_body()
    assert cfg.system_prompt_sha()


def test_frontmatter_tag_overrides_arm_label(tmp_path):
    prompt_file = tmp_path / "v5.md"
    prompt_file.write_text("---\nversion: 5\ntag: review-v5\n---\n# Self-review\n")
    cfg = load_config(_write_cfg(tmp_path, f"prompt:\n  system_prompt: {prompt_file}\n"))
    assert cfg.prompt_version() == "v5"
    assert cfg.arm_tag() == "review-v5"
    assert cfg.model_label() == "deepseek-v4-flash-think__review-v5"


def test_config_tag_takes_top_precedence(tmp_path):
    cfg = load_config(_write_cfg(tmp_path, "tag: baseline-replicate-v7\n"))
    assert cfg.arm_tag() == "baseline-replicate-v7"
    with pytest.raises(ValueError, match="label-safe"):
        load_config(_write_cfg(tmp_path, "tag: 'no spaces!'\n"))
    with pytest.raises(ValueError, match="label-safe"):
        load_config(_write_cfg(tmp_path, "tag: a__b\n"))  # '__' is the label separator


def test_demos_only_arm_requires_explicit_tag(tmp_path):
    reg = tmp_path / "demos.yaml"
    reg.write_text("content_file: x.json\ndemos: {}\n")
    with pytest.raises(ValueError, match="demos-only"):
        load_config(_write_cfg(tmp_path, f"prompt:\n  demos: {reg}\n"))
    cfg = load_config(_write_cfg(tmp_path, f"tag: demos-only-v9\nprompt:\n  demos: {reg}\n"))
    assert cfg.arm_tag() == "demos-only-v9"


def test_legacy_keys_still_load(tmp_path):
    prompt_file = tmp_path / "v1.md"
    prompt_file.write_text(PROMPT)
    cfg = load_config(_write_cfg(
        tmp_path, f"variant: fvk\nprompt:\n  fvk_prompt: {prompt_file}\n"))
    assert cfg.prompt.system_prompt == str(prompt_file)
    assert cfg.arm_tag() == "fvk-v1"


def test_missing_prompt_file_rejected(tmp_path):
    with pytest.raises(FileNotFoundError, match="system prompt"):
        load_config(_write_cfg(tmp_path, "prompt:\n  system_prompt: /nope/v1.md\n"))


def test_unknown_key_rejected(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text("run_name: x\ndataset: {instance_ids: [a], typo_key: 1}\n")
    with pytest.raises(ValueError, match="typo_key"):
        load_config(p)


def test_missing_instances_rejected(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text("run_name: x\n")
    with pytest.raises(ValueError, match="instance_ids"):
        load_config(p)


CODEX_MODEL = textwrap.dedent("""\
    model:
      provider: codex-cli
      name: codex-5.5
      codex_model: gpt-5.5
      reasoning_effort: xhigh
    """)


def test_codex_provider_loads_and_labels(tmp_path):
    cfg = load_config(_write_cfg(tmp_path, CODEX_MODEL))
    assert cfg.model.provider == "codex-cli"
    assert cfg.model.codex_model == "gpt-5.5"
    assert cfg.model_label() == "codex-5.5-xhigh__baseline"


def test_codex_provider_requires_codex_model(tmp_path):
    with pytest.raises(ValueError, match="codex_model"):
        load_config(_write_cfg(tmp_path, "model:\n  provider: codex-cli\n  name: codex-5.5\n"))


def test_codex_model_rejected_for_deepseek(tmp_path):
    with pytest.raises(ValueError, match="codex_model"):
        load_config(_write_cfg(tmp_path, "model:\n  codex_model: gpt-5.5\n"))


def test_unknown_provider_rejected(tmp_path):
    with pytest.raises(ValueError, match="provider"):
        load_config(_write_cfg(tmp_path, "model:\n  provider: codexcli\n"))
