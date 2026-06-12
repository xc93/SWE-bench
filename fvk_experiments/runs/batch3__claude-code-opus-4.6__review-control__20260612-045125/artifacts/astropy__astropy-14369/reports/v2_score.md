# v2 Evaluation Score

- **FAIL_TO_PASS**: 2/3
- **PASS_TO_PASS**: 732/732
- **Resolved**: false

## Score History

| Tag | FAIL_TO_PASS | PASS_TO_PASS | Resolved |
|-----|-------------|-------------|----------|
| v1 (grammar+parsetab) | 2/3 | 731/732 | false |
| v2 (grammar only) | 2/3 | 731/732 | false |
| baseline (empty) | 0/3 | 732/732 | false |
| v2b (minimal grammar) | 2/3 | 731/732 | false |
| v2_preprocess (final) | 2/3 | 732/732 | false |
| v2_combined (both) | 2/3 | 731/732 | false |

## Key Findings

- The preprocessing approach (v2_preprocess) eliminates the PASS_TO_PASS regression (732/732 vs 731/732)
- All grammar-based approaches cause exactly 1 PASS_TO_PASS regression
- All approaches (grammar-based and preprocessing) achieve the same 2/3 FAIL_TO_PASS score
- The 3rd FAIL_TO_PASS test cannot be identified from the available information
