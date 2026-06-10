"""DeepSeek inference: threaded, resumable, with full raw provenance per instance."""

from __future__ import annotations

import json
import os
import time
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .config import Config
from .data import load_oracle_texts, verify_instances_in_dataset
from .demos import demos_shas, load_demo_texts
from .extract import extract_diff


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    os.replace(tmp, path)


def build_messages(oracle_text: str, system_text: str | None) -> list[dict]:
    msgs = []
    if system_text:
        msgs.append({"role": "system", "content": system_text})
    msgs.append({"role": "user", "content": oracle_text})
    return msgs


def _request(client, cfg: Config, messages: list[dict]):
    kwargs: dict = {
        "model": cfg.model.name,
        "messages": messages,
        "max_tokens": cfg.model.max_tokens,
        "stream": False,
        "extra_body": {
            "thinking": {"type": "enabled" if cfg.model.thinking else "disabled"},
        },
    }
    if cfg.model.temperature is not None:
        kwargs["temperature"] = cfg.model.temperature
    if cfg.model.reasoning_effort:
        kwargs["extra_body"]["reasoning_effort"] = cfg.model.reasoning_effort
    return client.chat.completions.create(**kwargs)


def _call_with_retries(client, cfg: Config, messages: list[dict]):
    last_err = None
    for attempt in range(cfg.inference.api_retries):
        try:
            return _request(client, cfg, messages)
        except Exception as e:  # noqa: BLE001 - any transport/API error is retryable here
            last_err = e
            wait = 10 * (2**attempt)
            print(f"    api error (attempt {attempt + 1}/{cfg.inference.api_retries}): "
                  f"{type(e).__name__}: {e} — retrying in {wait}s", flush=True)
            time.sleep(wait)
    raise last_err


def _run_one(client, cfg: Config, iid: str, oracle_text: str, system_text: str | None,
             run_dir: Path, resume: bool) -> dict:
    raw_path = run_dir / "raw" / f"{iid}.json"
    if resume and raw_path.exists():
        rec = json.loads(raw_path.read_text())
        if rec.get("samples"):
            # Re-derive the patch from the saved responses with the CURRENT
            # extractor (first parsable sample wins, mirroring the live loop).
            # No new API calls on resume: same model outputs, refreshed parsing.
            patch = None
            for s in rec["samples"]:
                patch = extract_diff(s.get("content") or "")
                if patch:
                    break
            rec["model_patch"] = patch or ""
            _atomic_write(raw_path, json.dumps(rec, indent=2))
            return {**rec, "resumed": True}

    messages = build_messages(oracle_text, system_text)
    pdir = run_dir / "prompts"
    if system_text:
        _atomic_write(pdir / f"{iid}.system.txt", system_text)
    _atomic_write(pdir / f"{iid}.user.txt", oracle_text)

    t0 = time.monotonic()
    samples, patch, error = [], None, None
    try:
        for sample_i in range(1 + cfg.inference.retry_on_empty_patch):
            resp = _call_with_retries(client, cfg, messages)
            choice = resp.choices[0]
            msg = choice.message.model_dump()
            content = msg.get("content") or ""
            samples.append({
                "sample": sample_i,
                "api_model": resp.model,
                "finish_reason": choice.finish_reason,
                "content": content,
                "reasoning_content": msg.get("reasoning_content"),
                "usage": resp.usage.model_dump() if resp.usage else None,
            })
            patch = extract_diff(content)
            if patch:
                break
            print(f"    {iid}: no parsable diff in sample {sample_i}, "
                  f"{'re-sampling' if sample_i < cfg.inference.retry_on_empty_patch else 'giving up'}",
                  flush=True)
    except Exception as e:  # noqa: BLE001 - record and continue with empty patch
        error = f"{type(e).__name__}: {e}"

    rec = {
        "instance_id": iid,
        "model_patch": patch or "",
        "error": error,
        "samples": samples,
        "wall_s": round(time.monotonic() - t0, 1),
        "finished_at": _now(),
    }
    _atomic_write(raw_path, json.dumps(rec, indent=2))
    return rec


