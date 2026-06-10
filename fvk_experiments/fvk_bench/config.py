"""YAML config -> validated dataclasses, plus run/prompt labeling helpers."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

EXP_ROOT = Path(__file__).resolve().parent.parent  # fvk_experiments/
REPO_ROOT = EXP_ROOT.parent  # SWE-bench checkout


@dataclass
class DatasetCfg:
    name: str = "princeton-nlp/SWE-bench_Verified"
    split: str = "test"
    oracle_text_dataset: str = "princeton-nlp/SWE-bench_oracle"
    instance_ids: list[str] = field(default_factory=list)


@dataclass
class ModelCfg:
    name: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"
    thinking: bool = True
    reasoning_effort: str | None = None
    max_tokens: int = 65536
    temperature: float | None = None


@dataclass
class InferenceCfg:
    max_workers: int = 4
    request_timeout_s: int = 2400
    api_retries: int = 3
    retry_on_empty_patch: int = 1


@dataclass
class EvalCfg:
    max_workers: int = 4
    timeout_s: int = 1800
    # Keep pulled instance images so eval retries/reruns don't depend on the
    # (flaky) registry connection.
    cache_level: str = "instance"
    # Re-run the harness for instances that error on infra (e.g. docker pull
    # failures) up to this many extra times; deterministic failures like
    # "Patch Apply Failed" are not retried.
    infra_retries: int = 3


@dataclass
class PromptCfg:
    style: str = "oracle"
    fvk_prompt: str | None = None  # path relative to fvk_experiments/
    # Optional per-instance demonstrations (joint-embedding mimic): path to a
    # demos registry YAML; its frozen .content.json gets appended to the system
    # message per test instance. See fvk_bench/demos.py.
    demos: str | None = None


@dataclass
class Config:
    run_name: str
    variant: str  # "baseline" | "fvk"
    dataset: DatasetCfg
    model: ModelCfg
    inference: InferenceCfg
    eval: EvalCfg
    prompt: PromptCfg
    source_path: Path | None = None

    # ---- prompt helpers -------------------------------------------------
    def fvk_prompt_path(self) -> Path | None:
        if not self.prompt.fvk_prompt:
            return None
        p = Path(self.prompt.fvk_prompt)
        return p if p.is_absolute() else EXP_ROOT / p

    def fvk_prompt_file_text(self) -> str | None:
        p = self.fvk_prompt_path()
        return p.read_text() if p else None

    def fvk_prompt_body(self) -> str | None:
        """Prompt content with YAML frontmatter stripped (what gets injected)."""
        raw = self.fvk_prompt_file_text()
        if raw is None:
            return None
        m = re.match(r"\A---\n.*?\n---\n", raw, re.DOTALL)
        return raw[m.end():].lstrip("\n") if m else raw

    def fvk_prompt_sha(self) -> str | None:
        p = self.fvk_prompt_path()
        if not p:
            return None
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def _prompt_frontmatter(self) -> dict:
        raw = self.fvk_prompt_file_text()
        if raw is None:
            return {}
        m = re.match(r"\A---\n(.*?)\n---\n", raw, re.DOTALL)
        if not m:
            return {}
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def fvk_prompt_version(self) -> str | None:
        """`version:` from the prompt frontmatter, else the filename stem."""
        if not self.prompt.fvk_prompt:
            return None
        fm = self._prompt_frontmatter()
        if "version" in fm:
            v = str(fm["version"])
            return v if v.startswith("v") else f"v{v}"
        return self.fvk_prompt_path().stem

    # ---- labels ----------------------------------------------------------
    def variant_tag(self) -> str:
        """Arm label: `tag:` from the prompt frontmatter when present (for
        non-FVK control prompts, e.g. `review-v5`), else fvk-<version>."""
        if self.variant == "baseline":
            return "baseline"
        tag = self._prompt_frontmatter().get("tag")
        if tag:
            tag = str(tag)
            if not re.fullmatch(r"[A-Za-z0-9._-]+", tag):
                raise ValueError(f"prompt frontmatter tag must be label-safe: {tag!r}")
            return tag
        return f"fvk-{self.fvk_prompt_version()}"

    def model_label(self) -> str:
        think = "think" if self.model.thinking else "nothink"
        return f"{self.model.name}-{think}__{self.variant_tag()}"


def _build(cls, d: dict):
    fields = {f for f in cls.__dataclass_fields__}
    unknown = set(d) - fields
    if unknown:
        raise ValueError(f"Unknown {cls.__name__} keys: {sorted(unknown)}")
    return cls(**d)


def load_config(path: str | Path) -> Config:
    path = Path(path)
    raw = yaml.safe_load(path.read_text())
    cfg = Config(
        run_name=raw["run_name"],
        variant=raw["variant"],
        dataset=_build(DatasetCfg, raw.get("dataset", {})),
        model=_build(ModelCfg, raw.get("model", {})),
        inference=_build(InferenceCfg, raw.get("inference", {})),
        eval=_build(EvalCfg, raw.get("eval", {})),
        prompt=_build(PromptCfg, raw.get("prompt", {})),
        source_path=path.resolve(),
    )
    validate(cfg)
    return cfg


def validate(cfg: Config) -> None:
    if cfg.variant not in ("baseline", "fvk"):
        raise ValueError(f"variant must be 'baseline' or 'fvk', got {cfg.variant!r}")
    if cfg.variant == "fvk":
        p = cfg.fvk_prompt_path()
        if not p:
            raise ValueError("variant 'fvk' requires prompt.fvk_prompt to be set")
        if not p.exists():
            raise FileNotFoundError(f"FVK prompt file not found: {p}")
    if cfg.variant == "baseline" and cfg.prompt.fvk_prompt:
        raise ValueError("variant 'baseline' must not set prompt.fvk_prompt")
    if cfg.prompt.demos:
        if cfg.variant != "fvk":
            raise ValueError("prompt.demos requires the treatment variant 'fvk'")
        p = Path(cfg.prompt.demos)
        if not (p if p.is_absolute() else EXP_ROOT / p).exists():
            raise FileNotFoundError(f"demos registry not found: {cfg.prompt.demos}")
    if not cfg.dataset.instance_ids:
        raise ValueError("dataset.instance_ids must be a non-empty pinned list")
    if cfg.prompt.style != "oracle":
        raise ValueError(f"only prompt.style 'oracle' is supported, got {cfg.prompt.style!r}")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", cfg.run_name):
        raise ValueError("run_name must be filesystem/docker safe: [A-Za-z0-9._-]+")
