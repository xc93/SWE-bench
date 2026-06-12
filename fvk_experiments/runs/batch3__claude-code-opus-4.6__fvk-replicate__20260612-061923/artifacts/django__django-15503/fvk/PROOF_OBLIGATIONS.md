# PROOF OBLIGATIONS — django__django-15503

## Bug-fix obligations (FAIL_TO_PASS)

### OB-1: has_key with numeric string key must find matching objects
- **Input:** `data__has_key='1111'` where JSON data is `{'1111': 'bar'}`
- **Expected:** Object is returned in the queryset
- **Mechanism:** JSON path must use `$."1111"` (object key), not `$[1111]` (array index)
- **Backends:** SQLite, MySQL, Oracle

### OB-2: has_keys/has_any_keys with numeric string keys must find matching objects
- **Input:** `data__has_keys=['1111', 'foo']` or `data__has_any_keys=['1111']`
- **Expected:** Object is returned when all/any keys exist
- **Mechanism:** Same as OB-1, all keys must use object key notation

## Non-regression obligations (PASS_TO_PASS)

### OB-3: has_key with non-numeric string key must still work
- **Input:** `data__has_key='foo'`
- **Expected:** No change in behavior; `."foo"` was already generated correctly
- **Tests:** test_has_key, test_has_key_null_value

### OB-4: has_key with nested KeyTransform LHS must still work
- **Input:** `value__baz__has_key='a'`, `value__d__1__has_key='f'`
- **Expected:** LHS path correctly navigates (array indices preserved), RHS key checked
- **Tests:** test_has_key_deep

### OB-5: has_key with KeyTransform RHS must still work
- **Input:** `Q(value__has_key=KeyTransform("b", KeyTransform(1, "value")))`
- **Expected:** RHS path preserves array index notation for navigation
- **Tests:** test_has_key_list, test_has_key_deep

### OB-6: has_key with F() expression RHS must still work
- **Input:** `Q(value__has_key=F("value__d__1__f"))`
- **Expected:** F expression resolves to KeyTransform, navigation path preserved
- **Tests:** test_has_key_deep, test_has_key_list

### OB-7: has_keys with multiple string keys must still work
- **Input:** `data__has_keys=['a', 'c', 'h']`
- **Expected:** AND condition with correct object key paths
- **Tests:** test_has_keys

### OB-8: has_any_keys with multiple string keys must still work
- **Input:** `data__has_any_keys=['c', 'l']`
- **Expected:** OR condition with correct object key paths
- **Tests:** test_has_any_keys

### OB-9: KeyTransformIsNull on SQLite must still work
- **Input:** `value__d__0__isnull=False`
- **Expected:** Path `$."d"[0]` (navigation), NOT `$."d"."0"` (object key)
- **Mechanism:** KeyTransformIsNull.as_sqlite() must use compile_json_path directly
- **Tests:** test_key_transform_expression, test_nested_key_transform_expression, test_ordering_grouping_by_key_transform, test_key_transform_annotation_expression, test_nested_key_transform_annotation_expression, test_nested_key_transform_on_subquery

### OB-10: KeyTransformIsNull on Oracle must still work
- **Input:** Same as OB-9
- **Expected:** JSON_EXISTS with correct navigation path
- **Mechanism:** KeyTransformIsNull.as_oracle() must use compile_json_path directly

### OB-11: KeyTransform navigation must not change
- **Input:** `data__0`, `data__nested__key`
- **Expected:** compile_json_path produces correct navigation paths with array indices
- **Mechanism:** compile_json_path() is NOT modified
- **Tests:** test_deep_lookup_array, test_deep_lookup_mixed, test_deep_lookup_objs

### OB-12: PostgreSQL behavior must not change
- **Input:** Any has_key/has_keys/has_any_keys on PostgreSQL
- **Expected:** as_postgresql() path is unchanged
- **Mechanism:** v1 only changes as_sql() which is NOT called by as_postgresql()

### OB-13: Other JSON lookups must not change
- **Input:** contains, contained_by, exact, icontains on any backend
- **Expected:** No change; these lookups don't use HasKeyLookup
- **Tests:** all non-has_key JSON tests
