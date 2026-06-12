# Setup Notes

- repo/ is checked out at the base commit (squashed as single "base" commit 14a8a4d)
- .venv/bin/python imports astropy 5.1 correctly
- pytest 7.4.0 is available
- All 9 existing RST tests pass: repo/astropy/io/ascii/tests/test_rst.py
- NumPy ndarray size warning (harmless binary compat note) present but tests pass
