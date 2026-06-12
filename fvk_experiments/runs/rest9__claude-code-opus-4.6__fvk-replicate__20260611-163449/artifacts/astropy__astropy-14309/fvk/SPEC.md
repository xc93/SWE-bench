# SPEC — is_fits identifier function

## Intended behavior (from issue + API docs)

The `is_fits(origin, filepath, fileobj, *args, **kwargs)` function in `astropy/io/fits/connect.py` is an **identifier function** registered with the IO registry. Its job: return `True` if the input can be identified as FITS format, `False` otherwise. It must never raise.

Per `astropy/io/registry/base.py:232-236`, identifier functions:
- Receive `(origin, path, fileobj, *args, **kwargs)` where `path` and `fileobj` may both be `None`
- Must return `True` or `False`
- When both `path` and `fileobj` are `None`, must work from `args[0]`
- The implicit contract: `args` may be empty (callers pass `[]`)

## Pre-condition

The function must handle all combinations of its inputs without raising:
- `filepath` can be `None` or a string (any extension)
- `fileobj` can be `None` or a file-like object
- `args` can be empty or contain FITS/non-FITS objects

## Post-condition

Returns `True` iff one of:
1. `fileobj` is not None and its first 30 bytes match `FITS_SIGNATURE`
2. `filepath` is not None and ends with a recognized FITS extension
3. `args` is non-empty and `args[0]` is an instance of `(HDUList, TableHDU, BinTableHDU, GroupsHDU)`

Returns `False` in all other cases. Never raises an exception.

## Non-regression obligations

1. When `fileobj` is provided, the function must read 30 bytes, check the signature, seek back, and return the result
2. When `filepath` has a FITS extension (.fits, .fits.gz, .fit, .fit.gz, .fts, .fts.gz), must return `True` regardless of `args`
3. When `args[0]` is a FITS HDU type, must return `True` even if `filepath` is None
4. The function must not modify `args`, `kwargs`, or any mutable state
5. All existing tests in `astropy/io/fits/tests/test_connect.py` must continue to pass
6. All existing tests in `astropy/io/registry/tests/test_registries.py` must continue to pass
