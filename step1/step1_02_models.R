# =============================================================================
# Step 1: glutamate across condition, session and region
#   1A  log_glu ~ condition * session * region + (1 | subject)
#   1B  same + (1 | subject:condition:session)     <- final Step-1 model
# Settings (Obai): categorical factors, sum coding, REML,
#                  Type-III ANOVA with Satterthwaite df
# Outputs:
#   table1_1_F_p_1A_vs_1B.csv      F and p for the 7 terms, 1A vs 1B
#   table1_2_model_comparison.csv  subject/visit/residual SD, AIC, BIC, logLik
#   table1_3_final_step1_1B.csv    final table (1B): F, num df, den df, p, question
# Run with working directory = this folder. Needs: install.packages("lmerTest")
# =============================================================================

library(lmerTest)

# ---- Data ----------------------------------------------------------------------
dat <- read.csv("step1_input.csv")

dat$condition <- factor(dat$condition, levels = c("MEC", "MSL"))
dat$session   <- factor(dat$session,   levels = 1:5)
dat$region    <- factor(dat$region,    levels = c("PCC", "SMA"))
dat$subject   <- factor(dat$subject)

# Sum coding: each level is compared with the average over levels
contrasts(dat$condition) <- contr.sum(2)
contrasts(dat$session)   <- contr.sum(5)
contrasts(dat$region)    <- contr.sum(2)

# ---- Models (REML) -------------------------------------------------------------
m1A <- lmer(log_glu ~ condition * session * region + (1 | subject),
            data = dat, REML = TRUE)

m1B <- lmer(log_glu ~ condition * session * region +
              (1 | subject) + (1 | subject:condition:session),
            data = dat, REML = TRUE)

cat("1B singular fit (visit SD ~ 0)?", isSingular(m1B), "\n")

# ---- Type-III ANOVA, Satterthwaite df --------------------------------------------
aA <- anova(m1A, type = 3, ddf = "Satterthwaite")
aB <- anova(m1B, type = 3, ddf = "Satterthwaite")

# ---- Table 1.1: F and p, 1A vs 1B ------------------------------------------------
t11 <- data.frame(term = rownames(aA),
                  F_1A = round(aA$`F value`, 2), p_1A = round(aA$`Pr(>F)`, 3),
                  F_1B = round(aB$`F value`, 2), p_1B = round(aB$`Pr(>F)`, 3))

# ---- Table 1.2: model comparison ---------------------------------------------
sds <- function(m) {
  vc <- as.data.frame(VarCorr(m))
  get <- function(g) if (g %in% vc$grp) vc$sdcor[vc$grp == g] else NA
  c(subject_SD  = get("subject"),
    visit_SD    = get("subject:condition:session"),
    residual_SD = get("Residual"),
    AIC = AIC(m), BIC = BIC(m), logLik = as.numeric(logLik(m)))
}
t12 <- data.frame(model = c("1A", "1B"), round(rbind(sds(m1A), sds(m1B)), 3))

# ---- Table 1.3: final Step-1 table (1B) --------------------------------------------
questions <- c(
  "condition"                = "Averaged over sessions and regions, is glutamate different after MSL than after MEC?",
  "session"                  = "Averaged over condition and region, does glutamate change across the day (Sessions 1-5)?",
  "region"                   = "Averaged over condition and session, is glutamate different in SMA than in PCC?",
  "condition:session"        = "Does the MSL-MEC difference change from session to session?",
  "condition:region"         = "Is the MSL-MEC difference different in SMA than in PCC (averaged over sessions)?",
  "session:region"           = "Do SMA and PCC follow different daytime trajectories?",
  "condition:session:region" = "Does the SMA-vs-PCC difference in the MSL-MEC effect change across sessions?"
)
t13 <- data.frame(term     = rownames(aB),
                  F        = round(aB$`F value`, 2),
                  num_df   = aB$NumDF,
                  den_df   = round(aB$DenDF, 1),
                  p        = round(aB$`Pr(>F)`, 3),
                  question = questions[rownames(aB)])

# ---- Print and save ----------------------------------------------------------------
cat("\nTable 1.1  F and p, Step 1A vs Step 1B\n");   print(t11, row.names = FALSE)
cat("\nTable 1.2  Model comparison\n");              print(t12, row.names = FALSE)
cat("\nTable 1.3  Final Step-1 table (Step 1B)\n");  print(t13, row.names = FALSE)

write.csv(t11, "table1_1_F_p_1A_vs_1B.csv",     row.names = FALSE)
write.csv(t12, "table1_2_model_comparison.csv", row.names = FALSE)
write.csv(t13, "table1_3_final_step1_1B.csv",   row.names = FALSE)
