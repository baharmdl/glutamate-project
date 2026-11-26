# Step 2 - 04: Figure 2.1 (D per subject and session) and Figure 2.2 (primary vs sensitivity)
# Run from this folder after scripts 01-03:  python step2_04_figures.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pct = lambda x: 100 * (np.exp(x) - 1)       # back-transform for the y-axis
d    = pd.read_csv("final/step2_D.csv")
sess = pd.read_csv("step2_session_means.csv")
t21  = pd.read_csv("final/table2_1_primary_contrast.csv")["value"]
est, lo, hi = float(t21[3]), float(t21[4]), float(t21[5])     # average D and 95% CI
sens = pd.read_csv("step2_sensitivity_contrast.csv").iloc[0]

# ---- Figure 2.1 -------------------------------------------------------------
colors  = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
markers = ["o", "s", "^", "v", "P", "X"]
fig, ax = plt.subplots(figsize=(8, 5))
for k, s in enumerate(sorted(d.subject.unique())):
    ds = d[d.subject == s].set_index("session").reindex([1, 2, 3, 4, 5])  # missing block = gap
    x = np.arange(1, 6) - 0.2 + 0.08 * k
    ax.plot(x, pct(ds.D), color=colors[k], lw=1, alpha=0.45)
    ax.plot(x, pct(ds.D), ls="none", marker=markers[k], ms=8, color=colors[k], mec="white", label=s)
ax.axhspan(pct(lo), pct(hi), color="0.85", alpha=0.6, lw=0, label="model average D, 95% CI")
ax.axhline(pct(est), color="0.25", ls="--", lw=1.5)
ax.errorbar(sess.session + 0.33, pct(sess.mean_D),
            yerr=[pct(sess.mean_D) - pct(sess.CI95_low), pct(sess.CI95_high) - pct(sess.mean_D)],
            fmt="D", color="black", ms=7, capsize=3, label="model mean per session, 95% CI")
ax.axhline(0, color="0.4", lw=1)
for b in [1.5, 2.5, 3.5, 4.5]:
    ax.axvline(b, color="0.9", lw=1, zorder=0)
ax.set_xticks(range(1, 6), [f"Session {s}" for s in range(1, 6)])
ax.set_ylabel("D as 100 × (exp(D) − 1)  (%)\n> 0: MSL/MEC ratio larger in SMA than in PCC")
ax.set_title("Figure 2.1  SMA-vs-PCC learning-related glutamate contrast (D)\n"
             "per subject and session (complete blocks only; missing blocks left empty)", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(fontsize=8, frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1))
fig.tight_layout()
fig.savefig("final/figure2_1_D_by_session.png", dpi=200)

# ---- Figure 2.2 -------------------------------------------------------------
rows = [("Primary: complete blocks\nD ~ session + (1|subject)", est, lo, hi),
        ("Sensitivity: all regional pairs\nSMA − PCC from dGlu model",
         sens.estimate, sens.CI95_low, sens.CI95_high)]
fig, ax = plt.subplots(figsize=(7, 2.8))
for y, (lab, e, l, h) in zip([1, 0], rows):
    ax.plot([l, h], [y, y], color="#2a78d6", lw=2)
    ax.plot(e, y, "o", color="#2a78d6", ms=9, mec="white")
    ax.text(h + 0.01, y, f" {e:.3f} [{l:.3f}, {h:.3f}]", va="center", fontsize=9)
ax.axvline(0, color="0.4", lw=1)
ax.set_yticks([1, 0], [r[0] for r in rows], fontsize=9)
ax.set_ylim(-0.6, 1.6)
ax.set_xlim(-0.2, 0.42)
ax.set_xlabel("SMA − PCC difference in log(MSL/MEC), estimate and 95% CI (log units)")
ax.set_title("Figure 2.2  Primary vs all-available regional sensitivity estimate", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("final/figure2_2_primary_vs_sensitivity.png", dpi=200)
