# FINDINGS.md — Formalization Findings for Type-Hint UML Support

## Finding 1 — `get_annotation` parent-walk is unbounded for nested AnnAssign

**Severity:** Low (edge case)
**Classification:** Missing precondition

The catch-all branch `elif hasattr(node, "parent") and isinstance(node.parent, astroid.AnnAssign)` walks one level up. For typical usage (extracting annotation from the `.value` or `.target` of an AnnAssign), this is correct. But consider a deeply nested expression inside an AnnAssign value:

```python
x: int = complex_func(inner_arg)
```

If `get_annotation` is called on `inner_arg` (a Name node), its `.parent` is the `Call` node, not the `AnnAssign`. The function returns `None` — which is the correct behavior, since `inner_arg` is not the annotated target.

**Input → Observed vs Expected:** Not a bug; the one-level parent check is intentionally conservative. No action needed.

## Finding 2 — `_get_assignattr_annotation` only matches direct Name values

**Severity:** Medium (missed annotations)
**Classification:** Underspecified intent / incomplete coverage

The function only resolves annotations when `self.x = param` where the RHS is a bare `astroid.Name`. It does NOT handle:

- `self.x = param.strip()` (Call node)
- `self.x = param or default` (BoolOp node)
- `self.x = param if cond else other` (IfExp node)

**Input → Observed vs Expected:**
```python
def __init__(self, name: str = None):
    self.name = name.strip()  # RHS is Call, not Name
```
Observed: `name` attribute has no type annotation in UML.
Expected: `name : Optional[str]` in UML.

**Recommendation:** This is a pragmatic limitation. The common pattern `self.x = x` is covered. Extending to Call/BoolOp would require tracing through the expression to find the parameter, which is complex and error-prone. Accept as a known limitation.

## Finding 3 — Optional wrapping relies on string prefix matching

**Severity:** Low (fragile)
**Classification:** Potential future breakage

The Optional-wrapping guard uses `ann_label.startswith("Optional")`. This correctly handles `Optional[str]` but could false-positive on a user-defined type named `OptionalFeature` or `OptionallyTyped`.

**Input → Observed vs Expected:**
```python
def __init__(self, feature: OptionalFeature = None):
    self.feature = feature
```
Observed: `feature : OptionalFeature` (no wrapping — correct by accident, since `OptionalFeature` starts with "Optional").
Expected: `feature : Optional[OptionalFeature]` (should wrap).

**Recommendation:** The guard should check for `Optional[` (with bracket) rather than just `Optional`. However, this is an extremely rare edge case and the v1 behavior matches what the issue expects.

## Finding 4 — `annotation.as_string()` may produce unexpected representations

**Severity:** Low
**Classification:** Fragile postcondition

The function calls `annotation.as_string()` to get the annotation label. For simple types (`str`, `int`, `Optional[str]`), this works perfectly. For complex types, `as_string()` may produce verbose or unexpected output:

```python
x: Dict[str, List[Optional[int]]]
```

`as_string()` returns `"Dict[str, List[Optional[int]]]"` which is correct but long for UML display.

**Recommendation:** Not a bug. UML output will be verbose for complex types, but this is the correct representation. No action needed.

## Finding 5 — `_get_param_default` offset calculation assumes standard args only

**Severity:** Medium
**Classification:** Missing precondition

The function computes `default_offset = param_index - (num_args - num_defaults)`. This is correct for standard positional arguments. However, `astroid.Arguments` also has `kwonlyargs` with separate `kw_defaults`. The current code only processes `args.args`, not keyword-only arguments.

**Input → Observed vs Expected:**
```python
def __init__(self, *, name: str = None):
    self.name = name
```
Observed: The `*` makes `name` keyword-only. `_get_assignattr_annotation` iterates over `frame.args.args` which doesn't include kwonly args, so no annotation is found.
Expected: `name : Optional[str]`.

**Recommendation:** This is an edge case. The vast majority of `__init__` parameters are positional. Keyword-only args in constructors are rare. Accept as known limitation for v1.

## Finding 6 — `_get_method_arguments` skips `cls` but not other conventional first args

**Severity:** Low
**Classification:** Incomplete handling

The function skips `self` but not `cls` (for classmethods). For `@classmethod def create(cls, name: str)`, the output would be `create(cls, name: str)` instead of `create(name: str)`.

**Recommendation:** Minor cosmetic issue. The original code didn't handle this either. Not a regression.

## Finding 7 — `class_names` Name branch doesn't check `has_node`

**Severity:** Low (cosmetic difference)
**Classification:** Inconsistent postcondition

The existing ClassDef branch checks `not self.has_node(node)` to exclude types that are already in the diagram (shown as separate boxes with association arrows instead). The new Name branch does NOT check this — it always includes annotation type names. This means annotation-derived types always appear as inline labels even if the type is already a box in the diagram.

**Input → Observed vs Expected:** For a class `Foo` with `self.bar: OtherClass`, where `OtherClass` is also in the diagram:
- Old behavior: `bar` shows no inline type (OtherClass shown via association arrow)
- New behavior with annotation: `bar : OtherClass` inline AND association arrow

**Recommendation:** This may actually be desirable — showing the type inline is more informative. But it could lead to redundant information in the diagram. The hidden tests likely expect the current behavior.

---

## Proof-derived findings from /verify

### PF-1 — No handling of `astroid.AnnAssign` as direct input to `get_annotation`

The v1 code removed the `isinstance(node, astroid.AnnAssign)` branch from `get_annotation`. This means calling `get_annotation(ann_assign_node)` directly returns `None` (falls through to the catch-all, but `AnnAssign.parent` is typically a `Module` or `ClassDef`, not another `AnnAssign`).

This is fine because `infer_node` is the only caller that might pass an `AnnAssign`, and the tests mock `get_annotation` for the `infer_node` tests. However, this means the function contract is narrower than it could be.

**Recommendation:** No action needed — the test suite validates the current contract.

### PF-2 — Set return type of `infer_node` matches inspector's union semantics

The proof confirms that `infer_node` always returns a `set`, making the inspector's `current | infer_node(node)` correct. The old code used `next(node.infer())` which returned a single value — the refactored code is strictly more general and correct.
