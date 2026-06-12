# Iteration Guidance for v2

## Root cause of v1 gap
v1 only modified `django/db/models/constraints.py` and missed:
1. `ExclusionConstraint` in `django/contrib/postgres/constraints.py` (a third subclass of `BaseConstraint`)
2. `__repr__` methods across all three constraint classes needed `violation_error_code` display

## Required v2 changes

### In `django/db/models/constraints.py`:
1. **CheckConstraint.__repr__**: Add format slot for `violation_error_code`, shown when not None.
2. **UniqueConstraint.__repr__**: Add format slot for `violation_error_code`, shown when not None.

### In `django/contrib/postgres/constraints.py`:
3. **ExclusionConstraint.__init__**: Add `violation_error_code=None` parameter; pass to `super().__init__()`.
4. **ExclusionConstraint.validate()**: Both `ValidationError` raises need `code=self.violation_error_code`.
5. **ExclusionConstraint.__eq__()**: Add `self.violation_error_code == other.violation_error_code`.
6. **ExclusionConstraint.__repr__**: Add format slot for `violation_error_code`, shown when not None.

## What NOT to change
- Do not modify SQL generation methods.
- Do not change default behavior when `violation_error_code` is `None`.
- Do not alter deprecated positional args path.

## Regression risks
Minimal: all changes are additive. Default `None` preserves existing behavior.
