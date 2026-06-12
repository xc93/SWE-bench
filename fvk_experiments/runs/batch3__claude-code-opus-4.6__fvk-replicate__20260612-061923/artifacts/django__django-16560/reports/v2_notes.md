# v2 Notes

## How v2 differs from v1

v2 adds all v1 changes PLUS three categories of updates:

### 1. ExclusionConstraint updates (django/contrib/postgres/constraints.py)
- Added `violation_error_code=None` parameter to `ExclusionConstraint.__init__`
- Forwards `violation_error_code` to `super().__init__()`
- Updated `validate()` to pass `code=self.violation_error_code` to `ValidationError`
- Added `violation_error_code` comparison to `__eq__`
- Added `violation_error_code` to `__repr__`

### 2. __repr__ updates (both files)
- Updated `CheckConstraint.__repr__` to show `violation_error_code` when not None
- Updated `UniqueConstraint.__repr__` to show `violation_error_code` when not None
- Updated `ExclusionConstraint.__repr__` to show `violation_error_code` when not None

### 3. Minor cleanup
- Changed `self.get_violation_error_code()` to `self.violation_error_code` for direct attribute access

## Which FVK findings caused the change

**Finding 1 (CRITICAL):** ExclusionConstraint was identified as a subclass of BaseConstraint that was NOT updated in v1.

**Finding 2 (discovered during v2 iteration):** The `__repr__` methods for CheckConstraint and UniqueConstraint did not show `violation_error_code`. FVK reasoning about "what behavior should remain unchanged for the public APIs the patch touches" led to examining ALL methods that handle `violation_error_message` and ensuring parallel treatment for `violation_error_code`. The `__repr__` methods were the gap.

## Regression risks v2 is designed to avoid

- When `violation_error_code` is None (default), `__repr__` output is identical to before
- ExclusionConstraint backward compatibility fully preserved
- All 73 existing public constraint tests pass
- `validate_constraints` code path unchanged (still checks `e.code == "unique"`)
