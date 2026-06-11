"""Per-run report.md + summary.json, pair comparisons, and the RESULTS.md index.

Everything here derives from a run's FROZEN artifacts (meta.json, harness report,
raw/ records) — never from a live config — so editing a config after a run can
never re-label history. Readers accept both current and legacy artifact keys
(`arm`/`variant_tag`, `prompt_*`/`fvk_prompt_*`) so old runs keep rendering.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

from .config import EXP_ROOT
from .evaluate import instance_report_path


def _today() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _mark(v: bool | None) -> str:
    return {True: "✅ yes", False: "❌ no"}.get(v, "—")


def _get(d: dict, *keys, default=None):
    """First non-None value among (current, legacy...) artifact keys."""
    for k in keys:
        if d.get(k) is not None:
            return d[k]
    return default


def _arm(s: dict) -> str:
    return _get(s, "arm", "variant_tag", default="?")


def collect_run_summary(run_dir: Path) -> dict:
    """Join the run's meta + harness report + per-instance reports + raw records."""
    meta = json.loads((run_dir / "meta.json").read_text())
    label = meta["model_label"]
    ids = meta["instance_ids"]
    run_id = meta.get("run_id", run_dir.name)
    harness_path = run_dir / "eval" / f"{label.replace('/', '__')}.{run_id}.json"
    harness = json.loads(harness_path.read_text())
    resolved = set(harness.get("resolved_ids", []))

    instances = []
    for iid in ids:
        raw_p = run_dir / "raw" / f"{iid}.json"
        raw = json.loads(raw_p.read_text()) if raw_p.exists() else {}
        irep_p = instance_report_path(run_id, label, iid)
        irep = {}
        if irep_p.exists():
            try:
                irep = json.loads(irep_p.read_text()).get(iid, {})
            except json.JSONDecodeError:
                pass
        usage = (raw.get("samples") or [{}])[-1].get("usage") or {}
        instances.append({
            "instance_id": iid,
            "patch_extracted": bool(raw.get("model_patch")),
            "n_samples": len(raw.get("samples") or []),
            "inference_error": raw.get("error"),
            "patch_applied": irep.get("patch_successfully_applied"),
            "resolved": iid in resolved,
            "contaminated": bool(raw.get("contaminated")),
            "contamination_evidence": raw.get("contamination_evidence") or [],
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "wall_s": raw.get("wall_s"),
        })

    summary = {
        "run_id": run_id,
        "generated_at": _today(),
        "arm": _arm(meta),
        "model_label": label,
        "model": meta.get("model"),
        "thinking": meta.get("thinking"),
        "prompt_version": _get(meta, "prompt_version", "fvk_prompt_version"),
        "prompt_sha256": _get(meta, "prompt_sha256", "fvk_prompt_sha256"),
        "demos_registry": meta.get("demos_registry"),
        "demos_registry_sha256": meta.get("demos_registry_sha256"),
        "demos_content_sha256": meta.get("demos_content_sha256"),
        "dataset": meta.get("dataset"),
        "n_instances": len(ids),
        "solved_count": len(resolved & set(ids)),
        "resolved_ids": sorted(resolved & set(ids)),
        "contaminated_ids": sorted(i["instance_id"] for i in instances
                                   if i["contaminated"]),
        "empty_patch_ids": harness.get("empty_patch_ids", []),
        "error_ids": harness.get("error_ids", []),
        "harness_report": str(harness_path),
        "meta": meta,
        "instances": instances,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


# ---- agentic (claude-code) extras: v1->v2 transitions + claimed-vs-official ----

# Tolerant of both shapes in the wild: the evaluator's "FAIL_TO_PASS 2/2" and
# the protocol reports' "FAIL_TO_PASS: 2 / 2" / "Resolved: true".
_CLAIM_F2P = re.compile(r"FAIL_TO_PASS:?\s*(\d+)\s*/\s*(\d+)")
_CLAIM_P2P = re.compile(r"PASS_TO_PASS:?\s*(\d+)\s*/\s*(\d+)")
_CLAIM_RES = re.compile(r"resolved:\s*\**\s*(true|false)", re.I)


def parse_claimed_aggregates(text: str) -> dict | None:
    """LAST private-evaluator-shaped aggregate claim in `text` (the final
    self-eval is what the agent reports), or None."""
    f2p = _CLAIM_F2P.findall(text)
    p2p = _CLAIM_P2P.findall(text)
    res = _CLAIM_RES.findall(text)
    if not (f2p or res):
        return None
    return {
        "FAIL_TO_PASS": "/".join(f2p[-1]) if f2p else None,
        "PASS_TO_PASS": "/".join(p2p[-1]) if p2p else None,
        "resolved": res[-1].lower() == "true" if res else None,
    }


def claimed_for_instance(artifacts_dir: Path) -> dict | None:
    """In-session claimed aggregates from a harvested artifacts/<iid>/reports/."""
    reports = artifacts_dir / "reports"
    if not reports.is_dir():
        return None
    texts = []
    for f in sorted(reports.rglob("*")):
        if f.is_file() and f.suffix.lower() in (".md", ".txt", ".json", ""):
            try:
                texts.append(f.read_text(errors="replace"))
            except OSError:
                continue
    return parse_claimed_aggregates("\n".join(texts)) if texts else None


def render_transition_table(ids: list[str], v1_resolved: set[str],
                            v2_resolved: set[str],
                            claimed_by_iid: dict[str, dict | None]) -> str:
    """Markdown: per-instance v1->v2 official verdicts + claimed cross-check."""
    def _rx(resolved: bool) -> str:
        return "R" if resolved else "X"

    rows = []
    counts = {"R→R": 0, "R→X": 0, "X→R": 0, "X→X": 0}
    for iid in ids:
        v1, v2 = iid in v1_resolved, iid in v2_resolved
        trans = f"{_rx(v1)}→{_rx(v2)}"
        counts[trans] += 1
        marker = {"X→R": " 📈", "R→X": " 📉"}.get(trans, "")
        claim = claimed_by_iid.get(iid)
        if claim is None:
            claim_cell, check = "—", "—"
        else:
            claim_cell = (f"F2P {claim['FAIL_TO_PASS'] or '?'} · "
                          f"P2P {claim['PASS_TO_PASS'] or '?'} · "
                          f"resolved {claim['resolved']}")
            check = ("—" if claim["resolved"] is None
                     else ("✅ match" if claim["resolved"] == v2 else "❌ MISMATCH"))
        rows.append(f"| {iid} | {_mark(v1)} | {_mark(v2)} | {trans}{marker} "
                    f"| {claim_cell} | {check} |")
    header = ("| instance_id | v1 resolved (official) | v2 resolved (official) "
              "| v1→v2 | claimed (in-session) | claimed = official |\n"
              "|---|---|---|---|---|---|")
    summary = (f"Transitions: R→R {counts['R→R']} · R→X {counts['R→X']} · "
               f"X→R {counts['X→R']} · X→X {counts['X→X']}")
    return header + "\n" + "\n".join(rows) + "\n\n" + summary


def _agentic_section(run_dir: Path, s: dict) -> str:
    """v1->v2 section for phased agentic runs; '' when the run has no v1 pass."""
    label = s["model_label"].replace("/", "__")
    v1_report = run_dir / "eval" / f"{label}.{s['run_id']}-v1.json"
    if not v1_report.exists():
        return ""
    try:
        v1 = json.loads(v1_report.read_text())
    except (OSError, json.JSONDecodeError):
        return ""
    ids = [i["instance_id"] for i in s["instances"]]
    v1_resolved = set(v1.get("resolved_ids", [])) & set(ids)
    v2_resolved = set(s["resolved_ids"])
    claimed = {iid: claimed_for_instance(run_dir / "artifacts" / iid) for iid in ids}
    table = render_transition_table(ids, v1_resolved, v2_resolved, claimed)
    return (f"\n## Agentic phases: v1 → v2 (official harness verdicts)\n\n"
            f"v1 = the pre-self-review patch (`predictions_v1.jsonl`, harness run "
            f"`{s['run_id']}-v1`); v2 = the final submission. \"claimed\" is what the "
            f"session's own report asserted (parsed from `artifacts/<iid>/reports/`).\n\n"
            f"**v1 solved {len(v1_resolved)} / {len(ids)}** → "
            f"**v2 solved {s['solved_count']} / {len(ids)}**\n\n"
            f"{table}\n")


def _contamination_banner(s: dict) -> str:
    """Prominent invalidation notice for runs with contaminated instances.

    A contaminated instance read the out-of-workspace answer key (or leaked a
    hidden FAIL_TO_PASS name before its eval): its prediction was emptied, so it
    is scored unsolved regardless of what patch it produced."""
    cids = s.get("contaminated_ids") or []
    if not cids:
        return ""
    by_id = {i["instance_id"]: i for i in s["instances"]}
    lines = [f"\n> ⚠️ **{len(cids)} INVALIDATED for contamination** — prediction emptied, "
             f"scored unsolved. Evidence in `audit/<iid>.json`."]
    for iid in cids:
        ev = "; ".join(by_id.get(iid, {}).get("contamination_evidence") or []) or "see audit"
        lines.append(f"> - `{iid}` — {ev[:300]}")
    return "\n".join(lines) + "\n"


def write_run_report(run_dir: Path) -> Path:
    s = collect_run_summary(run_dir)
    if s["prompt_version"]:
        prompt_line = (f"- **System prompt**: `{s['meta'].get('prompt_path') or s['meta'].get('fvk_prompt_path')}` "
                       f"(version **{s['prompt_version']}**, sha256 `{(s['prompt_sha256'] or '')[:12]}…`)\n")
    else:
        prompt_line = "- **System prompt**: none\n"
    demos_line = ""
    if s.get("demos_registry"):
        demos_line = (f"- **Demos**: `{s['demos_registry']}` (registry sha `{(s['demos_registry_sha256'] or '')[:12]}…`, "
                      f"content sha `{(s['demos_content_sha256'] or '')[:12]}…`)\n")
    rows = "\n".join(
        f"| {i['instance_id']}{' ⚠️ CONTAMINATED' if i['contaminated'] else ''} "
        f"| {_mark(i['patch_extracted'])} | {_mark(i['patch_applied'])} "
        f"| {_mark(i['resolved'])} | {i['n_samples']} | {i['prompt_tokens'] or '—'} "
        f"| {i['completion_tokens'] or '—'} | {i['wall_s'] or '—'} "
        f"| {i['inference_error'] or ''} |"
        for i in s["instances"]
    )
    md = f"""# Run report — `{s['run_id']}`

Generated: {s['generated_at']}

- **Arm**: `{s['arm']}`
- **Model**: `{s['model']}` (thinking={'on' if s['thinking'] else 'off'}), label `{s['model_label']}`
{prompt_line}{demos_line}- **Dataset**: `{s['dataset']}` ({s['n_instances']} pinned instances)

## Result: **{s['solved_count']} / {s['n_instances']} solved**
{_contamination_banner(s)}
| instance_id | patch extracted | patch applied | resolved | samples | in tok | out tok | wall s | inference error |
|---|---|---|---|---|---|---|---|---|
{rows}

Resolved: {', '.join(f'`{i}`' for i in s['resolved_ids']) or '(none)'}
{_agentic_section(run_dir, s)}
## Provenance

- Config snapshot: `config.snapshot.yaml` · meta: `meta.json` · machine-readable: `summary.json`
- Predictions: `predictions.jsonl` · raw responses (incl. reasoning): `raw/`
- Exact prompts sent: `prompts/` · harness report: `eval/` · harness logs: `logs/run_evaluation/{s['run_id']}/`
"""
    out = run_dir / "report.md"
    out.write_text(md)
    return out


def write_pair_report(baseline_dir: Path, treatment_dir: Path, out_path: Path) -> Path:
    b = json.loads((baseline_dir / "summary.json").read_text())
    t = json.loads((treatment_dir / "summary.json").read_text())
    b_ids = [i["instance_id"] for i in b["instances"]]
    t_ids = [i["instance_id"] for i in t["instances"]]
    if b_ids != t_ids:
        raise ValueError("Runs cover different instance sets — not a valid pair")
    b_arm, t_arm = _arm(b), _arm(t)

    b_model = b["model_label"].split("__")[0]
    t_model = t["model_label"].split("__")[0]
    cross_model_banner = "" if b_model == t_model else (
        f"\n> ⚠️ **Cross-model comparison** (`{b_model}` vs `{t_model}`): this measures the\n"
        f"> model difference, NOT the prompt effect. For a prompt A/B, compare arms that\n"
        f"> share a model.\n")

    bi = {i["instance_id"]: i for i in b["instances"]}
    ti = {i["instance_id"]: i for i in t["instances"]}
    rows, flips = [], {"both": [], "neither": [], "treatment_only": [], "baseline_only": []}
    for iid in b_ids:
        br, tr = bi[iid]["resolved"], ti[iid]["resolved"]
        if br and tr:
            flip, key = "=", "both"
        elif not br and not tr:
            flip, key = "=", "neither"
        elif tr:
            flip, key = "📈 treatment-only", "treatment_only"
        else:
            flip, key = "📉 baseline-only", "baseline_only"
        flips[key].append(iid)
        rows.append(f"| {iid} | {_mark(br)} | {_mark(tr)} | {flip} |")

    t_prompt = (f"`{_get(t, 'prompt_version', 'fvk_prompt_version')}` "
                f"(sha256 `{(_get(t, 'prompt_sha256', 'fvk_prompt_sha256') or '')[:12]}…`)"
                if _get(t, "prompt_version", "fvk_prompt_version") else "—")
    if t.get("demos_registry"):
        t_prompt += f" + demos `{t['demos_registry']}`"
    delta = t["solved_count"] - b["solved_count"]
    md = f"""# Pair comparison — {b_arm} vs {t_arm}

Generated: {_today()}
{cross_model_banner}
| | {b_arm} | {t_arm} |
|---|---|---|
| **solved_count** | **{b['solved_count']} / {b['n_instances']}** | **{t['solved_count']} / {t['n_instances']}** |
| run_id | `{b['run_id']}` | `{t['run_id']}` |
| model | `{b['model_label']}` | `{t['model_label']}` |
| treatment prompt | — | {t_prompt} |

**solved_count_baseline = {b['solved_count']}** · **solved_count_treatment = {t['solved_count']}** · Δ = {delta:+d}

## Per-instance pairs

| instance_id | {b_arm} resolved | {t_arm} resolved | flip |
|---|---|---|---|
{chr(10).join(rows)}

- Solved by both: {len(flips['both'])} · by neither: {len(flips['neither'])}
- Solved **only by {t_arm}**: {len(flips['treatment_only'])} {flips['treatment_only'] or ''}
- Solved **only by {b_arm}**: {len(flips['baseline_only'])} {flips['baseline_only'] or ''}

With n={b['n_instances']} this is directional evidence, not statistical significance.

## Run reports

- {b_arm}: `{baseline_dir}/report.md`
- {t_arm}: `{treatment_dir}/report.md`
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    return out_path


def write_results_index(exp_root: Path = EXP_ROOT) -> Path:
    """Regenerate RESULTS.md — the one-page, shareable summary of every run.

    Fully derived from on-disk artifacts (runs/*/summary.json, reports/pair__*.md,
    gold sanity harness reports), so it is safe to re-run any time.
    """
    runs_dir, reports_dir = exp_root / "runs", exp_root / "reports"

    summaries = {}
    for sp in sorted(runs_dir.glob("*/summary.json")):
        s = json.loads(sp.read_text())
        summaries[s["run_id"]] = s

    pair_lines = []
    for pp in sorted(reports_dir.glob("pair__*__VS__*.md")):
        m = re.match(r"pair__(.+)__VS__(.+)\.md$", pp.name)
        a = summaries.get(m.group(1)) if m else None
        b = summaries.get(m.group(2)) if m else None
        if not (a and b):
            pair_lines.append(f"- [{pp.name}](reports/{pp.name})")
            continue
        subject = a["run_id"].split("__")[0]
        delta = b["solved_count"] - a["solved_count"]
        pair_lines.append(
            f"- **{_arm(a)}: {a['solved_count']}/{a['n_instances']} vs "
            f"{_arm(b)}: {b['solved_count']}/{b['n_instances']} (Δ {delta:+d})** "
            f"— `{a['model']}`, {subject} — [per-instance comparison](reports/{pp.name})")

    run_rows = []
    for s in sorted(summaries.values(),
                    key=lambda x: (x.get("model", ""),
                                   (x.get("meta") or {}).get("started_at", ""))):
        started = ((s.get("meta") or {}).get("started_at") or "")[:16].replace("T", " ")
        version = _get(s, "prompt_version", "fvk_prompt_version")
        sha = _get(s, "prompt_sha256", "fvk_prompt_sha256")
        prompt = f"`{version}` (sha `{(sha or '')[:12]}`)" if sha else "—"
        if s.get("demos_registry"):
            prompt += " +demos"
        think = " +thinking" if s.get("thinking") else ""
        run_rows.append(
            f"| [`{s['run_id']}`](runs/{s['run_id']}/report.md) | {started} | "
            f"`{s['model']}`{think} | {_arm(s)} | {prompt} | "
            f"**{s['solved_count']} / {s['n_instances']}** |")

    gold_lines = []
    for gp in sorted(runs_dir.glob("gold-sanity__*/eval/gold.*.json")):
        g = json.loads(gp.read_text())
        gold_lines.append(f"- `{gp.parent.parent.name}` — gold patches resolved "
                          f"**{g.get('resolved_instances')}/{g.get('total_instances')}**")

    md = f"""# FVK experiment results

A/B comparison: does injecting a distilled [formal-verification-kit](https://github.com/grosu/formal-verification-kit)
methodology prompt (formalize the program, verify the fix against the spec, then patch —
see [prompts/fvk/](prompts/fvk/)) change DeepSeek's solve rate on SWE-bench?

Setting: one-shot **oracle** prompting (issue + relevant source files → unified-diff patch),
official SWE-bench docker harness; **solved** = all FAIL_TO_PASS + PASS_TO_PASS tests pass.
Both arms always share model, instances, and sampling config — the only difference is the
FVK system prompt. Methodology details and caveats: [DESIGN.md](DESIGN.md).

_Last regenerated: {_today()} (auto-generated — `run.py results` to refresh)._

## Pair comparisons

{chr(10).join(pair_lines) or '_none yet_'}

## All runs

| run | started (UTC) | model | arm | prompt | solved |
|---|---|---|---|---|---|
{chr(10).join(run_rows) or '| _none yet_ | | | | | |'}

## Environment sanity (gold-patch) runs

{chr(10).join(gold_lines) or '_none yet_'}

## Reading the numbers

- Model diffs are mechanically normalized (hunk-header recount only, identical for both
  arms) before evaluation; unnormalized originals sit in each run's
  `predictions.pre-normalize.jsonl`. A patch that still fails to apply counts as unsolved.
- Infra failures (e.g. docker pull errors) are auto-retried and never silently counted —
  every verdict comes from an executed test run.
- Small-n runs are directional evidence, not statistical significance.
"""
    out = exp_root / "RESULTS.md"
    out.write_text(md)
    return out
