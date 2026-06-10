"""Instance selection and oracle-text loading (HuggingFace datasets)."""

from __future__ import annotations

from .config import Config


def resolve_first_n_by_repo(dataset_name: str, split: str, repo: str, n: int) -> list[str]:
    """First `n` instance_ids whose id starts with `<repo>__`, in HF row order."""
    from datasets import load_dataset

    ds = load_dataset(dataset_name, split=split)
    prefix = f"{repo}__"
    ids = [iid for iid in ds["instance_id"] if iid.startswith(prefix)]
    if len(ids) < n:
        raise ValueError(f"Only {len(ids)} instances for repo {repo!r} in {dataset_name}:{split}")
    return ids[:n]


def load_oracle_texts(cfg: Config) -> dict[str, str]:
    """instance_id -> oracle prompt text, for exactly the configured instances."""
    from datasets import load_dataset

    want = set(cfg.dataset.instance_ids)
    ds = load_dataset(cfg.dataset.oracle_text_dataset, split=cfg.dataset.split)
    texts: dict[str, str] = {}
    for row in ds:
        iid = row["instance_id"]
        if iid in want:
            texts[iid] = row["text"]
            if len(texts) == len(want):
                break
    missing = want - texts.keys()
    if missing:
        raise ValueError(
            f"{len(missing)} configured instances missing from "
            f"{cfg.dataset.oracle_text_dataset}:{cfg.dataset.split}: {sorted(missing)}"
        )
    return texts


def verify_instances_in_dataset(cfg: Config) -> None:
    """Hard-fail early if a pinned id is not in the evaluation dataset."""
    from datasets import load_dataset

    ds = load_dataset(cfg.dataset.name, split=cfg.dataset.split)
    have = set(ds["instance_id"])
    missing = set(cfg.dataset.instance_ids) - have
    if missing:
        raise ValueError(
            f"Pinned instances not in {cfg.dataset.name}:{cfg.dataset.split}: {sorted(missing)}"
        )
