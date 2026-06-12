# ITERATION GUIDANCE: v1 → v2

## What v1 got right

- Correctly identified the code location (`_check_required_columns` in `core.py`)
- Correctly used conditional logic to preserve single-column format
- Correctly showed all required columns and found columns for multi-column case

## What v1 got wrong

1. **Format string produces extra quotes**: The format `"expected '{}'"` wraps the list repr in single quotes. For `['time', 'flux']`, this gives `"expected '['time', 'flux']'"` instead of `"expected ['time', 'flux']"`.

2. **Changed the "no columns" branch unnecessarily**: Lines 73-75 were not cited in the issue and should be left alone to avoid regressions.

## Exact minimal changes for v2

Change ONLY lines 79-81 (the elif/mismatch branch). Replace:

```python
raise ValueError("{} object is invalid - expected '{}' "
                 "as the first column{} but found '{}'"
                 .format(self.__class__.__name__, required_columns[0], plural, self.colnames[0]))
```

With conditional formatting that:
- For `len(required_columns) == 1`: produces `"expected 'X' as the first column but found 'Y'"` (identical to original)
- For `len(required_columns) > 1`: produces `"expected ['X', 'Y'] as the first columns but found ['X']"` (no extra quotes)

## Changes forbidden for v2

- Do NOT modify the "no columns" branch (lines 73-75)
- Do NOT change `_required_columns_relax` logic
- Do NOT change the `plural` computation
- Do NOT change `autocheck_required_columns` decorator
- Do NOT change any other file
