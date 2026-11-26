# Step 2 - 01: dSMA, dPCC and D for each complete subject x session block
# Run from this folder: Session > Set Working Directory > To Source File Location

dat <- read.csv("../step1 v3/step1_input.csv")

# One row per subject x session, one column per region_condition (e.g. SMA_MSL)
dat$cell <- paste(dat$region, dat$condition, sep = "_")
wide <- reshape(dat[, c("subject", "session", "cell", "glutamate")],
                idvar = c("subject", "session"), timevar = "cell", direction = "wide")
names(wide) <- sub("glutamate.", "", names(wide), fixed = TRUE)
wide <- wide[order(wide$subject, wide$session),
             c("subject", "session", "SMA_MSL", "SMA_MEC", "PCC_MSL", "PCC_MEC")]

# Keep only complete blocks (all four values); nothing is filled in
cat("Incomplete blocks left out:\n")
print(wide[!complete.cases(wide), ], row.names = FALSE)
d <- wide[complete.cases(wide), ]

d$dSMA <- round(log(d$SMA_MSL / d$SMA_MEC), 4)   # MSL vs MEC change in SMA
d$dPCC <- round(log(d$PCC_MSL / d$PCC_MEC), 4)   # MSL vs MEC change in PCC
d$D    <- round(log(d$SMA_MSL / d$SMA_MEC) - log(d$PCC_MSL / d$PCC_MEC), 4)

cat("\nComplete blocks:", nrow(d), "of 30\n")
print(table(d$subject))

write.csv(d, "final/step2_D.csv", row.names = FALSE)
write.csv(merge(dat[, 1:6], d[, 1:2]), "step2_blocks_long.csv", row.names = FALSE)  # the 104 values used
