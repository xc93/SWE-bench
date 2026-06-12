# v1 Notes

## Behavioral change
v1 adds a `violation_error_code` parameter to `BaseConstraint`, `CheckConstraint`, and `UniqueConstraint`. This allows users to customize the `code` attribute of the `ValidationError` raised when a constraint is violated, similar to the existing `violation_error_message` mechanism.

## Files modified
- `django/db/models/constraints.py`

## Changes in detail

### BaseConstraint
- Added `violation_error_code = None` class attribute
- Added `violation_error_code` parameter to `__init__`
- Added `get_violation_error_code()` method
- Added `violation_error_code` to `deconstruct()` (only when not None)

### CheckConstraint
- Added `violation_error_code` parameter to `__init__`, forwarded to super
- Updated `validate()` to pass `code=self.get_violation_error_code()` to `ValidationError`
- Added `violation_error_code` to `__eq__` comparison

### UniqueConstraint
- Added `violation_error_code` parameter to `__init__`, forwarded to super
- Updated `validate()` to pass `code=self.get_violation_error_code()` to `ValidationError` in all three branches (expressions, fields, condition)
- Added `violation_error_code` to `__eq__` comparison

## Public tests run
- `python tests/runtests.py constraints` - 73 tests pass, 4 skipped

## Why this matches the public issue
The issue requests the ability to customize the `code` attribute of `ValidationError` raised by `BaseConstraint.validate`. The approach mirrors the existing `violation_error_message` pattern: a class attribute, an `__init__` parameter, a getter method, and integration into deconstruct/equality/clone. When `violation_error_code` is None (the default), the `ValidationError` behaves exactly as before (code defaults to None in ValidationError constructor).
