# Step 1: Glutamate across the day

Scientific question: does MRS glutamate vary across session, condition (MSL / MEC) and region (SMA / PCC)?

Run from the Step-1 folder, in this order. Step 1 reads the Step-0 output `../step0/table0_1_per_measurement.csv`.

| Script | What it does | Output |
|---|---|---|
| `step1_01_prepare_input.R` | Keeps valid MRS measurements from Step 0 and adds `log_glu` | `step1_input.csv` |
| `step1_02_models.R` | Fits Step 1A and Step 1B mixed models (sum coding, REML, Type-III ANOVA, Satterthwaite df) | `table1_1_F_p_1A_vs_1B.csv`, `table1_2_model_comparison.csv`, `table1_3_final_step1_1B.csv` |
| `step1_03_figure.py` | Two-panel glutamate trajectory figure (A: SMA, B: PCC) | `figure1_1_glutamate_trajectories.png` / `.pdf` |

Models

- 1A: `log_glu ~ condition * session * region + (1 | subject)`
- 1B (final): `log_glu ~ condition * session * region + (1 | subject) + (1 | subject:condition:session)`

Requirements: R with `lmerTest`; Python with `pandas` and `matplotlib`.
