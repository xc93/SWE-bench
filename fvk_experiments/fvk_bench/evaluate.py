"""Run the SWE-bench evaluation harness on a run's predictions (subprocess)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .config import Config, REPO_ROOT


def harness_report_path(run_dir: Path, model_label: str) -> Path:
    return run_dir / "eval" / f"{model_label.replace('/', '__')}.{run_dir.name}.json"


def run_eval(cfg: Config, run_dir: Path, predictions: str | None = None,
             run_id: str | None = None) -> Path:
    """Invoke swebench.harness.run_evaluation; returns the harness report path.

    `predictions` defaults to the run's predictions.jsonl; pass "gold" for a
    gold-patch sanity run.
    """
    run_id = run_id or run_dir.name
    preds = predictions or str(run_dir / "predictions.jsonl")
    (run_dir / "eval").mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "swebench.harness.run_evaluation",
        "--dataset_name", cfg.dataset.name,
        "--split", cfg.dataset.split,
        "--predictions_path", preds,
        "--instance_ids", *cfg.dataset.instance_ids,
        "--max_workers", str(cfg.eval.max_workers),
        "--timeout", str(cfg.eval.timeout_s),
        "--cache_level", cfg.eval.cache_level,
        "--run_id", run_id,
        "--report_dir", str(run_dir / "eval"),
    ]
    print(f"$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)
    label = "gold" if preds == "gold" else cfg.model_label()
    report = harness_report_path(run_dir, label)
    # The harness creates --report_dir but (as of this repo version) writes the
    # report into CWD; relocate it. The CWD copy is always the freshest, so it
    # overwrites any report from a previous eval of this run.
    stray = REPO_ROOT / report.name
    if stray.exists():
        stray.replace(report)
    if not report.exists():
        raise FileNotFoundError(f"harness report not found at {report}")
    return report


def instance_report_path(run_id: str, model_label: str, iid: str) -> Path:
    return (REPO_ROOT / "logs" / "run_evaluation" / run_id
            / model_label.replace("/", "__") / iid / "report.json")


def instance_log_path(run_id: str, model_label: str, iid: str) -> Path:
    return instance_report_path(run_id, model_label, iid).parent / "run_instance.log"


def _deterministic_failure(run_id: str, model_label: str, iid: str) -> bool:
    """True if the instance failed for a reason a re-run cannot change."""
    log = instance_log_path(run_id, model_label, iid)
    if not log.exists():
        return False
    return "Patch Apply Failed" in log.read_text(errors="replace")


def run_eval_with_retries(cfg: Config, run_dir: Path, predictions: str | None = None,
                          run_id: str | None = None) -> Path:
    """run_eval, re-running infra errors (e.g. docker pull EOF) until they clear
    or only deterministic failures (Patch Apply Failed) remain."""
    run_id = run_id or run_dir.name
    label = "gold" if predictions == "gold" else cfg.model_label()
    report = run_eval(cfg, run_dir, predictions=predictions, run_id=run_id)
    for attempt in range(cfg.eval.infra_retries):
        error_ids = json.loads(report.read_text()).get("error_ids", [])
        retryable = [i for i in error_ids
                     if not _deterministic_failure(run_id, label, i)]
        if not retryable:
            break
        print(f"[eval-retry {attempt + 1}/{cfg.eval.infra_retries}] re-running "
              f"{len(retryable)} infra-errored instances: {retryable}", flush=True)
        time.sleep(15)
        report = run_eval(cfg, run_dir, predictions=predictions, run_id=run_id)
    return report
