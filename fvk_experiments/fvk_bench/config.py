"""YAML config -> validated dataclasses, plus arm labeling helpers.

An arm is defined by WHAT IT INJECTS into the system message, not by a declared
type:

  - nothing                      -> arm "baseline"
  - static prompt and/or demos   -> a treatment arm

The arm label (used in run ids, prediction labels, and reports) resolves by
precedence: config-level `tag:` > the prompt file's frontmatter `tag:` >
"baseline" (nothing injected) > "fvk-<version>" (static prompt present).
A demos-only arm has no natural default and must set `tag:` explicitly.

Legacy keys accepted on load: top-level `variant:` (ignored — it was redundant)
and `prompt.fvk_prompt` (alias of `prompt.system_prompt`).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

EXP_ROOT = Path(__file__).resolve().parent.parent  # fvk_experiments/
REPO_ROOT = EXP_ROOT.parent  # SWE-bench checkout

_LABEL_RE = re.compile(r"[A-Za-z0-9._-]+")


def resolve_path(p: str | Path) -> Path:
    """Paths in configs are relative to fvk_experiments/."""
    p = Path(p)
    return p if p.is_absolute() else EXP_ROOT / p


def _check_label(label: str, what: str) -> str:
    if not _LABEL_RE.fullmatch(label) or "__" in label:
        raise ValueError(
            f"{what} must be label-safe ([A-Za-z0-9._-], no '__'): {label!r}")
    return label


@dataclass
class DatasetCfg:
    name: str = "princeton-nlp/SWE-bench_Verified"
    split: str = "test"
    oracle_text_dataset: str = "princeton-nlp/SWE-bench_oracle"
    instance_ids: list[str] = field(default_factory=list)


@dataclass
class ModelCfg:
    name: str = "deepseek-v4-flash"
    # "deepseek" (OpenAI-compatible API, needs api_key_env) or "codex-cli" (one-shot
    # `codex exec` under a ChatGPT subscription — no API key; `thinking`/`max_tokens`
    # are ignored, the Codex harness controls both).
    provider: str = "deepseek"
    base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"
    thinking: bool = True
    reasoning_effort: str | None = None
    max_tokens: int = 65536
    temperature: float | None = None
    # `codex exec -m` value (e.g. gpt-5.5); required for codex-cli, rejected otherwise.
    codex_model: str | None = None


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
    # Static system prompt file (frontmatter: version/date/source, optional tag).
    system_prompt: str | None = None
    # Per-instance demonstrations: path to a demos registry YAML; its frozen
    # .content.json gets appended to the system message per test instance.
    demos: str | None = None


@dataclass
class Config:
    run_name: str
    dataset: DatasetCfg
    model: ModelCfg
    inference: InferenceCfg
    eval: EvalCfg
    prompt: PromptCfg
    # Optional arm-label override (e.g. "baseline-replicate-v7").
    tag: str | None = None
    source_path: Path | None = None

    # ---- static prompt helpers -------------------------------------------
    def system_prompt_path(self) -> Path | None:
        return resolve_path(self.prompt.system_prompt) if self.prompt.system_prompt else None

    def _prompt_raw(self) -> str | None:
        p = self.system_prompt_path()
        return p.read_text() if p else None

    def _prompt_frontmatter(self) -> dict:
        raw = self._prompt_raw()
        if raw is None:
            return {}
        m = re.match(r"\A---\n(.*?)\n---\n", raw, re.DOTALL)
        if not m:
            return {}
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def system_prompt_body(self) -> str | None:
        """Prompt content with YAML frontmatter stripped (what gets injected)."""
        raw = self._prompt_raw()
        if raw is None:
            return None
        m = re.match(r"\A---\n.*?\n---\n", raw, re.DOTALL)
        return raw[m.end():].lstrip("\n") if m else raw

    def system_prompt_sha(self) -> str | None:
        p = self.system_prompt_path()
        return hashlib.sha256(p.read_bytes()).hexdigest() if p else None

    def prompt_version(self) -> str | None:
        """`version:` from the prompt frontmatter, else the filename stem."""
        if not self.prompt.system_prompt:
            return None
        fm = self._prompt_frontmatter()
        if "version" in fm:
            v = str(fm["version"])
            return v if v.startswith("v") else f"v{v}"
        return self.system_prompt_path().stem

    # ---- arm labeling ------------------------------------------------------
    def is_baseline(self) -> bool:
        return not (self.prompt.system_prompt or self.prompt.demos)

    def arm_tag(self) -> str:
        if self.tag:
            return _check_label(str(self.tag), "config tag")
        if self.is_baseline():
            return "baseline"
        fm_tag = self._prompt_frontmatter().get("tag")
        if fm_tag:
            return _check_label(str(fm_tag), "prompt frontmatter tag")
        if self.prompt.system_prompt:
            return f"fvk-{self.prompt_version()}"
        raise ValueError(
            "a demos-only arm has no default label — set a config-level `tag:`")

    def model_label(self) -> str:
        if self.model.provider == "codex-cli":
            effort = f"-{self.model.reasoning_effort}" if self.model.reasoning_effort else ""
            return f"{self.model.name}{effort}__{self.arm_tag()}"
        think = "think" if self.model.thinking else "nothink"
        return f"{self.model.name}-{think}__{self.arm_tag()}"


def _build(cls, d: dict):
    fields = {f for f in cls.__dataclass_fields__}
    unknown = set(d) - fields
    if unknown:
        raise ValueError(f"Unknown {cls.__name__} keys: {sorted(unknown)}")
    return cls(**d)


def load_config(path: str | Path) -> Config:
    path = Path(path)
    raw = yaml.safe_load(path.read_text())
    raw.pop("variant", None)  # legacy: arm type is derived now
    prompt_raw = raw.get("prompt", {})
    if "fvk_prompt" in prompt_raw:  # legacy alias
        prompt_raw.setdefault("system_prompt", prompt_raw.pop("fvk_prompt"))
    cfg = Config(
        run_name=raw["run_name"],
        dataset=_build(DatasetCfg, raw.get("dataset", {})),
        model=_build(ModelCfg, raw.get("model", {})),
        inference=_build(InferenceCfg, raw.get("inference", {})),
        eval=_build(EvalCfg, raw.get("eval", {})),
        prompt=_build(PromptCfg, prompt_raw),
        tag=raw.get("tag"),
        source_path=path.resolve(),
    )
    validate(cfg)
    return cfg


def validate(cfg: Config) -> None:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", cfg.run_name):
        raise ValueError("run_name must be filesystem/docker safe: [A-Za-z0-9._-]+")
    if not cfg.dataset.instance_ids:
        raise ValueError("dataset.instance_ids must be a non-empty pinned list")
    if cfg.model.provider not in ("deepseek", "codex-cli"):
        raise ValueError(
            f"model.provider must be 'deepseek' or 'codex-cli', got {cfg.model.provider!r}")
    if cfg.model.provider == "codex-cli" and not cfg.model.codex_model:
        raise ValueError(
            "provider 'codex-cli' requires model.codex_model (the `codex exec -m` value)")
    if cfg.model.provider != "codex-cli" and cfg.model.codex_model:
        raise ValueError("model.codex_model is only valid with provider 'codex-cli'")
    if cfg.prompt.style != "oracle":
        raise ValueError(f"only prompt.style 'oracle' is supported, got {cfg.prompt.style!r}")
    if cfg.prompt.system_prompt and not cfg.system_prompt_path().exists():
        raise FileNotFoundError(f"system prompt file not found: {cfg.prompt.system_prompt}")
    if cfg.prompt.demos and not resolve_path(cfg.prompt.demos).exists():
        raise FileNotFoundError(f"demos registry not found: {cfg.prompt.demos}")
    cfg.arm_tag()  # resolvable and label-safe, or raises
