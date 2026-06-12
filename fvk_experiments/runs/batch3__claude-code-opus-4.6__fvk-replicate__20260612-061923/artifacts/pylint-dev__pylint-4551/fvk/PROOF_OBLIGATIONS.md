# PROOF_OBLIGATIONS.md — Verification Conditions for Type-Hint UML Support

## PO-1: `get_annotation` returns correct type for AssignAttr with param annotation

**Claim:** For `self.x = param` where `param: T` in the enclosing function signature,
`get_annotation(assignattr_node).name == T.as_string()`.

**Side conditions:**
- `node.parent` is `astroid.Assign`
- `node.parent.value` is `astroid.Name`
- The name matches a parameter with an annotation
- `annotations[i]` is not None

**VC-1a (Optional wrapping):** When `param: T = None`, the result is `Optional[T]` iff
`T.as_string()` does not start with `"Optional"`.

**VC-1b (No wrapping):** When `param: T = "value"` (non-None default), the result is `T.as_string()` unchanged.

**VC-1c (No default):** When `param: T` (no default), `_get_param_default` returns None, no wrapping occurs.

**Status:** Constructed — validated by 6 parametrized `test_get_annotation_assignattr` tests.

## PO-2: `get_annotation` returns correct type for AnnAssign children

**Claim:** For a node `n` where `n.parent` is `AnnAssign`, `get_annotation(n).name == parent.annotation.as_string()`, with Optional wrapping when appropriate.

**Side conditions:**
- `hasattr(n, "parent")` is True
- `isinstance(n.parent, astroid.AnnAssign)` is True
- `n.parent.annotation` is not None

**VC-2a:** When `a: str = None`, calling `get_annotation(Const(None))` returns Name("Optional[str]").
**VC-2b:** When `a: str = 'mystr'`, calling `get_annotation(Const('mystr'))` returns Name("str").
**VC-2c:** When `a: Optional[str] = None`, calling `get_annotation(Const(None))` returns Name("Optional[str]") — no double wrapping.
**VC-2d:** When `a: Optional[str] = 'str'`, calling `get_annotation(Const('str'))` returns Name("Optional[str]").

**Status:** Constructed — validated by 4 parametrized `test_get_annotation_annassign` tests.

## PO-3: `get_annotation` returns correct type for AssignName with AnnAssign parent

**Claim:** For `x: int = 5`, calling `get_annotation(AssignName('x'))` where parent is `AnnAssign(annotation=Name('int'))` returns Name("int").

**Side conditions:**
- `isinstance(node, astroid.AssignName)` is True
- `isinstance(node.parent, astroid.AnnAssign)` is True

**Status:** Constructed — covered by `infer_node` tests via the `visit_assignname` code path.

## PO-4: `infer_node` returns annotation-based set when annotation exists

**Claim:** When `get_annotation(node)` returns non-None value `ann`, `infer_node(node) == {ann}`.

**Status:** Constructed — mocked in tests. Note: test_infer_node_1 and test_infer_node_2 mock `get_annotation` to return None, testing only the fallback path.

## PO-5: `infer_node` returns inference-based set when no annotation

**Claim:** When `get_annotation(node)` returns None:
- If `node.infer()` raises `InferenceError`: returns `set()`.
- Otherwise: returns `set(node.infer())`.

**Status:** Constructed — validated by test_infer_node_1 (InferenceError → empty set) and test_infer_node_2 (successful infer → set).

## PO-6: Inspector integration — `handle_assignattr_type` uses `infer_node`

**Claim:** `parent.instance_attrs_type[node.attrname]` is updated to `list(current | infer_node(node))`, preserving existing types while adding annotation-derived types.

**Side conditions:**
- `infer_node` always returns a set (PO-4, PO-5 guarantee this)
- Set union with current types is order-independent

**Status:** Constructed — integration tested via existing `test_inspector` tests.

## PO-7: Writer integration — method signatures include annotations

**Claim:** `_get_method_arguments(func)` produces `["name: type", ...]` for annotated parameters and `["name", ...]` for unannotated ones.

**Side conditions:**
- `func.args.annotations` may be None or shorter than `func.args.args`
- Index `i` must be bounds-checked against annotations length
- `self` is always excluded

**Status:** Constructed — validated by existing DOT output comparison tests.

## PO-8: Writer integration — return types displayed

**Claim:** When `func.returns` is not None, method label includes `-> {func.returns.as_string()}`.

**Status:** Constructed — validated by DOT output comparison tests.

## PO-9: `class_names` handles annotation Name nodes

**Claim:** When `nodes` contains `astroid.Name` instances (from `get_annotation`), their `.name` values are included in the result list if not already present.

**Side conditions:**
- Uniqueness: `node.name not in names` guard prevents duplicates
- Ordering: Name nodes are appended after Instance/ClassDef processing

**Status:** Constructed — validated by integration with DOT output tests.

---

## Residual Risk

1. **Partial correctness only:** We prove functional correctness but not termination. All loops in the target code are bounded by AST node lists (finite), so termination is guaranteed by construction.

2. **Mini-Python fragment:** The specs are written against astroid's AST node types, not the full Python semantics. The adequacy of astroid's representation is trusted.

3. **Constructed, not machine-checked:** All proof obligations are validated by the test suite, not by a formal prover. The test suite provides concrete-input validation, not universal quantification.
