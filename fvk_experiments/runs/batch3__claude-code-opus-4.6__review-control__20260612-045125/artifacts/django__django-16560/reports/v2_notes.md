# v2 Notes

## How v2 differs from v1
v2 adds two categories of changes that v1 missed:
1. `ExclusionConstraint` support in `django/contrib/postgres/constraints.py`
2. `__repr__` updates in all three constraint classes to include `violation_error_code`

## Files changed (additional to v1's constraints.py)
- `django/db/models/constraints.py` (additional __repr__ changes)
- `django/contrib/postgres/constraints.py` (new file, all changes)

## Changes in v2 (additional to v1)

### django/db/models/constraints.py:
1. `CheckConstraint.__repr__`: Added conditional `violation_error_code` display.
2. `UniqueConstraint.__repr__`: Added conditional `violation_error_code` display.

### django/contrib/postgres/constraints.py:
3. `ExclusionConstraint.__init__`: Added `violation_error_code=None` parameter; passes through to `super().__init__()`.
4. `ExclusionConstraint.validate()`: Both `ValidationError` raises now pass `code=self.violation_error_code`.
5. `ExclusionConstraint.__eq__()`: Added `self.violation_error_code == other.violation_error_code`.
6. `ExclusionConstraint.__repr__`: Added conditional `violation_error_code` display.

## Which review findings caused the change
- FINDINGS.md section 9: "CRITICAL: ExclusionConstraint not updated" and "CRITICAL: __repr__ methods not updated"

## Regression risks v2 avoids
- Default `None` preserves existing behavior when `violation_error_code` is not specified.
- No changes to SQL generation methods.
- `ExclusionConstraint.deconstruct()` already calls `super().deconstruct()` which handles `violation_error_code`.
