# Setup Notes

## Environment Verification

- **Repo HEAD**: `009bb81` (tagged "base"; workspace pre-built, commit hash differs from canonical `cdb6605` but astropy version matches 5.1)
- **astropy version**: 5.1 (confirmed via `import astropy; print(astropy.__version__)`)
- **astropy installed from**: `repo/astropy/__init__.py` (editable install)
- **pytest version**: 7.4.0
- **Test runner**: verified with `repo/astropy/io/registry/tests/test_registries.py` — 221 passed, 14 skipped

## Repairs

None needed. Environment was ready as staged.
