# v1 Notes

## Behavior Change
v1 adds Python type hint support to pyreverse UML generation:

1. **Instance attribute types from parameter annotations**: When `self.x = param` and `param` has a type annotation (e.g., `param: str`), the annotation type is used for the attribute in UML output.
2. **Instance attribute types from AnnAssign**: When `self.x: int = 5`, the annotation type is used.
3. **Class-level annotation types**: When `x: int = 5` or `y: str` at class level, the annotation type is used.
4. **Method parameter annotations in output**: Method signatures now include parameter type annotations (e.g., `method(a: str, b: int)`).
5. **Return type annotations in output**: Method signatures now include return type annotations (e.g., `method() -> str`).

## Files Modified
- `pylint/pyreverse/inspector.py`: Modified `handle_assignattr_type` to check for type annotations (from AnnAssign and from function parameter annotations). Modified `visit_assignname` to check for annotations on class-level variables.
- `pylint/pyreverse/writer.py`: Added `_get_method_arguments` helper to DiagramWriter that includes type annotations. Updated DotWriter and VCGWriter `get_values` to show parameter and return type annotations.

## Public Tests Run
- `tests/unittest_pyreverse_inspector.py`: 8/8 passed
- `tests/unittest_pyreverse_writer.py`: 6/6 passed (including DOT file comparison)

## Why v1 Matches the Public Issue
The issue states that pyreverse does not read Python type hints for UML generation. The example shows `self.a = a` where `a: str = None` should display `a : str` in the UML diagram. v1 adds annotation-based type resolution at the inspector level and annotation display at the writer level.
