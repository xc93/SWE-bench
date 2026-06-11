# FVK experiment results

A/B comparison: does injecting a distilled [formal-verification-kit](https://github.com/grosu/formal-verification-kit)
methodology prompt (formalize the program, verify the fix against the spec, then patch —
see [prompts/fvk/](prompts/fvk/)) change DeepSeek's solve rate on SWE-bench?

Setting: one-shot **oracle** prompting (issue + relevant source files → unified-diff patch),
official SWE-bench docker harness; **solved** = all FAIL_TO_PASS + PASS_TO_PASS tests pass.
Both arms always share model, instances, and sampling config — the only difference is the
FVK system prompt. Methodology details and caveats: [DESIGN.md](DESIGN.md).

_Last regenerated: 2026-06-11 06:19 UTC (auto-generated — `run.py results` to refresh)._

## Pair comparisons

- **baseline: 8/10 vs baseline-replicate-v7: 8/10 (Δ +0)** — `codex-5.5`, astropy10 — [per-instance comparison](reports/pair__astropy10__codex-5.5-xhigh__baseline__20260611-042659__VS__astropy10__codex-5.5-xhigh__baseline-replicate-v7__20260611-055642.md)
- **baseline: 8/10 vs fvk-v4: 7/10 (Δ -1)** — `codex-5.5`, astropy10 — [per-instance comparison](reports/pair__astropy10__codex-5.5-xhigh__baseline__20260611-042659__VS__astropy10__codex-5.5-xhigh__fvk-v4__20260611-042702.md)
- **baseline: 8/10 vs jointembed-v6: 9/10 (Δ +1)** — `codex-5.5`, astropy10 — [per-instance comparison](reports/pair__astropy10__codex-5.5-xhigh__baseline__20260611-042659__VS__astropy10__codex-5.5-xhigh__jointembed-v6__20260611-044734.md)
- **baseline: 8/10 vs review-v5: 5/10 (Δ -3)** — `codex-5.5`, astropy10 — [per-instance comparison](reports/pair__astropy10__codex-5.5-xhigh__baseline__20260611-042659__VS__astropy10__codex-5.5-xhigh__review-v5__20260611-044140.md)
- **baseline: 3/10 vs fvk-v1: 4/10 (Δ +1)** — `deepseek-v4-flash`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-flash-think__baseline__20260610-092805__VS__astropy10__ds-v4-flash-think__fvk-v1__20260610-094051.md)
- **baseline: 3/10 vs fvk-v2: 3/10 (Δ +0)** — `deepseek-v4-flash`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-flash-think__baseline__20260610-092805__VS__astropy10__ds-v4-flash-think__fvk-v2__20260610-111221.md)
- **baseline: 3/10 vs fvk-v3: 3/10 (Δ +0)** — `deepseek-v4-flash`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-flash-think__baseline__20260610-092805__VS__astropy10__ds-v4-flash-think__fvk-v3__20260610-113837.md)
- **baseline: 2/10 vs baseline-replicate-v7: 2/10 (Δ +0)** — `deepseek-v4-pro`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-pro-think__baseline__20260610-115611__VS__astropy10__ds-v4-pro-think__baseline-replicate-v7__20260610-143959.md)
- **baseline: 2/10 vs fvk-v1: 4/10 (Δ +2)** — `deepseek-v4-pro`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-pro-think__baseline__20260610-115611__VS__astropy10__ds-v4-pro-think__fvk-v1__20260610-120532.md)
- **baseline: 2/10 vs fvk-v2: 4/10 (Δ +2)** — `deepseek-v4-pro`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-pro-think__baseline__20260610-115611__VS__astropy10__ds-v4-pro-think__fvk-v2__20260610-122143.md)
- **baseline: 2/10 vs fvk-v3: 2/10 (Δ +0)** — `deepseek-v4-pro`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-pro-think__baseline__20260610-115611__VS__astropy10__ds-v4-pro-think__fvk-v3__20260610-123129.md)
- **baseline: 2/10 vs fvk-v4: 4/10 (Δ +2)** — `deepseek-v4-pro`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-pro-think__baseline__20260610-115611__VS__astropy10__ds-v4-pro-think__fvk-v4__20260610-125349.md)
- **baseline: 2/10 vs jointembed-v6: 4/10 (Δ +2)** — `deepseek-v4-pro`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-pro-think__baseline__20260610-115611__VS__astropy10__ds-v4-pro-think__jointembed-v6__20260610-141549.md)
- **baseline: 2/10 vs review-v5: 3/10 (Δ +1)** — `deepseek-v4-pro`, astropy10 — [per-instance comparison](reports/pair__astropy10__ds-v4-pro-think__baseline__20260610-115611__VS__astropy10__ds-v4-pro-think__review-v5__20260610-130805.md)

## All runs

