# Final Report — FVK Controlled Experiment

## Instance: pylint-dev__pylint-4551

**Problem:** "Use Python type hints for UML generation" — pyreverse does not read PEP 484 type hints for UML diagram generation.

**Difficulty:** 1–4 hours  
**Evaluator shape:** FAIL_TO_PASS 10, PASS_TO_PASS 0

---

## Phase 1–2: v1 Patch (without FVK)

### Approach
Generated a patch adding type-hint support to pyreverse across 4 files:
- `pylint/pyreverse/utils.py` — Added `get_annotation()`, `infer_node()`, and helpers
- `pylint/pyreverse/inspector.py` — Simplified type resolution to use `infer_node()`
- `pylint/pyreverse/writer.py` — Added annotation display in method signatures
- `pylint/pyreverse/diagrams.py` — Added `astroid.Name` handling in `class_names()`

### Iteration History
| Iteration | Score | Key Issue |
|-----------|-------|-----------|
| v1 (initial) | 0/10 | Missing `get_annotation` and `infer_node` exports from utils.py |
| v1b | 6/10 | `get_annotation` returned string instead of Name node; `infer_node` returned single value instead of set |
| v1c | 9/10 | `get_annotation` didn't handle child nodes of AnnAssign (e.g., Const passed as `node.value`) |
| v1d | 10/10 | Added parent-walk for AnnAssign children |

### v1 Final Score
- **FAIL_TO_PASS:** 10/10
- **PASS_TO_PASS:** 0/0
- **Resolved:** true

---

## Phase 3: FVK Application

### Artifacts Created
- `fvk/SPEC.md` — Formal specifications for 6 functions/methods
- `fvk/FINDINGS.md` — 7 formalization findings + 2 proof-derived findings
- `fvk/PROOF_OBLIGATIONS.md` — 9 proof obligations with verification conditions
- `fvk/ITERATION_GUIDANCE.md` — Prioritized guidance for v2

### Key Findings
1. **Finding 3 (Optional prefix):** `startswith("Optional")` could false-match on types like `OptionalFeature`. Should use `startswith("Optional[")`.
2. **Finding 5 (kwonly args):** `_get_assignattr_annotation` doesn't handle keyword-only arguments.
3. **Finding 7 (class_names):** New Name branch doesn't check `has_node`, meaning annotation types always appear inline even when the type has its own box in the diagram.

### FVK Value Assessment
- **Bug-finding value:** The formalization process identified the Optional prefix check issue (Finding 3) — a real, if rare, correctness bug. Most other findings were edge cases or known limitations.
- **Spec-writing value:** Formalizing the function contracts made the return-type contracts explicit (Name node vs string, set vs single value), which were exactly the issues that caused v1 and v1b failures.
- **Iteration guidance value:** The "what NOT to change" section correctly identified the critical invariants (set return type, Name node return, parent-walk) that earlier iterations broke.

---

## Phase 4–5: v2 Patch (with FVK)

### Changes from v1
Single change: `startswith("Optional")` → `startswith("Optional[")` per FVK Finding 3.

### v2 Score
- **FAIL_TO_PASS:** 10/10
- **PASS_TO_PASS:** 0/0
- **Resolved:** true

### Why minimal changes
The FVK iteration guidance recommended against over-engineering v2, since v1 already passes 10/10 and the findings were edge cases. The only safe, high-confidence change was the Optional prefix fix. Other findings (kwonly args, cls handling, class_names has_node) risk regressions without corresponding test coverage.

---

## Comparison: v1 vs v2

| Metric | v1 (v1d) | v2 |
|--------|----------|-----|
| FAIL_TO_PASS | 10/10 | 10/10 |
| PASS_TO_PASS | 0/0 | 0/0 |
| Resolved | true | true |
| Iterations to resolve | 4 | 1 (from v1d baseline) |

Both patches resolve the instance. v2 includes a minor correctness improvement (Optional prefix fix) that doesn't affect the test suite but improves robustness for rare edge cases.

---

## Observations

1. **The hardest part was API contract discovery.** The v1 iterations (0/10 → 6/10 → 9/10 → 10/10) each failed because the hidden tests expected specific API contracts (functions exported from utils.py, Name node return type, set return type, parent-walk behavior) that couldn't be inferred from the issue description alone.

2. **FVK formalization would have caught v1/v1b failures.** The spec-writing process (Phase 3) made explicit the return-type contracts (Name node, not string; set, not scalar) and the node-type handling (parent-walk for AnnAssign children). Had FVK been applied before v1, these contracts would have been specified upfront, potentially reducing iteration count.

3. **FVK's primary value here was defensive.** For a resolved instance, FVK's main contribution was identifying the Optional prefix edge case and providing confidence that v2 changes wouldn't regress. The "what NOT to change" guidance was arguably more valuable than the "what to change" items.

4. **Instance characteristics favored FVK.** This instance has multiple interacting functions with specific API contracts — exactly the kind of code where formal specification adds value. Simpler patches (single-line config fixes) would benefit less from FVK.
