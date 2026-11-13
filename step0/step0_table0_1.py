"""
Step 0 (Quality Control) -- builds Table 0.1 and the Figure 0.1 grid.

VERSION 3 (Nov 2026): corrected visit order for sub-04.
The .mat files hold 11 columns per participant in VISIT order, and the MSL/MEC
order was counterbalanced across participants:
  MEC first (sub-02, -03, -05, -06, -07): mec01..mec05, msl01..msl06
  MSL first (sub-04):                     msl01..msl06, mec01..mec05
Only Sessions 1-5 enter the pipeline; msl06 is skipped wherever it sits.
(Version 2, in step0/, applied the MEC-first order to everyone.)

Run from anywhere:   python step0_table0_1.py
Paths are relative to this file (step0/ lives inside new_plan/). Only READS data.

Inputs  (in new_plan/):
    MRS-data_from-benali/PCC_new.mat, SMA_new.mat, SD.mat   (6 participants x 11 columns; only the first 10 are used)
    simple_lp-0.09_fwhm-6/         fMRI time series, NO global signal regression
    simple-gsr_lp-0.09_fwhm-6/     fMRI time series, WITH global signal regression
                                   (per each folder's strategy.json: "global_signal": "basic")

Outputs (in step0/):
    table0_1_participant_summary.csv / .xlsx / .md   <- Table 0.1
    table0_1_per_measurement.csv                     <- one row per participant x session x region
    table0_1_session_grid.csv                        <- participant x session completeness (Figure 0.1 input)
    fmri_availability_long.csv                       <- one row per pipeline x participant x scan

VALIDITY RULES (Obai to confirm!): an MRS value is VALID if it is present (not NaN) and > 0.
Optional: set SD_MAX to also flag measurements whose SD is above a threshold (None = off).
Nothing is imputed or filled in.
"""
import os
import numpy as np
import pandas as pd
from scipy.io import loadmat

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
MRS_DIR = os.path.join(BASE, "MRS-data_from-benali")
FMRI = {  # label -> folder  (labels follow strategy.json, NOT the old notebook naming)
    "no_GSR":   os.path.join(BASE, "simple_lp-0.09_fwhm-6"),
    "with_GSR": os.path.join(BASE, "simple-gsr_lp-0.09_fwhm-6"),
}
SUBJECTS = [f"sub-{i:02d}" for i in range(2, 8)]
MEC = [f"mec{i:02d}" for i in range(1, 6)]
MSL = [f"msl{i:02d}" for i in range(1, 6)]          # Sessions 1-5 only
SESSIONS = MEC + MSL                                   # 10 sessions per participant
# Column order in the .mat files depends on each participant's visit order
MEC_FIRST = [f"mec{i:02d}" for i in range(1, 6)] + [f"msl{i:02d}" for i in range(1, 7)]
MSL_FIRST = [f"msl{i:02d}" for i in range(1, 7)] + [f"mec{i:02d}" for i in range(1, 6)]
COLUMN_ORDER = {sub: MEC_FIRST for sub in SUBJECTS}
COLUMN_ORDER["sub-04"] = MSL_FIRST          # sub-04 did the MSL visits first
SD_MAX = None   # e.g. 1.0 to also flag high-SD measurements

TARGET_ROIS = [
    "17Networks_LH_DefaultA_pCunPCC_1", "17Networks_RH_DefaultA_pCunPCC_1",
    "17Networks_LH_SomMotA_1", "17Networks_LH_SomMotA_2", "17Networks_RH_SomMotA_1",
    "17Networks_RH_SomMotA_2", "17Networks_RH_SomMotA_3", "17Networks_RH_SomMotA_4",
    "17Networks_LH_DorsAttnB_PostC_1", "17Networks_LH_DorsAttnB_PostC_2",
    "17Networks_LH_DorsAttnB_PostC_3", "17Networks_RH_DorsAttnB_PostC_1",
    "17Networks_RH_DorsAttnB_PostC_2",
]


def load(name, key):
    return np.asarray(loadmat(os.path.join(MRS_DIR, name))[key], dtype=float)


# ------------------------------------------------------------------ MRS
mrs = {"PCC": load("PCC_new.mat", "PCC"), "SMA": load("SMA_new.mat", "SMA")}
sd = {"PCC": load("SD.mat", "PCC_SD"), "SMA": load("SD.mat", "SMA_SD")}

for reg in ("SMA", "PCC"):
    assert mrs[reg].shape == (len(SUBJECTS), 11), mrs[reg].shape

rows = []
for r, sub in enumerate(SUBJECTS):
    for sess in SESSIONS:
        c = COLUMN_ORDER[sub].index(sess)    # this participant's column for this visit
        for reg in ("SMA", "PCC"):
            v, s = mrs[reg][r, c], sd[reg][r, c]
            if np.isnan(v):
                status = "missing (NaN)"
            elif v <= 0:
                status = "invalid (value = 0)"
            elif SD_MAX is not None and (np.isnan(s) or s > SD_MAX):
                status = f"invalid (SD > {SD_MAX})"
            else:
                status = "valid"
            rows.append(dict(subject=sub, condition=sess[:3], session=sess,
                             session_number=int(sess[3:]), region=reg,
                             glutamate=v, sd=s, status=status, valid=(status == "valid")))
meas = pd.DataFrame(rows)
meas.to_csv(os.path.join(HERE, "table0_1_per_measurement.csv"), index=False)

