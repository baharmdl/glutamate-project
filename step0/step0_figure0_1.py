"""
Figure 0.1 (version 2: Sessions 1-5 only) -- participant x session completeness grid for MRS (reads table0_1_per_measurement.csv).
Run step0_table0_1.py first.   python step0_figure0_1.py
Each session cell = 2x2 squares: columns MEC | MSL, rows SMA / PCC.
Filled = valid measurement, grey X = missing/invalid. Outlined cell = all four valid (complete matched session).
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "table0_1_per_measurement.csv"))
df = df[df.session_number <= 5]
subs = sorted(df.subject.unique())
MAROON, GREY, INK = "#9c2b2b", "#e6e6e6", "#333333"

fig, ax = plt.subplots(figsize=(9.2, 6.4))
cw, ch, gap = 1.0, 1.0, 0.55   # square size, gap between sessions
def x0(s, cond): return (s - 1) * (2 * cw + gap) + (0 if cond == "mec" else cw)
def y0(i, reg):  return -(i * (2 * ch + 0.6) + (0 if reg == "SMA" else ch))

complete_count = {s: 0 for s in range(1, 6)}
for i, sub in enumerate(subs):
    n_complete = 0
    for s in range(1, 6):
        blk = df[(df.subject == sub) & (df.session_number == s)]
        for r in blk.itertuples():
            x, y = x0(s, r.condition), y0(i, r.region)
            ax.add_patch(Rectangle((x, y), cw, ch, fc=MAROON if r.valid else GREY,
                                   ec="white", lw=1.5))
            if not r.valid:
                ax.plot([x + .25, x + .75], [y + .25, y + .75], c="#888", lw=1.3)
                ax.plot([x + .25, x + .75], [y + .75, y + .25], c="#888", lw=1.3)
        if blk.valid.all() and len(blk) == 4:
            n_complete += 1; complete_count[s] += 1
            ax.add_patch(Rectangle((x0(s, "mec") - .06, y0(i, "PCC") - .06), 2 * cw + .12, 2 * ch + .12,
                                   fc="none", ec=INK, lw=1.2))
    ax.text(-0.5, y0(i, "SMA") - 0.0, sub, ha="right", va="center", fontsize=10, fontweight="bold", color=INK)
    ax.text(-0.5, y0(i, "PCC") + 0.5 - 0.0, "", ha="right")
    ax.text(-0.15, y0(i, "SMA") + .5, "SMA", ha="right", va="center", fontsize=7, color="#666")
    ax.text(-0.15, y0(i, "PCC") + .5, "PCC", ha="right", va="center", fontsize=7, color="#666")
    ax.text(5 * (2 * cw + gap) - gap + 0.6, y0(i, "SMA"), f"{n_complete}/5", ha="left", va="center",
            fontsize=10, fontweight="bold", color=MAROON)
# fix participant label position (centre of the two rows)
for t in list(ax.texts):
    if t.get_text().startswith("sub-"):
        t.set_position((-1.6, t.get_position()[1] - 0.0)); t.set_ha("right")

ybot = y0(len(subs) - 1, "PCC") - 1.0
for s in range(1, 6):
    xc = x0(s, "mec") + cw
    ax.text(xc, 1.85, f"Session\n{s}", ha="center", va="bottom", fontsize=9, fontweight="bold", color=INK)
    ax.text(x0(s, "mec") + cw / 2, 1.15, "MEC", ha="center", va="bottom", fontsize=7, color="#666")
    ax.text(x0(s, "msl") + cw / 2, 1.15, "MSL", ha="center", va="bottom", fontsize=7, color="#666")
    ax.text(xc, ybot, f"{complete_count[s]}/6", ha="center", va="top", fontsize=10,
            fontweight="bold", color=MAROON)
ax.text(5 * (2 * cw + gap) - gap + 0.6, 1.95, "Complete\nsessions", ha="left", va="bottom", fontsize=8, color="#666")
ax.text(-1.6, ybot, "Complete\nparticipants", ha="right", va="top", fontsize=8, color="#666")

ax.set_xlim(-4.3, 5 * (2 * cw + gap) + 1.6); ax.set_ylim(ybot - 1.6, 3.4)
ax.set_aspect("equal"); ax.axis("off")
fig.suptitle("Figure 0.1  MRS measurement completeness per participant and session",
             fontsize=11, fontweight="bold", color=MAROON, x=0.5, y=0.97)

import matplotlib.lines as ml
h = [Rectangle((0, 0), 1, 1, fc=MAROON), Rectangle((0, 0), 1, 1, fc=GREY),
     Rectangle((0, 0), 1, 1, fc="none", ec=INK, lw=1.2)]
ax.legend(h, ["Valid measurement", "Missing / invalid", "Complete matched session (all 4 valid)"],
          loc="lower center", bbox_to_anchor=(0.5, -0.06), ncol=3, frameon=False, fontsize=8)
fig.text(0.5, 0.0, "Valid = present and > 0 (validity criteria pending). Nothing imputed. "
         "MEC = motor execution control, MSL = motor sequence learning.", fontsize=7, color="#666", ha="center")
fig.savefig(os.path.join(HERE, "figure0_1_mrs_completeness.png"), dpi=200, bbox_inches="tight")
fig.savefig(os.path.join(HERE, "figure0_1_mrs_completeness.pdf"), bbox_inches="tight")
print("saved")
