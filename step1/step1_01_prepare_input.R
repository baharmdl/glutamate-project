# =============================================================================
# Step 1 - Script 01: Prepare the input data
# -----------------------------------------------------------------------------
# What this script does:
#   1. Reads the Step-0 file with one row per participant x session x region.
#   2. Keeps only VALID measurements (the Step-0 rule: present and > 0).
#   3. Adds log_glu = natural log of glutamate.
#   4. Writes step1_input.csv into this folder (step1 v2/).
#
# How to run:
#   In RStudio: Session > Set Working Directory > To Source File Location,
#   then click "Source". (Or: setwd(".../new_plan/step1 v2") then source this file.)
#
# Only base R is used here - no packages needed yet.
# Nothing is imputed: missing/invalid measurements are simply left out.
# =============================================================================

# ---- 1. Read the Step-0 per-measurement table --------------------------------
step0_file <- file.path("..", "step0", "table0_1_per_measurement.csv")
meas <- read.csv(step0_file, stringsAsFactors = FALSE)

cat("Rows in Step-0 table:", nrow(meas), "(expected 120 = 6 participants x 10 sessions x 2 regions)\n")

# ---- 2. Keep valid measurements only -----------------------------------------
# 'valid' was written by Python as the text "True"/"False", which R reads as
# character, not logical. So we compare it to the text "True".
dat <- meas[as.character(meas$valid) %in% c("True", "TRUE"), ]
cat("Valid rows kept:", nrow(dat), "(expected 114)\n")
cat("Rows dropped:   ", nrow(meas) - nrow(dat), "\n\n")

# ---- 3. Build the analysis columns -------------------------------------------
# condition: MEC (motor execution control) or MSL (motor sequence learning)
# session  : 1-5 = the five times of day. Stored as a number here; it becomes a
#            categorical FACTOR in the model script (so no straight-line assumption).
# region   : SMA (motor-learning MRS voxel) or PCC (control MRS voxel)
input <- data.frame(
  subject   = dat$subject,
  condition = toupper(dat$condition),   # "mec" -> "MEC", "msl" -> "MSL"
  session   = dat$session_number,       # 1..5
  region    = dat$region,               # "SMA" / "PCC"
  glutamate = dat$glutamate,            # original units (used later for the figure)
  log_glu   = log(dat$glutamate)        # natural log (base e) -> the model outcome
)

# Order rows in a readable way: participant, session, condition, region
input <- input[order(input$subject, input$session, input$condition, input$region), ]
rownames(input) <- NULL

# ---- 4. Quick checks ---------------------------------------------------------
cat("Valid measurements per participant:\n")
print(table(input$subject))

cat("\nValid measurements per condition x session x region (max 6 = all participants):\n")
print(ftable(table(input$condition, input$session, input$region)))

cat("\nGlutamate (original units) and log_glu summary:\n")
print(summary(input[, c("glutamate", "log_glu")]))

stopifnot(all(input$glutamate > 0))   # log() needs positive values

# ---- 5. Write the Step-1 input file ------------------------------------------
write.csv(input, "step1_input.csv", row.names = FALSE)
cat("\nWrote step1_input.csv with", nrow(input), "rows and columns:",
    paste(names(input), collapse = ", "), "\n")
