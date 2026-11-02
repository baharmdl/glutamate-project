"""
Figure 1.1: glutamate trajectories across the day (descriptive only)
  Panel A = SMA, Panel B = PCC; Sessions 1-5; MEC and MSL
  Thin lines  = individual participants
  Thick lines = group mean +/- SEM of the available values
  Original glutamate units, same y-axis in both panels,
  missing data left missing (lines break), no significance marks.

Run from this folder:  python step1_03_figure.py
Needs: pandas, matplotlib
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dat = pd.read_csv("step1_input.csv")

COLORS = {"MEC": "#2a78d6", "MSL": "#eb6834"}
MARKERS = {"MEC": "o", "MSL": "s"}
SHIFT = {"MEC": -0.08, "MSL": 0.08}      # small left/right offset so they don't overlap
SESSIONS = [1, 2, 3, 4, 5]

fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)   # same y-axis

for ax, region, label in zip(axes, ["SMA", "PCC"], ["A  SMA", "B  PCC"]):
    for cond in ["MEC", "MSL"]:
        d = dat[(dat.region == region) & (dat.condition == cond)]
        x = np.array(SESSIONS) + SHIFT[cond]

        # Individual participants: reindex to all 5 sessions so missing = NaN = gap
        for subj, ds in d.groupby("subject"):
            y = ds.set_index("session")["glutamate"].reindex(SESSIONS)
            ax.plot(x, y, color=COLORS[cond], alpha=0.3, lw=0.8,
                    marker=".", ms=5)

        # Group summary: mean +/- SEM of available values per session
        g = d.groupby("session")["glutamate"].agg(["mean", "std", "count"]).reindex(SESSIONS)
        sem = g["std"] / np.sqrt(g["count"])
        ax.errorbar(x, g["mean"], yerr=sem, color=COLORS[cond], lw=2.4,
                    marker=MARKERS[cond], ms=7, capsize=0, ecolor="0.3",
                    elinewidth=1.2, label=cond, zorder=3)

    ax.set_title(label, loc="left", fontweight="bold", fontsize=13)
    ax.set_xticks(SESSIONS, [f"Session {s}" for s in SESSIONS])
    ax.spines[["top", "right"]].set_visible(False)

axes[0].set_ylabel("Glutamate (original units)")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
fig.text(0.99, 0.01, "Thin lines: individual participants. "
         "Thick lines: group mean ± SEM of available values.",
         ha="right", fontsize=9, color="0.3")
fig.tight_layout(rect=(0, 0.04, 1, 0.93))

fig.savefig("figure1_1_glutamate_trajectories.png", dpi=300)
fig.savefig("figure1_1_glutamate_trajectories.pdf")
