# Formal Specification: violation_error_code for BaseConstraint

## Intended behavior (from public issue)

Add a `violation_error_code` parameter to `BaseConstraint` (and all subclasses) that allows customizing the `code` attribute of the `ValidationError` raised when a constraint is violated. This mirrors the existing `violation_error_message` mechanism and is analogous to the `code` parameter on Django validators.

## Specification

### Pre-condition
- `BaseConstraint`, `CheckConstraint`, `UniqueConstraint`, and `ExclusionConstraint` exist with `violation_error_message` support.
- `ValidationError(message, code=None, params=None)` accepts an optional `code`.

### Post-condition
For every constraint class C in {BaseConstraint, CheckConstraint, UniqueConstraint, ExclusionConstraint}:

1. **__init__**: C accepts `violation_error_code=None` keyword parameter.
2. **Class attribute**: C has `violation_error_code = None` class attribute (no default code).
3. **Storage**: When `violation_error_code is not None`, `self.violation_error_code = violation_error_code`.
4. **validate**: All `ValidationError` raises include `code=self.violation_error_code`.
5. **deconstruct**: Includes `violation_error_code` in kwargs when not None.
6. **clone**: Preserved via deconstruct round-trip.
7. **__eq__**: Compares `violation_error_code`.

### Default behavior (backward compat)
When `violation_error_code` is not specified:
- `self.violation_error_code` is None
- `ValidationError` is raised with `code=None` (same as before)
- `deconstruct` does not include `violation_error_code` in kwargs
- All existing behavior is preserved
