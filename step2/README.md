# Step 2: Learning-related glutamate difference between SMA and PCC

Scientific question: after accounting for MEC, is the learning-related glutamate change different between SMA and PCC?

For each participant × session: `dSMA = log(SMA_MSL / SMA_MEC)`, `dPCC = log(PCC_MSL / PCC_MEC)`, `D = dSMA - dPCC`. Only complete blocks (all four values) are used; nothing is imputed.

Run Steps 0 and 1 first, then the scripts below from the Step-2 folder, in this order. Step 2 reads the Step-1 input file (`../step1 v3/step1_input.csv` in the local folder layout; change this path if your Step-1 folder has another name).

| Script | What it does | Output |
|---|---|---|
| `step2_01_compute_D.R` | Builds dSMA, dPCC and D for each complete subject × session block | `final/step2_D.csv`, `step2_blocks_long.csv` |
| `step2_02_primary_model.R` | Fits the primary model (sum coding, REML, Type-III ANOVA, Satterthwaite df) | `final/step2_primary_model_output.Rout`, `final/table2_1_primary_contrast.csv`, `step2_session_means.csv` |
| `step2_03_sensitivity_model.R` | Fits the all-available regional sensitivity model and the SMA − PCC contrast (emmeans) | `final/step2_sensitivity_model_output.Rout`, `step2_dGlu_long.csv`, `step2_sensitivity_contrast.csv` |
| `step2_04_figures.py` | Figure 2.1 (D per subject and session) and Figure 2.2 (primary vs sensitivity) | `final/figure2_1_D_by_session.png`, `final/figure2_2_primary_vs_sensitivity.png` |

Models

- Primary: `D ~ session + (1 | subject)`
- Sensitivity: `dGlu ~ region * session + (1 | subject) + (1 | subject:session)`, with `dGlu = log(Glu_MSL / Glu_MEC)`

Requirements: R with `lmerTest` and `emmeans`; Python with `numpy`, `pandas` and `matplotlib`. Create a `final/` folder next to the scripts before running.