# ------------------------------------------------------------------ matched complete blocks (sessions 1-5)
piv = meas.pivot_table(index=["subject", "session_number"], columns=["condition", "region"],
                       values="valid", aggfunc="first")
piv = piv.reindex(pd.MultiIndex.from_product([SUBJECTS, range(1, 6)],
                                             names=["subject", "session_number"]))
piv["complete"] = piv[[("mec", "SMA"), ("mec", "PCC"), ("msl", "SMA"), ("msl", "PCC")]].all(axis=1)

# ------------------------------------------------------------------ fMRI availability
def check_scan(path, labels):
    res = dict(file_exists=os.path.isfile(path), usable=False, n_timepoints=np.nan, problem="")
    if not res["file_exists"]:
        res["problem"] = "file missing"; return res
    try:
        df = pd.read_csv(path, header=None).apply(pd.to_numeric, errors="coerce")
    except Exception as e:
        res["problem"] = f"cannot read ({e})"; return res
    res["n_timepoints"] = len(df)
    if df.shape[1] != len(labels):
        res["problem"] = f"{df.shape[1]} columns vs {len(labels)} labels"; return res
    df.columns = labels
    miss = [r for r in TARGET_ROIS if r not in df.columns]
    if miss:
        res["problem"] = f"{len(miss)} target ROIs missing"; return res
    roi = df[TARGET_ROIS]
    if roi.isna().any().any():
        res["problem"] = "NaN in target ROIs"; return res
    if (roi.std(ddof=0) == 0).any():
        res["problem"] = "constant ROI signal"; return res
    res["usable"] = True
    return res

frows = []
for pipe, folder in FMRI.items():
    lab_path = os.path.join(folder, "labels.txt")
    labels = [l.strip() for l in open(lab_path)] if os.path.isfile(lab_path) else []
    for sub in SUBJECTS:
        for sess in SESSIONS:
            res = check_scan(os.path.join(folder, f"{sub}_ses-{sess}.csv"), labels)
            res.update(pipeline=pipe, subject=sub, session=sess, condition=sess[:3],
                       session_number=int(sess[3:]))
            frows.append(res)
fm = pd.DataFrame(frows)
fm.to_csv(os.path.join(HERE, "fmri_availability_long.csv"), index=False)

# ------------------------------------------------------------------ Table 0.1
def issues(sub):
    m = meas[(meas.subject == sub) & ~meas.valid]
    return "; ".join(f"{r.session} {r.region} ({r.status})" for r in m.itertuples()) or "none"

table = []
for sub in SUBJECTS:
    m = meas[meas.subject == sub]
    b = piv.loc[sub]
    miss_blocks = [f"S{n}" for n in b.index[~b["complete"]]]
    row = {
        "Participant": sub,
        "Valid MRS (of 20)": int(m.valid.sum()),
        "Valid SMA (of 10)": int(m[m.region == "SMA"].valid.sum()),
        "Valid PCC (of 10)": int(m[m.region == "PCC"].valid.sum()),
        "Missing/invalid MRS": issues(sub),
        "Complete matched sessions (of 5)": int(b["complete"].sum()),
        "Incomplete session pairs": ", ".join(miss_blocks) or "none",
    }
    for pipe in FMRI:
        f = fm[(fm.subject == sub) & (fm.pipeline == pipe)]
        row[f"fMRI {pipe} (of 10)"] = int(f.usable.sum())
        row[f"fMRI {pipe} problems"] = "; ".join(
            f"{r.session}: {r.problem}" for r in f[~f.usable].itertuples()) or "none"
    table.append(row)
table = pd.DataFrame(table)
tot = {"Participant": "TOTAL",
       "Valid MRS (of 20)": table["Valid MRS (of 20)"].sum(),
       "Valid SMA (of 10)": table["Valid SMA (of 10)"].sum(),
       "Valid PCC (of 10)": table["Valid PCC (of 10)"].sum(),
       "Missing/invalid MRS": f"{int((~meas.valid).sum())} of {len(meas)}",
       "Complete matched sessions (of 5)": table["Complete matched sessions (of 5)"].sum()}
for pipe in FMRI:
    tot[f"fMRI {pipe} (of 10)"] = table[f"fMRI {pipe} (of 10)"].sum()
table = pd.concat([table, pd.DataFrame([tot])], ignore_index=True).fillna("")

table.to_csv(os.path.join(HERE, "table0_1_participant_summary.csv"), index=False)
try:
    table.to_excel(os.path.join(HERE, "table0_1_participant_summary.xlsx"), index=False)
except Exception as e:
    print("xlsx skipped:", e)
cols = list(table.columns)
with open(os.path.join(HERE, "table0_1_participant_summary.md"), "w") as fh:
    fh.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
    for _, r in table.iterrows():
        fh.write("| " + " | ".join(str(r[c]) for c in cols) + " |\n")

# ------------------------------------------------------------------ Figure 0.1 input grid
grid = piv["complete"].unstack("session_number").map(lambda x: "complete" if x else "incomplete")
grid.columns = [f"Session {c}" for c in grid.columns]
grid.to_csv(os.path.join(HERE, "table0_1_session_grid.csv"))

pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 70)
print(table.to_string(index=False))
print("\nSession grid (complete = SMA & PCC valid in BOTH MSL and MEC):")
print(grid.to_string())
print("\nfMRI scan lengths:", fm.n_timepoints.value_counts().to_dict())
print("msl06 is not part of the pipeline (Sessions 1-5 only).")
print("\nWrote outputs to", HERE)
