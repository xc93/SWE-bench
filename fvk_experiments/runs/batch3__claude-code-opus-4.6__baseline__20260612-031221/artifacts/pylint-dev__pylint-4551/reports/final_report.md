# SWE-bench Baseline: pylint-dev__pylint-4551

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=320&length=1
- Repo: pylint-dev/pylint
- Repo URL: https://github.com/pylint-dev/pylint.git
- Instance ID: pylint-dev__pylint-4551
- Base commit: 99589b08de8c5a2c6cc61e13a37420a868c80599
- Base commit URL: https://github.com/pylint-dev/pylint/commit/99589b08de8c5a2c6cc61e13a37420a868c80599
- Version: 2.9
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

Pyreverse (pylint's UML generation tool) does not read PEP 484 Python type hints when generating UML diagrams. For example, `class C: def __init__(self, a: str = None): self.a = a` should show `a : str` in the UML output, but currently does not show any type information for annotated attributes.

## Patch

- Files changed:
  - `pylint/pyreverse/inspector.py` - Modified `handle_assignattr_type()` to prefer type annotations over inference for attribute types; modified `visit_classdef()` to process `Unknown` nodes (e.g., dataclass fields) with `AnnAssign` parent annotations; modified `visit_assignname()` to resolve annotations for class-level annotated locals.
  - `pylint/pyreverse/diagrams.py` - Added `get_annotation_label()` method as fallback in `get_attrs()` to extract annotation strings when ClassDef-based resolution fails (handles complex types like `Optional[str]`).
  - `pylint/pyreverse/writer.py` - Added `_get_method_arguments()` to `DiagramWriter` base class for formatting method arguments with type annotations; modified `DotWriter.get_values()` to show parameter type annotations and return type annotations in method signatures.

- Behavioral change:
  - Instance attributes now show types from PEP 484 annotations (constructor parameter annotations and annotated assignments)
  - Class-level annotated attributes (including dataclass fields) now show their annotation types
  - Method signatures in UML output now include parameter type annotations (`param: Type`)
  - Method return type annotations are now displayed (`method() -> ReturnType`)
  - Annotation-based types take precedence over inference-based types when annotations are present

- Public tests run: All 23 existing pyreverse tests pass (writer: 6, inspector: 8, diadefs: 9)

- Why this matches the public issue statement: The issue requests that pyreverse read Python type hints (PEP 484) for UML generation. The patch makes pyreverse extract type annotations from annotated assignments, constructor parameter annotations, class-level annotations, and method signatures, displaying them in the UML output as requested.