def run_inference(cfg: Config, run_dir: Path, resume: bool = True) -> Path:
    """Run all configured instances; write raw/, prompts/, predictions.jsonl, meta.json."""
    from openai import OpenAI

    api_key = os.environ.get(cfg.model.api_key_env)
    if not api_key:
        raise EnvironmentError(f"{cfg.model.api_key_env} is not set")

    print(f"[{_now()}] verifying instances and loading oracle texts…", flush=True)
    verify_instances_in_dataset(cfg)
    texts = load_oracle_texts(cfg)
    static_prompt = cfg.system_prompt_body()
    demo_texts = load_demo_texts(cfg)  # {} unless prompt.demos is configured

    def system_for(iid: str) -> str | None:
        parts = [t for t in (static_prompt, demo_texts.get(iid)) if t]
        return "\n\n".join(parts) if parts else None

    for sub in ("raw", "prompts", "eval"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    if cfg.source_path:
        _atomic_write(run_dir / "config.snapshot.yaml", cfg.source_path.read_text())

    meta = {
        "run_id": run_dir.name,
        "arm": cfg.arm_tag(),
        "model_label": cfg.model_label(),
        "model": cfg.model.name,
        "thinking": cfg.model.thinking,
        "prompt_path": cfg.prompt.system_prompt,
        "prompt_version": cfg.prompt_version(),
        "prompt_sha256": cfg.system_prompt_sha(),
        **demos_shas(cfg),
        "dataset": cfg.dataset.name,
        "split": cfg.dataset.split,
        "instance_ids": cfg.dataset.instance_ids,
        "started_at": _now(),
    }
    _atomic_write(run_dir / "meta.json", json.dumps(meta, indent=2))

    client = OpenAI(api_key=api_key, base_url=cfg.model.base_url,
                    timeout=cfg.inference.request_timeout_s, max_retries=0)

    ids = cfg.dataset.instance_ids
    print(f"[{_now()}] {meta['model_label']}: {len(ids)} instances, "
          f"{cfg.inference.max_workers} workers", flush=True)
    records: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=cfg.inference.max_workers) as pool:
        futs = {pool.submit(_run_one, client, cfg, iid, texts[iid], system_for(iid),
                            run_dir, resume): iid
                for iid in ids}
        done = 0
        for fut in as_completed(futs):
            iid = futs[fut]
            rec = fut.result()
            records[iid] = rec
            done += 1
            usage = (rec.get("samples") or [{}])[-1].get("usage") or {}
            print(f"[{done}/{len(ids)}] {iid}: "
                  f"patch={'yes' if rec['model_patch'] else 'NO'}"
                  f"{' (resumed)' if rec.get('resumed') else ''}"
                  f" error={rec.get('error') or '-'}"
                  f" in_tok={usage.get('prompt_tokens', '?')}"
                  f" out_tok={usage.get('completion_tokens', '?')}"
                  f" wall={rec.get('wall_s', '?')}s", flush=True)

    pred_path = run_dir / "predictions.jsonl"
    lines = [json.dumps({"instance_id": iid,
                         "model_name_or_path": cfg.model_label(),
                         "model_patch": records[iid]["model_patch"]})
             for iid in ids]
    _atomic_write(pred_path, "\n".join(lines) + "\n")

    meta["finished_at"] = _now()
    meta["n_with_patch"] = sum(1 for r in records.values() if r["model_patch"])
    meta["n_errors"] = sum(1 for r in records.values() if r.get("error"))
    _atomic_write(run_dir / "meta.json", json.dumps(meta, indent=2))
    print(f"[{_now()}] inference done: {meta['n_with_patch']}/{len(ids)} with patches, "
          f"{meta['n_errors']} errors -> {pred_path}", flush=True)
    return pred_path
