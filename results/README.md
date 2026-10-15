# Result evidence

These CSVs preserve the project's numerical comparison. Sales and errors use the dataset's original sales units, with no assumed currency.

| File | Scope |
|---|---|
| `seven_selection.csv` | Seven procedures ranked by mean daily MAE across the three development windows beginning 11 April, 9 May and 6 June 2015. |
| `forest_scores.csv` | Original Forest results for all six inspected 28-day windows. |
| `revenue_comparison.csv` | July baseline and Regression totals and percentage errors. |
| `backtest_scores.csv` | Four procedures across three development windows, including total percentage error. |
| `supplemental_scores.csv` | Four procedures across two supplemental windows. Together with the preceding two files, supports the four-improve/two-worsen total-error statement across six windows. |
| `forest_sensitivity_scores.csv` | Four fixed Forest specifications across the six windows, 24 rows. |
| `forest_sensitivity_summary.csv` | Three-development-window summaries of the sensitivity diagnostics. |

`Mean_MAE` and `Mean_RMSE` average window-level daily errors. `Total %` is 100 × (forecast total − actual total) / actual total. Absolute-total-error summaries remove the sign before averaging. `Neg` counts negative daily forecasts. Window averages give each window equal weight.

The notebook recomputes the original comparisons from raw data and checks the seven-procedure ranking and Forest scores against these snapshots. Its sensitivity section calls `scripts/forest_sensitivity.py`, which independently reconstructs the original Forest before writing the two sensitivity CSVs. The original comparison snapshots remain unchanged during a run. This is a consistency check, not independent validation on new data.

The sensitivity variants are post-ranking diagnostics. They do not retrospectively replace the original Forest in the seven-procedure ranking. All six periods have been inspected during development.
