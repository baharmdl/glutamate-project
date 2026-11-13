# Step 0: Quality control

Builds the analytic MRS/fMRI dataset used by all later steps. Run before Step 1.

| Script | What it does | Main output |
|---|---|---|
| `step0_table0_1.py` | Reads the raw MRS `.mat` files and fMRI time series, labels every measurement, flags valid/missing values (Sessions 1-5 only) | `table0_1_per_measurement.csv` (read by Step 1), Table 0.1, session grid, fMRI availability |
| `step0_figure0_1.py` | Participant × session completeness figure | `figure0_1_mrs_completeness.png` / `.pdf` |

**Visit order.** The raw `.mat` files store each participant's 11 visits in the order they happened, and the MSL/MEC order was counterbalanced. Every participant is read as MEC first except **sub-04, who did MSL first** (`COLUMN_ORDER` in `step0_table0_1.py`). An earlier version applied the MEC-first order to everyone, which mislabelled sub-04.

Inputs (not in this repository) are expected next to this folder: `MRS-data_from-benali/` and the two fMRI pipeline folders.

Requirements: Python with `numpy`, `pandas`, `scipy`, `matplotlib` (`openpyxl` for the .xlsx table).
