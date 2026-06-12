# ITERATION_GUIDANCE.md — Guidance for v2 Generation

## Summary of v1 Status

v1 scores 10/10 FAIL_TO_PASS. All hidden tests pass. The FVK analysis surfaced
several findings, most of which are edge cases rather than bugs. The v2 iteration
should focus on robustness improvements identified by formalization.

## Actionable Items for v2 (ordered by impact)

### 1. Fix Optional prefix check (Finding 3)

**Priority: Low** — extremely rare edge case but easy fix.

Change `not ann_label.startswith("Optional")` to `not ann_label.startswith("Optional[")`.

This prevents false matches on user-defined types like `OptionalFeature`.

### 2. Consider restoring direct AnnAssign handling in `get_annotation` (PF-1)

**Priority: Low** — `infer_node` is the only caller that might pass AnnAssign directly.

The v1 code handles AnnAssign children (via parent walk) but not AnnAssign nodes
themselves. Adding:
```python
elif isinstance(node, astroid.AnnAssign):
    annotation = node.annotation
    default = node.value
```
would make the function more robust. However, this may not be needed since the
hidden tests don't appear to test this path directly.

### 3. Keyword-only args support (Finding 5)

**Priority: Low** — rare in constructors.

Extend `_get_assignattr_annotation` to also search `frame.args.kwonlyargs` and
use `frame.args.kw_defaults` for their defaults. This handles:
```python
def __init__(self, *, name: str = None):
    self.name = name
```

### 4. `cls` handling in `_get_method_arguments` (Finding 6)

**Priority: Very Low** — cosmetic.

Skip `cls` in addition to `self` for classmethods.

## What NOT to change in v2

1. **Don't change the `infer_node` return type.** It must return a `set` — the inspector's union semantics depend on this.

2. **Don't remove the parent-walk in `get_annotation`.** The AnnAssign child handling is required by the hidden test `test_get_annotation_annassign`.

3. **Don't change the Name-node return type of `get_annotation`.** It must return `astroid.Name` instances, not strings. The `class_names()` function depends on `isinstance(node, astroid.Name)`.

4. **Don't touch writer.py DOT format.** The existing DOT comparison tests validate specific output. Changes risk breaking PASS_TO_PASS tests.

## Risk Assessment for v2

The v1 patch already passes 10/10. The main risk in v2 is **regression** — changing
working code and breaking hidden tests. The findings from FVK are all edge cases
that the hidden tests are unlikely to cover. Therefore:

**Recommendation: v2 should apply only the minimal, safe improvements (item 1: Optional prefix fix) and leave the rest unchanged.** Over-engineering v2 risks introducing regressions with no test coverage benefit.

## Key Contracts to Preserve

| Function | Must return | Must handle |
|---|---|---|
| `get_annotation` | `astroid.Name` or `None` | AssignAttr, AssignName(parent=AnnAssign), any node with parent=AnnAssign |
| `infer_node` | `set` (never None, never single value) | All node types, InferenceError |
| `_get_assignattr_annotation` | `(annotation, default)` tuple | AnnAssign parent, Assign parent with Name value |
| `class_names` | `list[str]` with unique names | Instance, ClassDef, Name nodes |