| run | started (UTC) | model | arm | prompt | solved |
|---|---|---|---|---|---|
| [`astropy10__codex-5.5-xhigh__baseline__20260611-042659`](runs/astropy10__codex-5.5-xhigh__baseline__20260611-042659/report.md) | 2026-06-11 04:27 | `codex-5.5` | baseline | — | **8 / 10** |
| [`astropy10__codex-5.5-xhigh__fvk-v4__20260611-042702`](runs/astropy10__codex-5.5-xhigh__fvk-v4__20260611-042702/report.md) | 2026-06-11 04:27 | `codex-5.5` | fvk-v4 | `v4` (sha `e9d27c533914`) | **7 / 10** |
| [`astropy10__codex-5.5-xhigh__review-v5__20260611-044140`](runs/astropy10__codex-5.5-xhigh__review-v5__20260611-044140/report.md) | 2026-06-11 04:41 | `codex-5.5` | review-v5 | `v5` (sha `09becca148f3`) | **5 / 10** |
| [`astropy10__codex-5.5-xhigh__jointembed-v6__20260611-044734`](runs/astropy10__codex-5.5-xhigh__jointembed-v6__20260611-044734/report.md) | 2026-06-11 04:47 | `codex-5.5` | jointembed-v6 | `v6` (sha `ad1565f39207`) +demos | **9 / 10** |
| [`astropy10__codex-5.5-xhigh__baseline-replicate-v7__20260611-055642`](runs/astropy10__codex-5.5-xhigh__baseline-replicate-v7__20260611-055642/report.md) | 2026-06-11 05:56 | `codex-5.5` | baseline-replicate-v7 | — | **8 / 10** |
| [`astropy10__ds-v4-flash-think__baseline__20260610-092805`](runs/astropy10__ds-v4-flash-think__baseline__20260610-092805/report.md) | 2026-06-10 09:52 | `deepseek-v4-flash` +thinking | baseline | — | **3 / 10** |
| [`astropy10__ds-v4-flash-think__fvk-v1__20260610-094051`](runs/astropy10__ds-v4-flash-think__fvk-v1__20260610-094051/report.md) | 2026-06-10 09:53 | `deepseek-v4-flash` +thinking | fvk-v1 | `v1` (sha `540c2ababb8c`) | **4 / 10** |
| [`astropy10__ds-v4-flash-think__fvk-v2__20260610-111221`](runs/astropy10__ds-v4-flash-think__fvk-v2__20260610-111221/report.md) | 2026-06-10 11:12 | `deepseek-v4-flash` +thinking | fvk-v2 | `v2` (sha `8c8f31b1e7b2`) | **3 / 10** |
| [`astropy10__ds-v4-flash-think__fvk-v3__20260610-113837`](runs/astropy10__ds-v4-flash-think__fvk-v3__20260610-113837/report.md) | 2026-06-10 11:38 | `deepseek-v4-flash` +thinking | fvk-v3 | `v3` (sha `8e64c5149c8c`) | **3 / 10** |
| [`astropy10__ds-v4-pro-think__baseline__20260610-115611`](runs/astropy10__ds-v4-pro-think__baseline__20260610-115611/report.md) | 2026-06-10 11:56 | `deepseek-v4-pro` +thinking | baseline | — | **2 / 10** |
| [`astropy10__ds-v4-pro-think__fvk-v1__20260610-120532`](runs/astropy10__ds-v4-pro-think__fvk-v1__20260610-120532/report.md) | 2026-06-10 12:05 | `deepseek-v4-pro` +thinking | fvk-v1 | `v1` (sha `540c2ababb8c`) | **4 / 10** |
| [`astropy10__ds-v4-pro-think__fvk-v2__20260610-122143`](runs/astropy10__ds-v4-pro-think__fvk-v2__20260610-122143/report.md) | 2026-06-10 12:22 | `deepseek-v4-pro` +thinking | fvk-v2 | `v2` (sha `8c8f31b1e7b2`) | **4 / 10** |
| [`astropy10__ds-v4-pro-think__fvk-v3__20260610-123129`](runs/astropy10__ds-v4-pro-think__fvk-v3__20260610-123129/report.md) | 2026-06-10 12:31 | `deepseek-v4-pro` +thinking | fvk-v3 | `v3` (sha `8e64c5149c8c`) | **2 / 10** |
| [`astropy10__ds-v4-pro-think__fvk-v4__20260610-125349`](runs/astropy10__ds-v4-pro-think__fvk-v4__20260610-125349/report.md) | 2026-06-10 12:54 | `deepseek-v4-pro` +thinking | fvk-v4 | `v4` (sha `e9d27c533914`) | **4 / 10** |
| [`astropy10__ds-v4-pro-think__review-v5__20260610-130805`](runs/astropy10__ds-v4-pro-think__review-v5__20260610-130805/report.md) | 2026-06-10 13:08 | `deepseek-v4-pro` +thinking | review-v5 | `v5` (sha `09becca148f3`) | **3 / 10** |
| [`astropy10__ds-v4-pro-think__jointembed-v6__20260610-141549`](runs/astropy10__ds-v4-pro-think__jointembed-v6__20260610-141549/report.md) | 2026-06-10 14:16 | `deepseek-v4-pro` +thinking | jointembed-v6 | `v6` (sha `ad1565f39207`) | **4 / 10** |
| [`astropy10__ds-v4-pro-think__baseline-replicate-v7__20260610-143959`](runs/astropy10__ds-v4-pro-think__baseline-replicate-v7__20260610-143959/report.md) | 2026-06-10 14:40 | `deepseek-v4-pro` +thinking | baseline-replicate-v7 | — | **2 / 10** |

## Environment sanity (gold-patch) runs

- `gold-sanity__astropy10__ds-v4-flash-think__baseline__20260610-092803` — gold patches resolved **10/10**

## Reading the numbers

- Model diffs are mechanically normalized (hunk-header recount only, identical for both
  arms) before evaluation; unnormalized originals sit in each run's
  `predictions.pre-normalize.jsonl`. A patch that still fails to apply counts as unsolved.
- Infra failures (e.g. docker pull errors) are auto-retried and never silently counted —
  every verdict comes from an executed test run.
- Small-n runs are directional evidence, not statistical significance.
