# v1 Notes

## What behavior v1 changes

v1 adds support for Python type hints (PEP 484) in pyreverse UML generation by adding two utility functions and integrating them into the existing inspector and diagram pipeline.

### Key additions:

1. **`get_annotation(node)` in `utils.py`**: Extracts type annotation information from AST nodes:
   - For values in `AnnAssign` statements: reads the annotation from the parent node
   - For `AssignAttr` nodes (e.g., `self.x = x`): looks up the corresponding function parameter annotation
   - Handles `Optional` wrapping: when the default value is `None`, wraps the annotation type in `Optional[...]`
   - Returns an `_AnnotationLabel` object with `.name` attribute containing the annotation string

2. **`infer_node(node)` in `utils.py`**: Replaces direct `node.infer()` calls:
   - First checks for annotation via `get_annotation`
   - Falls back to `node.infer()` if no annotation
   - Returns `set()` on `InferenceError` (instead of propagating the exception)

3. **Inspector changes**: `handle_assignattr_type` and `visit_assignname` now use `infer_node` instead of direct inference

4. **Diagram changes**: `class_names` now handles annotation label objects (non-ClassDef nodes with `.name` attribute)

## Files modified

1. `pylint/pyreverse/utils.py` — Added `_AnnotationLabel` class, `get_annotation()`, `infer_node()`, and `import astroid`
2. `pylint/pyreverse/inspector.py` — Modified `handle_assignattr_type` and `visit_assignname` to use `utils.infer_node`
3. `pylint/pyreverse/diagrams.py` — Modified `class_names` to handle annotation label objects

## Public tests run

All 23 existing pyreverse tests pass:
- `tests/unittest_pyreverse_inspector.py` — 8 passed
- `tests/unittest_pyreverse_writer.py` — 6 passed
- `tests/unittest_pyreverse_diadefs.py` — 9 passed

## Why v1 matches the public issue

The issue requests that pyreverse read Python type hints for UML generation. v1 adds:
- Function parameter annotation propagation to instance attributes
- Direct annotation reading from AnnAssign nodes
- Automatic Optional wrapping when default is None
- Fallback to inference when no annotation is available
