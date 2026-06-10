#!/usr/bin/env python
"""CLI for FVK pair-comparison experiments on SWE-bench.

Run from anywhere with the repo venv, e.g.:
    .venv/bin/python fvk_experiments/run.py run --config fvk_experiments/configs/astropy10_baseline.yaml
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fvk_bench.config import EXP_ROOT, load_config  # noqa: E402

STAGES = ("infer", "eval", "report")


def _ts() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")


def cmd_run(args) -> int:
    from fvk_bench.evaluate import run_eval_with_retries
    from fvk_bench.inference import run_inference
    from fvk_bench.report import write_run_report

    cfg = load_config(args.config)
    stages = args.stages.split(",")
    bad = set(stages) - set(STAGES)
    if bad:
        raise SystemExit(f"unknown stages: {sorted(bad)} (valid: {','.join(STAGES)})")

    run_id = args.run_id or f"{cfg.run_name}__{_ts()}"
    run_dir = EXP_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"run_id: {run_id}\nrun_dir: {run_dir}", flush=True)

    if "infer" in stages:
        run_inference(cfg, run_dir, resume=not args.no_resume)
    if "eval" in stages:
        run_eval_with_retries(cfg, run_dir)
    if "report" in stages:
        out = write_run_report(cfg, run_dir)
        from fvk_bench.report import write_results_index
        write_results_index()
        s = json.loads((run_dir / "summary.json").read_text())
        print(f"\n=== {s['variant_tag']}: solved {s['solved_count']}/{s['n_instances']} "
              f"=== \nreport: {out}", flush=True)
    return 0


def cmd_pin_instances(args) -> int:
    from fvk_bench.data import resolve_first_n_by_repo

    ids = resolve_first_n_by_repo(args.dataset, args.split, args.repo, args.n)
    print(f"# first {args.n} {args.repo} instances of {args.dataset}:{args.split} "
          f"(HF row order), resolved {dt.date.today().isoformat()}")
    print("instance_ids:")
    for iid in ids:
        print(f"  - {iid}")
    return 0


def cmd_gold_sanity(args) -> int:
    from fvk_bench.evaluate import run_eval_with_retries

    cfg = load_config(args.config)
    run_id = f"gold-sanity__{cfg.run_name}__{_ts()}"
    run_dir = EXP_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    report = run_eval_with_retries(cfg, run_dir, predictions="gold", run_id=run_id)
    rep = json.loads(report.read_text())
    print(f"\n=== gold sanity: resolved {rep.get('resolved_instances')}"
          f"/{rep.get('total_instances')} ===")
    unresolved = rep.get("unresolved_ids", []) + rep.get("error_ids", [])
    if unresolved:
        print(f"NOT clean — investigate before trusting model evals: {unresolved}")
    print(f"report: {report}")
    return 0


def cmd_compare(args) -> int:
    from fvk_bench.report import write_pair_report, write_results_index

    b, t = Path(args.baseline), Path(args.treatment)
    out = Path(args.out) if args.out else (
        EXP_ROOT / "reports" / f"pair__{b.name}__VS__{t.name}.md")
    write_pair_report(b, t, out)
    write_results_index()
    print(f"pair report: {out}")
    print(out.read_text())
    return 0


def cmd_results(args) -> int:
    from fvk_bench.report import write_results_index

    out = write_results_index()
    print(f"results index regenerated: {out}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="run one experiment arm from a config")
    pr.add_argument("--config", required=True)
    pr.add_argument("--stages", default="infer,eval,report",
                    help=f"comma-separated subset of {','.join(STAGES)}")
    pr.add_argument("--run-id", default=None,
                    help="reuse an existing run dir (default: <run_name>__<utc timestamp>)")
    pr.add_argument("--no-resume", action="store_true",
                    help="re-query the API even for instances with saved responses")
    pr.set_defaults(fn=cmd_run)

    pp = sub.add_parser("pin-instances", help="print pinned instance ids for a config")
    pp.add_argument("--dataset", default="princeton-nlp/SWE-bench_Verified")
    pp.add_argument("--split", default="test")
    pp.add_argument("--repo", required=True, help="e.g. astropy")
    pp.add_argument("--n", type=int, default=10)
    pp.set_defaults(fn=cmd_pin_instances)

    pg = sub.add_parser("gold-sanity", help="evaluate gold patches for a config's instances")
    pg.add_argument("--config", required=True)
    pg.set_defaults(fn=cmd_gold_sanity)

    pc = sub.add_parser("compare", help="write a pair-comparison report from two run dirs")
    pc.add_argument("--baseline", required=True)
    pc.add_argument("--treatment", required=True)
    pc.add_argument("--out", default=None)
    pc.set_defaults(fn=cmd_compare)

    ps = sub.add_parser("results", help="regenerate RESULTS.md from run artifacts")
    ps.set_defaults(fn=cmd_results)

    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
