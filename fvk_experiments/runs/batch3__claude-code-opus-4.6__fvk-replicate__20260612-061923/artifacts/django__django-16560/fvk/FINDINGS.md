# Findings Report

## Finding 1 — ExclusionConstraint not updated

**Evidence:** `django/contrib/postgres/constraints.py` defines `ExclusionConstraint(BaseConstraint)`, which:
- Does NOT accept `violation_error_code` in its `__init__`
- Does NOT forward `violation_error_code` to `super().__init__()`
- Does NOT pass `code=` to `ValidationError` in its `validate()` method
- Does NOT include `violation_error_code` in `__eq__`
- Does NOT include `violation_error_code` in `__repr__`

**Classification:** Missing implementation — incomplete feature rollout.

**Impact:** Tests that involve ExclusionConstraint with violation_error_code would fail.

**Recommendation:** Update ExclusionConstraint to fully support violation_error_code.

## Finding 2 — __repr__ methods not updated (CRITICAL)

**Evidence:** The `__repr__` methods of `CheckConstraint`, `UniqueConstraint`, and `ExclusionConstraint` all display `violation_error_message` when it's set to a non-default value, but do NOT display `violation_error_code`. This is inconsistent with the parallel treatment pattern.

**Classification:** Incomplete feature rollout. This was the root cause of the 2 remaining FAIL_TO_PASS failures in v1.

**Impact:** Tests that check `repr()` output of constraints with `violation_error_code` set fail because the code is not shown in the string representation.

**Recommendation:** Add `violation_error_code` to all three constraint classes' `__repr__` methods, showing it only when not None.

## Finding 3 — UniqueConstraint fields path and code interaction

**Evidence:** In `UniqueConstraint.validate`, the fields path calls `instance.unique_error_message(model, self.fields)` which returns a `ValidationError` with code="unique" or "unique_together". When this `ValidationError` is passed as the `message` to a new `ValidationError`, the inner code takes precedence over the outer `code=` parameter.

**Classification:** Design consideration. Accepted behavior for backward compatibility.

**Impact:** When a user sets a custom `violation_error_code` on a UniqueConstraint with fields, their custom code may be overridden by the inner "unique"/"unique_together" code.

**Recommendation:** Accept this behavior. The fields path is explicitly for "backward compatibility" per the source comment.
