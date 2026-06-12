# SPEC.md — Formal Specification of Type-Hint UML Support

## Intent (from issue pylint-dev__pylint-4551)

Pyreverse should read Python PEP 484 type hints and use them for UML generation.
Given `class C: def __init__(self, a: str = None): self.a = a`, the UML output
should display `a : str` (or `a : Optional[str]`) instead of showing no type.

The change touches five subsystems: annotation extraction, type inference,
instance-attribute resolution, local-variable resolution, and writer output.

---

## Function Contracts

### 1. `get_annotation(node) -> Optional[astroid.Name]`

**Domain:** `node` is any astroid AST node.

**Precondition:** `node` is one of:
- `astroid.AssignAttr` (e.g., `self.x = param`)
- `astroid.AssignName` whose `.parent` is `astroid.AnnAssign`
- Any node whose `.parent` is `astroid.AnnAssign` (e.g., the `.value` child)

**Postcondition:**
- If annotation is found: returns `astroid.Name` with `.name` equal to the annotation's `.as_string()` representation.
- If annotation is found AND default value is `Const(None)` AND annotation label does not start with `"Optional"`: `.name` is wrapped as `"Optional[{label}]"`.
- If no annotation is found (no matching pattern, or annotation is None): returns `None`.

**Formal contract (pseudo-K):**
```
claim <get_annotation>
  requires: node ∈ {AssignAttr, AssignName(parent=AnnAssign), *(parent=AnnAssign)}
  ensures:  result.name == wrap_optional(annotation.as_string(), default)
            WHERE wrap_optional(label, default) =
              IF default is Const(None) AND NOT label.startswith("Optional")
              THEN "Optional[" + label + "]"
              ELSE label
```

### 2. `infer_node(node) -> Set`

**Domain:** `node` is any astroid AST node.

**Precondition:** None (handles all node types).

**Postcondition:**
- If `get_annotation(node)` returns non-None `ann`: returns `{ann}` (singleton set).
- Else if `node.infer()` succeeds: returns `set(node.infer())`.
- Else (InferenceError): returns `set()` (empty set).

**Formal contract:**
```
claim <infer_node>
  requires: True
  ensures:  result == IF get_annotation(node) != None
                      THEN {get_annotation(node)}
                      ELSE try_set(node.infer()) or set()
```

### 3. `_get_assignattr_annotation(node) -> Tuple[Optional[Node], Optional[Node]]`

**Domain:** `node` is `astroid.AssignAttr`.

**Precondition:** `node` is an `AssignAttr` inside an `__init__` method body.

**Postcondition:** Returns `(annotation, default)` where:
- Case 1 (AnnAssign parent): `node.parent` is `AnnAssign` -> `(parent.annotation, parent.value)`
- Case 2 (Assign parent, value is Name matching a parameter): Finds the matching parameter in the enclosing `FunctionDef.args`, returns `(param_annotation, param_default)`.
- Case 3 (no match): returns `(None, None)`.

### 4. `_get_param_default(args_node, param_index) -> Optional[Node]`

**Domain:** `args_node` is `astroid.Arguments`, `param_index` is `int >= 0`.

**Precondition:** `0 <= param_index < len(args_node.args)`.

**Postcondition:**
- If `args_node.defaults` is empty or `param_index` has no corresponding default: returns `None`.
- Otherwise: returns `defaults[param_index - (num_args - num_defaults)]`.

**Side condition:** `default_offset = param_index - (num_args - num_defaults)`. This is valid because Python aligns defaults right-to-left with parameters.

### 5. `_get_method_arguments(func) -> List[str]`

**Domain:** `func` is `astroid.FunctionDef`.

**Postcondition:** Returns list of strings, one per non-self argument:
- If the argument has an annotation at index `i`: `"{arg.name}: {annotations[i].as_string()}"`.
- Otherwise: `"{arg.name}"`.

### 6. `class_names(nodes)` (modified)

**Domain:** `nodes` is a list of astroid nodes.

**Postcondition (extended):** In addition to existing Instance/ClassDef handling, if a node is `astroid.Name` and `node.name` is not already in the result list, appends `node.name`. This enables annotation-derived type names to appear in UML attribute labels.

---

## Invariants

1. **Annotation priority:** Annotations always take precedence over inference. If `get_annotation` returns non-None, `infer_node` uses it; the old inference path is only a fallback.
2. **Optional wrapping idempotence:** `Optional[Optional[str]]` is prevented by the `startswith("Optional")` guard.
3. **Set semantics:** `infer_node` always returns a `set`, never a single value or None. The inspector merges via set union (`current | infer_node(node)`).
4. **Name node contract:** `get_annotation` returns `astroid.Name` instances (not strings), so `class_names()` can handle them uniformly with its `isinstance(node, astroid.Name)` branch.
