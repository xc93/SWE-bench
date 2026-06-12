# Setup Verification

- repo/ checked out at commit b299fe8c84369474f8bc536cadec865d7a4f5cb3 (environment_setup_commit, not the base_commit)
- .venv/bin/python imports astropy 5.0
- pytest is available (.venv/bin/python -m pytest)
- Note: running tests via pytest triggers numpy binary incompatibility warnings and IERS data issues due to internet access being disabled by pytest-remotedata plugin. Manual Python verification of transforms works correctly.
- All transform logic verified manually by running coordinate conversions outside pytest.
