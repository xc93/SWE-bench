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
        # Phased agentic arms also harvest a v1 (pre-self-review) patch set:
        # grade it through the same official harness under "<run_id>-v1" so the
        # report can show the v1 -> v2 transition with executed verdicts.
        v1_preds = run_dir / "predictions_v1.jsonl"
        if v1_preds.exists():
            run_eval_with_retries(cfg, run_dir, predictions=str(v1_preds),
                                  run_id=f"{run_id}-v1")
    if "report" in stages:
        out = write_run_report(run_dir)
        from fvk_bench.report import write_results_index
        write_results_index()
        s = json.loads((run_dir / "summary.json").read_text())
        print(f"\n=== {s['arm']}: solved {s['solved_count']}/{s['n_instances']} "
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


def cmd_isolation_probe(args) -> int:
    """Self-check the production launch path: sealed HOME + an out-of-repo
    throwaway workspace, one real claude session, a trivial prompt asking what
    project notes / memory / special instructions and non-built-in tools the
    agent can see. Prints the agent's final text and the tool names in the
    stream so we can confirm NO experiment notes and NO playwright/vercel/etc.
    """
    import shutil
    import tempfile

    from fvk_bench.agentic import workspaces_root
    from fvk_bench.agents.claude_code import (build_claude_argv, parse_stream,
                                              resolve_claude_bin, run_claude_session)
    from fvk_bench.agents.profile import ensure_sealed_home, sealed_env
    from fvk_bench.config import (Config, DatasetCfg, EvalCfg, InferenceCfg,
                                  ModelCfg, PromptCfg)

    claude_bin = args.claude_bin or resolve_claude_bin()
    cc_model = args.model

    # EXACT production sealed launch: sealed HOME (no user CLAUDE.md/memory/
    # plugins) + the same argv builder used by real arms.
    sealed = ensure_sealed_home()
    env = sealed_env(sealed)
    cfg = Config(
        run_name="isolation-probe",
        dataset=DatasetCfg(instance_ids=["probe"]),
        model=ModelCfg(provider="claude-code", name="claude-code-probe",
                       cc_model=cc_model, max_turns=4, session_timeout_s=args.timeout),
        inference=InferenceCfg(), eval=EvalCfg(), prompt=PromptCfg(),
    )
    argv = build_claude_argv(claude_bin, cfg)

    # Throwaway workspace OUTSIDE the repo (under workspaces_root), so no
    # repo-ancestor CLAUDE.md is discoverable from the session cwd.
    ws_root = workspaces_root() / "_isolation_probe"
    ws_root.mkdir(parents=True, exist_ok=True)
    ws = Path(tempfile.mkdtemp(prefix="probe-", dir=ws_root))
    stream_path = ws / "stream.jsonl"
    prompt = (
        "This is an isolation self-check. Do not edit files. Briefly answer two "
        "things: (1) list any project notes, memory, or special instructions you "
        "can see (CLAUDE.md, project memory, anything describing a task or "
        "experiment) — if none, say 'NONE'; (2) list the names of any non-built-in "
        "tools available to you (plugins, MCP servers); if only the standard "
        "built-in tools are available, say 'only built-in tools'.")

    print(f"sealed HOME: {sealed}\nsealed env: HOME={env['HOME']} "
          f"CLAUDE_CONFIG_DIR={env.get('CLAUDE_CONFIG_DIR')}")
    print(f"argv: {' '.join(argv)}")
    print(f"cwd (throwaway, out-of-repo): {ws}\n--- running one session ---", flush=True)
    res = run_claude_session(argv, prompt, cwd=ws, timeout_s=args.timeout,
                             stream_path=stream_path, env=env)
    events = parse_stream(stream_path)

    # Final assistant text + every tool name seen in the stream.
    final_text, tool_names = "", []
    for ev in events:
        if ev.get("type") == "assistant":
            for block in (ev.get("message") or {}).get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text" and (block.get("text") or "").strip():
                    final_text = block["text"]
                elif block.get("type") == "tool_use" and block.get("name"):
                    if block["name"] not in tool_names:
                        tool_names.append(block["name"])
    # The session's advertised toolset (system init event), if present.
    init_tools = []
    for ev in events:
        if ev.get("type") == "system" and ev.get("tools"):
            init_tools = ev["tools"]
            break

    authed = bool(events) and any(e.get("type") == "assistant" for e in events)
    BAD = ("playwright", "vercel", "telegram", "superpowers", "chrome-devtools")
    advertised = init_tools or tool_names
    leaked = sorted({t for t in advertised
                     for b in BAD if b in str(t).lower()})

    print("\n=== ISOLATION PROBE RESULT ===")
    print(f"(a) authenticated: {'YES' if authed else 'NO'} "
          f"(rc={res['returncode']}, timed_out={res['timed_out']})")
    if not authed:
        print(f"    stderr tail: {res['stderr_tail'][-500:]!r}")
    print(f"(b) agent final text:\n{final_text or '(none)'}")
    print(f"(c) tools advertised (system init): {init_tools or '(none in stream)'}")
    print(f"    tools actually used: {tool_names or '(none)'}")
    print(f"    leaked plugin/MCP tools (MUST be empty): {leaked or 'NONE ✅'}")
    print(f"\nstream: {stream_path}")
    if not args.keep:
        shutil.rmtree(ws, ignore_errors=True)
    return 0


def cmd_prepull_images(args) -> int:
    """Warm the local docker cache with each pinned instance's OFFICIAL eval
    image (the v2 in-session evaluator and the final harness both use it).
    Sequential on purpose: registry-1.docker.io flakes under parallel pulls on
    this host. Re-runnable; already-present images are instant."""
    from fvk_bench.agentic import ensure_instance_image, instance_image_candidates
    from fvk_bench.data import load_full_rows

    cfg = load_config(args.config)
    rows = load_full_rows(cfg)
    failed: list[str] = []
    for i, iid in enumerate(cfg.dataset.instance_ids, 1):
        try:
            name = ensure_instance_image(rows[iid], retries=args.retries)
            print(f"[{i}/{len(cfg.dataset.instance_ids)}] ok {iid}: {name}", flush=True)
        except Exception as e:  # noqa: BLE001 — keep pulling the rest
            failed.append(iid)
            print(f"[{i}/{len(cfg.dataset.instance_ids)}] FAILED {iid}: "
                  f"{str(e)[-300:]}", flush=True)
            print(f"    candidates were: {instance_image_candidates(rows[iid])}",
                  flush=True)
    if failed:
        print(f"\n{len(failed)} image(s) NOT available — rerun before the arm: {failed}")
        return 1
    print(f"\nall {len(cfg.dataset.instance_ids)} eval images present")
    return 0


def cmd_build_demos(args) -> int:
    from fvk_bench.demos import build_content

    out = build_content(Path(args.registry).resolve(),
                        source_json=Path(args.source) if args.source else None)
    data = json.loads(out.read_text())
    sizes = {t: sum(len(p["problem_statement"]) + len(p["patch"]) for p in picks)
             for t, picks in data["demos"].items()}
    print(f"content frozen: {out}")
    for t, n in sorted(sizes.items()):
        print(f"  {t}: 3 demos, {n:,} chars (~{n // 4:,} tok)")
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

    pi = sub.add_parser("isolation-probe",
                        help="self-check the sealed launch path: one claude session "
                             "in a sealed HOME + out-of-repo workspace; prints what "
                             "project notes / tools the agent can see")
    pi.add_argument("--model", default="claude-opus-4-6",
                    help="claude --model value (default: claude-opus-4-6)")
    pi.add_argument("--claude-bin", default=None, help="override the claude binary")
    pi.add_argument("--timeout", type=int, default=180, help="session timeout (s)")
    pi.add_argument("--keep", action="store_true",
                    help="keep the throwaway workspace dir")
    pi.set_defaults(fn=cmd_isolation_probe)

    pq = sub.add_parser("prepull-images",
                        help="pull each pinned instance's official eval image "
                             "(sequential; rerun until clean before a v2 arm)")
    pq.add_argument("--config", required=True)
    pq.add_argument("--retries", type=int, default=2,
                    help="extra pull attempts per image (docker hub flakes)")
    pq.set_defaults(fn=cmd_prepull_images)

    pd = sub.add_parser("build-demos",
                        help="freeze demo content JSON from a demos registry YAML")
    pd.add_argument("--registry", required=True)
    pd.add_argument("--source", default=None,
                    help="optional id->{problem_statement,patch} JSON (skips dataset download)")
    pd.set_defaults(fn=cmd_build_demos)

    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
