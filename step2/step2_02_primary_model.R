# Step 2 - 02: primary model  D ~ session + (1 | subject)
# session categorical, sum coding (intercept = average D over the 5 sessions),
# REML, Satterthwaite df (lmerTest default)
library(lmerTest)
library(emmeans)

d <- read.csv("final/step2_D.csv")
d$session <- factor(d$session)
d$subject <- factor(d$subject)
contrasts(d$session) <- contr.sum(5)

m <- lmer(D ~ session + (1 | subject), data = d, REML = TRUE)
s <- summary(m)
a <- anova(m, type = 3)                     # session omnibus test
out <- c(capture.output(s), capture.output(a), paste("Singular fit:", isSingular(m)))
writeLines(out, "final/step2_primary_model_output.Rout")
cat(out, sep = "\n")

# Average D (intercept), 95% CI, back-transform 100 * (exp(x) - 1)
co  <- s$coefficients["(Intercept)", ]
ci  <- co[["Estimate"]] + c(-1, 1) * qt(0.975, co[["df"]]) * co[["Std. Error"]]
pct <- function(x) round(100 * (exp(x) - 1), 1)
sd_subject <- as.data.frame(VarCorr(m))$sdcor[1]

t21 <- data.frame(
  quantity = c("number of subjects", "number of possible subject x session blocks",
               "number of complete blocks analysed", "estimated mean D (log units)",
               "95% CI lower (log units)", "95% CI upper (log units)",
               "back-transformed D, 100*(exp(D)-1) (%)", "back-transformed 95% CI lower (%)",
               "back-transformed 95% CI upper (%)", "p-value for mean D",
               "ANOVA p-value for session", "subject random-effect SD", "residual SD",
               "singular/boundary fit reported by R"),
  value = c(6, 30, nrow(d),
            round(co[["Estimate"]], 3), round(ci, 3),
            pct(co[["Estimate"]]), pct(ci),
            round(co[["Pr(>|t|)"]], 3), round(a$`Pr(>F)`, 3),
            round(sd_subject, 3), round(sigma(m), 3),
            ifelse(isSingular(m), "yes", "no")))
print(t21, row.names = FALSE)
write.csv(t21, "final/table2_1_primary_contrast.csv", row.names = FALSE)

# Model mean D per session, used only for Figure 2.1
em <- as.data.frame(emmeans(m, ~ session, lmer.df = "satterthwaite"))
write.csv(data.frame(session = em$session, mean_D = round(em$emmean, 4),
                     CI95_low = round(em$lower.CL, 4), CI95_high = round(em$upper.CL, 4)),
          "step2_session_means.csv", row.names = FALSE)
