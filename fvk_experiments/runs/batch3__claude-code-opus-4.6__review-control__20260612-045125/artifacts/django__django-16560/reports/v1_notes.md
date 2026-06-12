# v1 Notes

## What behavior v1 changes
Adds a `violation_error_code` parameter to `BaseConstraint`, `CheckConstraint`, and `UniqueConstraint`. When a constraint's `validate()` method raises a `ValidationError`, the custom `code` is now passed to the `ValidationError` constructor. This allows users to customize the error code without subclassing the constraint.

## Files modified
- `django/db/models/constraints.py`

## Changes made
1. **BaseConstraint.__init__**: Added `violation_error_code=None` parameter; stores it as `self.violation_error_code`.
2. **BaseConstraint.deconstruct**: Includes `violation_error_code` in kwargs when not None.
3. **CheckConstraint.__init__**: Added `violation_error_code=None` parameter, passes through to super().
4. **CheckConstraint.validate**: Passes `code=self.violation_error_code` to `ValidationError`.
5. **CheckConstraint.__eq__**: Includes `violation_error_code` in equality comparison.
6. **UniqueConstraint.__init__**: Added `violation_error_code=None` parameter, passes through to super().
7. **UniqueConstraint.validate**: Passes `code=self.violation_error_code` to all four `ValidationError` raises (expressions path, fields path, condition path).
8. **UniqueConstraint.__eq__**: Includes `violation_error_code` in equality comparison.

## Public tests run
- `constraints.tests.BaseConstraintTests` (12 tests) - all pass
- `constraints.tests.CheckConstraintTests` (16 tests) - all pass
- `constraints.tests.UniqueConstraintTests` (45 tests) - all pass (4 skipped for DB features)
- Total: 73 pass, 0 fail, 4 skipped

## Why v1 matches the public issue
The issue requests the ability to customize the `code` attribute of `ValidationError` raised by `BaseConstraint.validate`, analogous to the existing `violation_error_message`. The patch adds `violation_error_code` following the exact same pattern as `violation_error_message`.
