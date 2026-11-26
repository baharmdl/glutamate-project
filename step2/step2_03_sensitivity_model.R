# Step 2 - 03: sensitivity with all available regional MSL/MEC pairs
# dGlu = log(Glu_MSL / Glu_MEC);  dGlu ~ region * session + (1 | subject) + (1 | subject:session)
# sum coding, REML, Satterthwaite df; SMA - PCC computed explicitly with emmeans
library(lmerTest)
library(emmeans)

dat <- read.csv("../step1 v3/step1_input.csv")

# One row per subject x session x region; keep rows with both MSL and MEC
p <- reshape(dat[, c("subject", "session", "region", "condition", "glutamate")],
             idvar = c("subject", "session", "region"), timevar = "condition", direction = "wide")
p <- p[complete.cases(p), ]
p$dGlu <- log(p$glutamate.MSL / p$glutamate.MEC)
cat("Regional pairs used:", nrow(p), "\n")
write.csv(p, "step2_dGlu_long.csv", row.names = FALSE)

p$region  <- factor(p$region, levels = c("SMA", "PCC"))
p$session <- factor(p$session)
contrasts(p$region)  <- contr.sum(2)
contrasts(p$session) <- contr.sum(5)

m <- lmer(dGlu ~ region * session + (1 | subject) + (1 | subject:session), data = p, REML = TRUE)

# SMA - PCC, averaged equally over the 5 sessions
con <- summary(contrast(emmeans(m, ~ region, lmer.df = "satterthwaite"), list("SMA - PCC" = c(1, -1))), infer = TRUE)

out <- c(capture.output(summary(m)), capture.output(anova(m, type = 3)),
         capture.output(con), paste("Singular fit:", isSingular(m)))
writeLines(out, "final/step2_sensitivity_model_output.Rout")
cat(out, sep = "\n")

write.csv(data.frame(estimate = round(con$estimate, 3), CI95_low = round(con$lower.CL, 3),
                     CI95_high = round(con$upper.CL, 3), p = round(con$p.value, 3)),
          "step2_sensitivity_contrast.csv", row.names = FALSE)
