# Moderation of PFA-ABCDE Effectiveness on PTSD Symptom Trajectories: Exploratory Analysis

**Project:** PhD Paper 4 — Rodrigo A. Figueroa (Pontificia Universidad Católica de Chile)
**Supervisors:** Chris Hoeboer, Miranda Olff (Amsterdam UMC)
**AI disclosure:** Claude Opus 4 assisted with coding and methodological review. All decisions reviewed and approved by Figueroa.
**Document initiated:** 2026-04-04
**Last updated:** 2026-05-28

---

## Index

- [Section 0 — Project overview](#section-0-project-overview)
- [Section 1 — Environment setup](#section-1-environment-setup)
- [Section 2 — Pooling justification](#section-2-pooling-justification)
- [Section 3 — Data preparation](#section-3-data-preparation)
- [Section 4 — Descriptive statistics and baseline comparisons](#section-4-descriptive-statistics-and-baseline-comparisons)
- [Section 5 — Missing data and dropout analysis](#section-5-missing-data-and-dropout-analysis)
- [Section 6 — Model specification](#section-6-model-specification)
- [Section 7 — Multiple imputation](#section-7-multiple-imputation)
- [Section 8 — PFA main effect — pooled model (MI)](#section-8-pfa-main-effect--pooled-model-mi)
- [Section 9 — Moderation analysis (MI)](#section-9-moderation-analysis-mi)
- [Section 10 — Sensitivity analyses](#section-10-sensitivity-analyses)
- [Section 11 — Effect sizes and clinical significance](#section-11-effect-sizes-and-clinical-significance)
- [Section 12 — Summary of results](#section-12-summary-of-results)
- [Section 13 — Computational environment](#section-13-computational-environment)
- [Appendix A — Variable codebook](#appendix-a-variable-codebook)
- [Appendix B — Outstanding methodological decisions](#appendix-b-outstanding-methodological-decisions)

---

## Section 0 Project overview

This document presents an exploratory pooled analysis of two randomized controlled trials evaluating Psychological First Aid (PFA-ABCDE) against psychoeducation in adults presenting to Chilean emergency departments after recent trauma.

**Study 1** (Figueroa et al., 2022, EJPT 13:1; N=221, 5 EDs, follow-up at 0/1/6 months) found PFA reduced PCL at 1 month (d=0.42) but not at 6 months. **Study 2** (Figueroa et al., 2024, EJPT 15:1; N=166, 2 EDs, follow-up at 0/1/3 months) found no significant PFA effect at 3 months (p=.148). Neither trial was powered for moderation analysis. Pooling both datasets (N=387) enables two objectives: (1) a systematic moderator screen across seven baseline characteristics, and (2) re-estimation of the overall PFA main effect with greater power.

Both trials shared the same intervention protocol, active control (psychoeducation), measurement instruments (PCL baseline and follow-up, BDI-II, PDEQ, TQ), provider training program, and randomization procedure. The analysis is framed as exploratory and hypothesis-generating.

---

## Section 1 Environment setup

### 1.1 System dependencies

The R packages `mice`, `mitml`, `lme4`, and `car` depend on `nloptr`, which requires CMake (≥ 3.15) for source compilation. Install before launching R:

```sh
# macOS (Homebrew)
brew install cmake nlopt

# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y cmake libnlopt-dev libxml2-dev libssl-dev libcurl4-openssl-dev

# Fedora/RHEL
sudo dnf install -y cmake NLopt-devel libxml2-devel openssl-devel libcurl-devel

# Windows: install Rtools (matching R version) from https://cran.r-project.org/bin/windows/Rtools/
```

### 1.2 R packages

```r
required <- c(
  "foreign", "dplyr", "tidyr",
  "nlme", "lme4", "nloptr",
  "mice", "mitml", "jomo", "pbkrtest",
  "tableone", "car", "parameters", "effectsize",
  "ggplot2", "patchwork"
)

to_install <- required[!sapply(required, requireNamespace, quietly = TRUE)]
if (length(to_install) > 0) {
  install.packages(to_install, repos = "https://cran.r-project.org",
                   Ncpus = 4, quiet = TRUE)
}

missing_after <- required[!sapply(required, requireNamespace, quietly = TRUE)]
if (length(missing_after) > 0) {
  stop("Packages still missing after install: ",
       paste(missing_after, collapse = ", "),
       ". Check that Section 1.1 system dependencies are installed.")
} else {
  message("All ", length(required), " required R packages are installed.")
}
```

Package versions at time of definitive run: R 4.5.3, nlme 3.1.168, mice 3.19.0, mitml 0.4.5, lme4 2.0.1, dplyr 1.2.1, tidyr 1.3.2, ggplot2 4.0.2, tableone 0.13.2, car 3.1.5.

### 1.3 Data loading

```r
suppressPackageStartupMessages({
  library(foreign)
  library(nlme)
  library(mice)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
})

data_wide <- read.spss("data/1903161009_PAP.sav", to.data.frame = TRUE)
cat("Dimensions:", nrow(data_wide), "rows x", ncol(data_wide), "columns\n")
```

**Result:** `Dimensions: 387 rows x 116 columns`

Key variable mapping from SPSS (full codebook in [Appendix A](#appendix-a-variable-codebook)):

| Analysis variable | SPSS column | Notes |
|---|---|---|
| PCL baseline | `t0_pcl_tot` | |
| PCL 1-month | `t1_pcl_tot` | |
| PCL 3-month | `t2_pcl_tot` | Study 2 only |
| PCL 6-month | `t3_pcl_tot` | Study 1 only |
| Treatment | `t0_tx` | PE (control) / PFA |
| Provider | `t0_provider` | |
| Study wave | `t0_recr_wave` | `first` = Study 1, `second` = Study 2 |
| Hospital | `t0_hospital` | |

Harmonized endpoint: `pcl_endpoint = coalesce(t3_pcl_tot, t2_pcl_tot)` — 6-month for Study 1, 3-month for Study 2.

---

## Section 2 Pooling justification

### 2.1 The two studies

| Feature | Study 1 (2022) | Study 2 (2024) |
|---|---|---|
| N randomized | 221 | 166 |
| Emergency departments | 5 (3 public, 2 private) | 2 (1 public, 1 private) |
| Follow-up | 0, 1, 6 months | 0, 1, 3 months |
| Intentional trauma | Excluded | Included (18/166) |
| Providers | 15 (5 of whom continued into Study 2) | 5 (all had previously served in Study 1) |
| Primary result | PCL lower at 1 mo (d=0.42); not at 6 mo | Not significant at 3 mo (p=.148) |

The 5 Study 2 providers are a strict subset of the 15 Study 1 providers — provider pools overlap rather than being disjoint. This has implications for the provider-clustering sensitivity analysis (Section 10.2) and for the limitations discussion (Section 12.4 #4).

### 2.2 Rationale for combining

Neither trial was powered for moderation. Pooling enables a systematic moderator screen and a more precise main-effect estimate. The studies share protocol, instruments, and team. Differences in follow-up duration, sites, and inclusion criteria are addressed by including `study` as a covariate in all models and by evaluating the combination empirically.

### 2.3 Empirical endpoint comparison

```r
d$study <- ifelse(as.character(d$t0_recr_wave) == "first", 1L, 2L)
d$pfa <- ifelse(d$t0_tx == "PFA", 1, 0)
d$pcl_0 <- d$t0_pcl_tot
d$pcl_endpoint <- ifelse(d$study == 1, d$t3_pcl_tot, d$t2_pcl_tot)

ep <- d[!is.na(d$pcl_endpoint), ]

# Unadjusted
t.test(pcl_endpoint ~ study, data = ep)
wilcox.test(pcl_endpoint ~ study, data = ep)

# Adjusted (ANCOVA: pcl_0 + pfa)
ep_cc <- ep[!is.na(ep$pcl_0) & !is.na(ep$pfa), ]
ancova <- lm(pcl_endpoint ~ factor(study) + pcl_0 + factor(pfa), data = ep_cc)
summary(ancova)
```

**Results:**

| Comparison | Study 1 (6 mo) | Study 2 (3 mo) | Difference | p |
|---|---|---|---|---|
| Unadjusted means | 33.47 | 30.90 | 2.57 | 0.231 |
| Adjusted (pcl_0 + pfa) | 34.70 | 32.28 | 2.42 | 0.210 |
| Cohen's d (unadjusted) | — | — | 0.18 | — |

Endpoint PCL scores do not differ significantly between studies.

### 2.4 Omnibus interaction test

```r
suppressPackageStartupMessages({ library(nlme); library(dplyr); library(tidyr) })

d$pfa   <- as.integer(d$t0_tx == "PFA")
d$pcl_0 <- as.numeric(d$t0_pcl_tot)
d$pcl_t0 <- as.numeric(d$t0_pcl_tot)
d$pcl_t1 <- as.numeric(d$t1_pcl_tot)
d$pcl_t2 <- coalesce(as.numeric(d$t3_pcl_tot), as.numeric(d$t2_pcl_tot))
d$id    <- as.integer(d$t0_code)

dl <- d %>%
  dplyr::select(id, study, pfa, pcl_0, pcl_t0, pcl_t1, pcl_t2) %>%
  tidyr::pivot_longer(cols = c(pcl_t0, pcl_t1, pcl_t2),
                      names_to = "time_label", values_to = "pcl") %>%
  dplyr::mutate(time = dplyr::case_when(
                  time_label == "pcl_t0" ~ 0L,
                  time_label == "pcl_t1" ~ 1L,
                  time_label == "pcl_t2" ~ 2L)) %>%
  dplyr::select(-time_label) %>%
  dplyr::arrange(id, time)

dl$t01 <- pmin(dl$time, 1)
dl$t12 <- pmax(dl$time - 1, 0)
dl_cc <- dl[!is.na(dl$pcl) & !is.na(dl$pcl_0), ]

# Reduced model: study as covariate only
m0 <- lme(pcl ~ t01*pfa + t12*pfa + pcl_0 + factor(study),
           random = ~1|id, data = dl_cc, method = "ML",
           control = lmeControl(opt = "optim"))

# Full model: study interacts with pfa × time
m1 <- lme(pcl ~ t01*pfa*factor(study) + t12*pfa*factor(study) + pcl_0,
           random = ~1|id, data = dl_cc, method = "ML",
           control = lmeControl(opt = "optim"))

anova(m0, m1)
summary(m1)$tTable
```

**Results.** Long format: 711 rows from 367 subjects (complete cases on `pcl` and `pcl_0`).

Omnibus LRT (5 df): χ² = 8.54, p = 0.129 — not significant. Combining is justified.

Individual interaction coefficients from the full model (shown for transparency; the formal pooling decision rests on the omnibus LRT above):

| Term | Estimate | SE | t | p |
|---|---|---|---|---|
| t01:pfa:study2 | 4.15 | 3.59 | 1.16 | 0.248 |
| pfa:study2:t12 | −8.82 | 4.22 | −2.09 | 0.038 |
| t01:study2 | −5.45 | 2.48 | −2.20 | 0.029 |
| pfa:study2 | −0.22 | 2.07 | −0.11 | 0.915 |
| study2:t12 | 5.83 | 2.98 | 1.96 | 0.051 |

The omnibus test supports combining. The focal `pfa:study2:t12` coefficient (p = 0.038) indicates the late-slope PFA effect may differ between studies — explored further in Section 8.3.

### 2.5 Study-specific PFA estimates and Clogg-Paternoster test

The previous subsection reports interaction coefficients from a *single* fully-interacted model. This subsection reports the *same comparison* via separate per-study fits plus the Clogg-Paternoster z-test for coefficient equality. The two are not redundant: the omnibus LRT pools information across phases and tests the joint study × treatment × time interaction; the Clogg-Paternoster test focuses on one coefficient (early or late slope) and uses independent per-study standard errors. We retain both because the joint test motivates pooling and the focused test characterizes the divergence.

```r
for (s in 1:2) {
  ds <- dl_cc[dl_cc$study == s, ]
  m <- lme(pcl ~ t01*pfa + t12*pfa + pcl_0,
           random = ~1|id, data = ds, method = "ML",
           control = lmeControl(opt = "optim"))
  print(summary(m)$tTable)
}
```

**Per-study PFA effects:**

| Phase | Study 1 (N=209) | Study 2 (N=158) |
|---|---|---|
| Early (t01:pfa) | b = −5.51, 95% CI [−10.77, −0.24], p = 0.042 | b = −1.35, 95% CI [−5.96, 3.25], p = 0.565 |
| Late (t12:pfa) | b = 5.09, 95% CI [−0.99, 11.16], p = 0.103 | b = −3.68, 95% CI [−9.27, 1.91], p = 0.199 |

**Clogg-Paternoster z-test for coefficient equality:**

```r
m_s1 <- lme(pcl ~ t01*pfa + t12*pfa + pcl_0,
            random = ~1|id, data = dl_cc[dl_cc$study == 1, ],
            method = "ML", control = lmeControl(opt = "optim"))
m_s2 <- lme(pcl ~ t01*pfa + t12*pfa + pcl_0,
            random = ~1|id, data = dl_cc[dl_cc$study == 2, ],
            method = "ML", control = lmeControl(opt = "optim"))

se_direct <- function(m, term) summary(m)$tTable[term, "Std.Error"]
b_direct  <- function(m, term) summary(m)$tTable[term, "Value"]

# Early slope
b1 <- b_direct(m_s1, "t01:pfa"); se1 <- se_direct(m_s1, "t01:pfa")
b2 <- b_direct(m_s2, "t01:pfa"); se2 <- se_direct(m_s2, "t01:pfa")
z_early <- (b1 - b2) / sqrt(se1^2 + se2^2)
p_early <- 2 * (1 - pnorm(abs(z_early)))

# Late slope
b1L <- b_direct(m_s1, "t12:pfa"); se1L <- se_direct(m_s1, "t12:pfa")
b2L <- b_direct(m_s2, "t12:pfa"); se2L <- se_direct(m_s2, "t12:pfa")
z_late <- (b1L - b2L) / sqrt(se1L^2 + se2L^2)
p_late <- 2 * (1 - pnorm(abs(z_late)))
```

| Phase | b₁ − b₂ | z | p |
|---|---|---|---|
| Early (t01:pfa) | −4.16 | −1.17 | 0.244 |
| Late (t12:pfa) | 8.77 | 2.08 | 0.037 |

Early-slope coefficients are compatible between studies. Late-slope coefficients differ significantly — opposite signs, neither individually significant.

### 2.6 Decision

The omnibus test and endpoint comparison support pooling. `study` enters as a main-effect covariate in all models. The late-slope heterogeneity (opposite-signed per-study `t12:pfa` coefficients, Clogg p = 0.037) is an exploratory observation discussed in Section 8.3.

---

## Section 3 Data preparation

Wide-first workflow: data preparation and MI are performed in wide format (1 row per participant) to guarantee within-subject consistency of imputed baseline covariates. Pivot to long occurs after imputation.

### 3.1 Variable selection and typing

**Why `pcl_0` is excluded from the wide MI dataset and reconstructed afterwards.** The analysis uses `pcl_0` (a time-invariant baseline covariate) and `pcl_t0` (PCL measured at the baseline timepoint). Definitionally `pcl_0 ≡ pcl_t0`. If both enter `mice` with identical missingness patterns, PMM draws independent donors for each, breaking the equality. The simplest solution is to impute only `pcl_t0` in wide format and reconstruct `pcl_0 <- pcl_t0` after `mice::complete()` (Section 7.4).

```r
suppressPackageStartupMessages({ library(dplyr); library(tidyr) })

d_raw <- foreign::read.spss("data/1903161009_PAP.sav",
                            to.data.frame = TRUE, reencode = "UTF-8")
stopifnot(nrow(d_raw) == 387)

analysis_wide <- d_raw %>%
  transmute(
    id          = as.integer(t0_code),
    study       = ifelse(as.character(t0_recr_wave) == "first", 1L, 2L),
    pfa         = as.integer(t0_tx == "PFA"),
    provider    = trimws(as.character(t0_provider)),
    hospital    = as.character(t0_hospital),
    p_hospital  = as.integer(hospital %in% c("SOTERO", "BARROS LUCO", "PADRE HURTADO")),
    pcl_t0      = as.numeric(t0_pcl_tot),
    bdi_0       = as.numeric(t0_bdi),
    pdeq        = as.numeric(t0_pdeq),
    tq          = as.numeric(t0_tq),
    sex         = as.integer(t0_sex == "female"),
    educ        = as.numeric(t0_years_educ),
    age         = as.numeric(t0_age),
    intent      = as.integer(t0_tx_int == "Yes"),
    pcl_t1      = as.numeric(t1_pcl_tot),
    pcl_t2      = coalesce(as.numeric(t3_pcl_tot), as.numeric(t2_pcl_tot))
  )
```

**Results:**

- Dimensions: 387 rows × 16 cols
- Unique IDs: 387 (range 1–388; gap at ID = 386)

Binary coding:
- `pfa`: 0 = PE control, 1 = PFA
- `sex`: 0 = male, 1 = female
- `p_hospital`: 0 = private (ACHS, UC), 1 = public (Sótero del Río, Padre Hurtado, Barros Luco)
- `intent`: 0 = accidental, 1 = intentional

PFA × Study: Study 1: 112 PE / 109 PFA; Study 2: 88 PE / 78 PFA.

**Providers:** 15 distinct providers across the two studies. All 5 Study 2 providers were drawn from the Study 1 provider pool (i.e., the 5 form a strict subset of the 15). This overlap structure is relevant to Section 6.2 (random effects) and Section 10.2 (provider-clustering sensitivity).

`intent`: Study 1 = 0 intentional (by design); Study 2 = 18 intentional + 5 NA.

### 3.2 Structural notes

- `intent` is nested within Study 2 — `intent × pfa × time` is tested within Study 2 only (Section 9.1).
- `p_hospital` is a public-vs-private contrast based on funding/ownership: public = MINSAL hospitals (Sótero del Río, Padre Hurtado, Barros Luco); private = ACHS (a workplace-insurance mutualidad) and UC (university hospital). The coefficient is interpreted as a public-vs-private hospital contrast and is not used as an SES proxy.
- Study-2 allocation imbalance (88/78, 6%) is larger than expected under block randomization. Analyzed as ITT per protocol; residual imbalance absorbed by covariates.

### 3.3 Pivot function

```r
pivot_to_long <- function(df_wide) {
  stopifnot("pcl_0" %in% names(df_wide))
  df_wide %>%
    tidyr::pivot_longer(
      cols      = c(pcl_t0, pcl_t1, pcl_t2),
      names_to  = "time_label",
      values_to = "pcl"
    ) %>%
    mutate(
      time = dplyr::case_when(
        time_label == "pcl_t0" ~ 0L,
        time_label == "pcl_t1" ~ 1L,
        time_label == "pcl_t2" ~ 2L
      ),
      t01 = pmin(time, 1L),
      t12 = pmax(time - 1L, 0L)
    ) %>%
    dplyr::select(-time_label) %>%
    dplyr::arrange(id, time)
}

analysis_long_cc <- pivot_to_long(analysis_wide %>% mutate(pcl_0 = pcl_t0))
```

**Results:**

- Long-format rows: 1161 (387 × 3)
- Observed PCL per time: t=0: 367 observed / 20 missing; t=1: 187 / 200; t=2: 171 / 216
- Piecewise mapping: `(time, t01, t12) = (0,0,0), (1,1,0), (2,1,1)` — correct.

**Justification for piecewise modeling.** A piecewise specification with knot at month 1 is preferred over a single linear slope or quadratic term because (i) PFA-ABCDE is theoretically an early-phase intervention; the relevant comparison between arms is at month 1, when the intervention's mechanism (peritraumatic stabilization) is expected to peak. (ii) The control-arm trajectories are visibly non-linear: roughly flat from baseline to month 1, then declining (natural recovery and any delayed psychoeducation effect). A single slope or quadratic blends those two phases and obscures the early treatment contrast. (iii) Piecewise slopes give two interpretable coefficients per arm — `t01:pfa` for the acute window, `t12:pfa` for the recovery window — each of which can be moderated separately (Section 9). A quadratic would not yield phase-specific moderator tests.

### 3.4 Verification

```r
chk <- function(lbl, x) cat(sprintf("  %-35s %s\n", lbl, ifelse(isTRUE(x), "PASS", "FAIL")))
chk("N = 387 unique ids",        length(unique(analysis_wide$id)) == 387)
chk("No duplicate ids",          !any(duplicated(analysis_wide$id)))
chk("Study 1 N = 221",           sum(analysis_wide$study == 1) == 221)
chk("Study 2 N = 166",           sum(analysis_wide$study == 2) == 166)
chk("pfa in {0,1}",              all(analysis_wide$pfa %in% c(0,1)))
chk("study in {1,2}",            all(analysis_wide$study %in% c(1,2)))
chk("p_hospital in {0,1}",       all(analysis_wide$p_hospital %in% c(0,1)))
chk("sex in {0,1}",              all(analysis_wide$sex %in% c(0,1)))
chk("intent in {0,1,NA}",        all(analysis_wide$intent %in% c(0,1) | is.na(analysis_wide$intent)))
pcl_all <- c(analysis_wide$pcl_t0, analysis_wide$pcl_t1, analysis_wide$pcl_t2)
chk("PCL within [17,85]",        all(pcl_all >= 17 & pcl_all <= 85, na.rm = TRUE))
chk("BDI within [0,63]",         all(analysis_wide$bdi_0 >= 0 & analysis_wide$bdi_0 <= 63, na.rm = TRUE))
chk("PDEQ within [10,50]",       all(analysis_wide$pdeq >= 10 & analysis_wide$pdeq <= 50, na.rm = TRUE))
chk("Long rows = 3 * N",         nrow(analysis_long_cc) == 3 * 387)

saveRDS(analysis_wide, "outputs/analysis_wide.rds")
saveRDS(pivot_to_long, "outputs/pivot_to_long.rds")
```

All 13 checks PASS. Missingness per variable (wide): pcl_t0=20, bdi_0=27, pdeq=25, tq=26, educ=25, age=11, intent=5, pcl_t1=200, pcl_t2=216.

---

## Section 4 Descriptive statistics and baseline comparisons

### 4.1 Overall sample

```r
suppressPackageStartupMessages({
  library(dplyr); library(tidyr); library(tableone); library(ggplot2)
})

d <- readRDS("outputs/analysis_wide.rds")

cont_vars <- c("pcl_t0","bdi_0","pdeq","tq","educ","age","pcl_t1","pcl_t2")
cat_vars  <- c("pfa","study","sex","p_hospital","intent")
tab1 <- CreateTableOne(vars = c(cont_vars, cat_vars), data = d,
                       factorVars = cat_vars)
print(tab1, smd = FALSE, test = FALSE, showAllLevels = TRUE)
```

| Variable | Overall (N = 387) |
|---|---|
| PCL baseline, mean (SD) | 40.79 (16.65) |
| BDI-II, mean (SD) | 16.35 (11.67) |
| PDEQ, mean (SD) | 24.85 (11.41) |
| Prior traumas, mean (SD) | 2.67 (2.18) |
| Education (years), mean (SD) | 11.64 (3.96) |
| Age (years), mean (SD) | 45.38 (15.59) |
| Female, n (%) | 239 (61.8%) |
| Public hospital, n (%) | 357 (92.2%) |
| Intentional trauma, n (%) | 18 (4.7%) |

### 4.2 Randomization check (PFA vs control)

```r
base_vars <- c("pcl_t0","bdi_0","pdeq","tq","educ","age","sex","p_hospital","intent","study")
tab2 <- CreateTableOne(vars = base_vars, strata = "pfa", data = d,
                       factorVars = c("sex","p_hospital","intent","study"),
                       test = TRUE)
print(tab2, smd = FALSE, showAllLevels = TRUE)
```

| Variable | Control (N=200) | PFA (N=187) | p |
|---|---|---|---|
| PCL baseline | 41.39 (16.22) | 40.14 (17.13) | 0.472 |
| BDI-II | 16.74 (12.21) | 15.91 (11.06) | 0.501 |
| PDEQ | 24.65 (11.39) | 25.07 (11.46) | 0.723 |
| Prior traumas | 2.59 (2.20) | 2.75 (2.16) | 0.489 |
| Education | 11.83 (4.14) | 11.43 (3.76) | 0.341 |
| Age | 43.71 (16.31) | 47.19 (14.59) | 0.030 |
| Female (%) | 58.0% | 65.8% | 0.142 |
| Public hospital (%) | 92.0% | 92.5% | 1.000 |
| Intentional (%) | 5.0% | 4.4% | 0.953 |
| Study 2 (%) | 44.0% | 41.7% | 0.725 |

The table tests 10 variables; of these, 9 are baseline covariates (`study` is a design indicator included for transparency). One of the 9 baseline tests is significant (age, p=0.030, PFA arm 3.5 years older). Under the null, E[#sig at α=0.05] = 0.45 — one significant result is what chance predicts. Age enters all models as `ns(age, df=2)`.

### 4.3 Between-study comparison

```r
base_vars_s <- c("pcl_t0","bdi_0","pdeq","tq","educ","age","sex","p_hospital","pfa")
tab3 <- CreateTableOne(vars = base_vars_s, strata = "study", data = d,
                       factorVars = c("sex","p_hospital","pfa"),
                       test = TRUE)
print(tab3, smd = FALSE, showAllLevels = TRUE)
```

| Variable | Study 1 (N=221) | Study 2 (N=166) | p |
|---|---|---|---|
| PCL baseline | 40.24 (15.78) | 41.52 (17.76) | 0.468 |
| BDI-II | 17.41 (11.94) | 14.92 (11.19) | 0.046 |
| PDEQ | 26.23 (12.06) | 22.99 (10.21) | 0.007 |
| Prior traumas | 2.73 (2.25) | 2.60 (2.09) | 0.574 |
| Education | 11.11 (4.26) | 12.29 (3.45) | 0.005 |
| Age | 48.57 (16.35) | 41.21 (13.48) | <0.001 |
| Female (%) | 58.8% | 65.7% | 0.206 |

Four variables differ between studies (BDI, PDEQ, education, age). These differences are the reason `study` is a covariate in every model.

### 4.4 PCL trajectories

```r
dl <- d %>% mutate(pcl_0 = pcl_t0) %>%
  pivot_longer(cols = c(pcl_t0, pcl_t1, pcl_t2),
               names_to = "time_label", values_to = "pcl") %>%
  mutate(time = dplyr::case_when(
           time_label == "pcl_t0" ~ 0L,
           time_label == "pcl_t1" ~ 1L,
           time_label == "pcl_t2" ~ 2L),
         study_lbl = ifelse(study == 1, "Study 1 (endpoint 6 months)",
                            "Study 2 (endpoint 3 months)"),
         arm = ifelse(pfa == 1, "PFA", "Control (PE)"))

traj <- dl %>% filter(!is.na(pcl)) %>%
  group_by(study_lbl, arm, time) %>%
  summarise(n = n(), m = mean(pcl), se = sd(pcl)/sqrt(n()),
            lo = m - 1.96*se, hi = m + 1.96*se, .groups = "drop")

p <- ggplot(traj, aes(x = time, y = m, colour = arm, group = arm)) +
  geom_line(linewidth = 0.9) + geom_point(size = 2.5) +
  geom_errorbar(aes(ymin = lo, ymax = hi), width = 0.08) +
  facet_wrap(~ study_lbl) +
  scale_x_continuous(breaks = 0:2, labels = c("Baseline","1 month","Endpoint")) +
  scale_colour_manual(values = c("Control (PE)" = "#4e79a7", "PFA" = "#e15759")) +
  labs(x = NULL, y = "PCL total (mean ± 95% CI)", colour = NULL,
       title = "PCL trajectories by arm and study") +
  theme_bw(base_size = 11) + theme(legend.position = "top")

ggsave("outputs/fig_4_4_trajectories.png", p, width = 8, height = 4, dpi = 150)
```

**Retention by wave:**

| Study | Baseline | 1 month | Endpoint |
|---|---|---|---|
| Study 1 | 209/221 (95%) | 65/221 (29%) | 91/221 (41%) |
| Study 2 | 158/166 (95%) | 122/166 (73%) | 80/166 (48%) |

Study 1 retains only 29% at 1 month. Pooled retention: 48% at 1 month, 44% at endpoint.

---

## Section 5 Missing data and dropout analysis

### 5.1 Missingness pattern

```r
suppressPackageStartupMessages({ library(dplyr); library(tidyr); library(splines) })
d <- readRDS("outputs/analysis_wide.rds")
d$drop_t1  <- as.integer(is.na(d$pcl_t1))
d$drop_end <- as.integer(is.na(d$pcl_t2))

key <- c("pcl_t0","bdi_0","pdeq","tq","educ","age","intent","pcl_t1","pcl_t2")
miss_overall <- sapply(d[, key], function(x) sum(is.na(x)))
print(miss_overall)
```

| Variable | Overall NA | Study 1 | Study 2 | Control | PFA |
|---|---|---|---|---|---|
| pcl_t0 | 20 | 12 | 8 | 8 | 12 |
| bdi_0 | 27 | 14 | 13 | 10 | 17 |
| pdeq | 25 | 13 | 12 | 12 | 13 |
| tq | 26 | 19 | 7 | 13 | 13 |
| educ | 25 | 19 | 6 | 11 | 14 |
| age | 11 | 8 | 3 | 4 | 7 |
| intent | 5 | 0 | 5 | 1 | 4 |
| pcl_t1 | 200 | 156 | 44 | 102 | 98 |
| pcl_t2 | 216 | 130 | 86 | 116 | 100 |

Baseline NAs are low (1–7% per variable) and balanced across arms and studies. Follow-up missingness is heavily Study-1-loaded at 1 month (156/200 pooled NAs) but roughly balanced at endpoint.

### 5.2 Dropout symmetry

```r
test_arm <- function(x, y, label) {
  tab <- table(x, y)
  tst <- suppressWarnings(chisq.test(tab))
  cat(sprintf("%-40s chi-sq=%.3f p=%.3f\n", label, tst$statistic, tst$p.value))
}
test_arm(d$pfa, d$drop_t1,  "Dropout T1 x arm (pooled)")
test_arm(d$pfa[d$study==1], d$drop_t1[d$study==1],  "Dropout T1 x arm (Study 1)")
test_arm(d$pfa[d$study==2], d$drop_t1[d$study==2],  "Dropout T1 x arm (Study 2)")
test_arm(d$pfa, d$drop_end, "Dropout endpoint x arm (pooled)")
test_arm(d$pfa[d$study==1], d$drop_end[d$study==1], "Dropout endpoint x arm (Study 1)")
test_arm(d$pfa[d$study==2], d$drop_end[d$study==2], "Dropout endpoint x arm (Study 2)")
```

| Test | χ² | p |
|---|---|---|
| Dropout T1 × arm (pooled) | 0.110 | 0.740 |
| Dropout T1 × arm (Study 1) | 0.045 | 0.832 |
| Dropout T1 × arm (Study 2) | 0.000 | 1.000 |
| Dropout endpoint × arm (pooled) | 0.668 | 0.414 |
| Dropout endpoint × arm (Study 1) | 0.150 | 0.699 |
| Dropout endpoint × arm (Study 2) | 0.221 | 0.638 |

All six tests non-significant (all p > 0.4). No differential attrition between arms.

### 5.3 Predictors of dropout

`age` enters the dropout model as a natural-cubic spline (`ns(age, df = 2)`), consistent with all primary and sensitivity models — this is why a likelihood-ratio test is used to confirm non-linearity rather than a single linear coefficient.

```r
pred_cols <- c("pfa","pcl_t0","bdi_0","pdeq","tq","sex","educ","age","intent","p_hospital","study")
d_cc <- d[complete.cases(d[, pred_cols]), ]

fit_drop <- function(outcome, label) {
  f <- as.formula(paste(outcome, "~ pfa + pcl_t0 + bdi_0 + pdeq + tq + sex + educ +",
                        "ns(age, df = 2) + intent + p_hospital + factor(study)"))
  m <- glm(f, data = d_cc, family = binomial(link = "logit"))
  co <- summary(m)$coefficients
  or    <- exp(co[, "Estimate"])
  or_lo <- exp(co[, "Estimate"] - 1.96 * co[, "Std. Error"])
  or_hi <- exp(co[, "Estimate"] + 1.96 * co[, "Std. Error"])
  data.frame(OR = round(or, 2),
             CI95 = sprintf("[%.2f, %.2f]", or_lo, or_hi),
             p = sprintf("%.3f", co[, "Pr(>|z|)"]))
}
fit_drop("drop_t1",  "Dropout at 1 month")
fit_drop("drop_end", "Dropout at endpoint")
```

Complete-case N: 331 of 387. Significant predictors: `sex` (OR 0.55, p=0.028) and `study` (OR 0.16, p<0.001) at T1; `educ` (OR 0.92, p=0.013) and the age spline (OR 0.15, p=0.010) at endpoint. All are in the analytic covariate set. PFA arm is not a significant predictor at either wave. Age spline fits better than linear at endpoint (LRT χ²=5.29, p=0.021). Diagnostics are compatible with MAR conditional on the covariate set.

---

## Section 6 Model specification

### 6.1 Covariates

| Variable | Rationale |
|---|---|
| `pcl_0` | Baseline PTSD severity is the strongest single predictor of outcome PCL; including it as an ANCOVA-style covariate dramatically reduces residual variance and protects against any residual baseline imbalance between arms. Reconstructed post-MI as `pcl_0 = pcl_t0` (Section 3.1, Section 7.4). |
| `bdi_0` | Baseline depression. Comorbid depressive symptoms predict both PTSD persistence and treatment response; conditioning isolates the PFA effect from confounding by acute depressive load. |
| `pdeq` | Peritraumatic dissociation (Ozer et al., 2003 meta-analysis: dissociation is a robust risk factor for chronic PTSD). Adjusts for an established risk axis the trial did not balance on. |
| `sex` | Established PTSD risk factor (≈2× lifetime prevalence in women). Also a T1-dropout predictor in this sample (OR 0.55) — including it improves the MAR plausibility for the imputation model. |
| `educ` | Lower education predicts worse PTSD trajectory and is an endpoint-dropout predictor in this sample (OR 0.92). Same MAR/precision logic as `sex`. |
| `age` | Recovery trajectories are non-linear in age (older adults recover more slowly; the curve is not monotonic). Enters as `ns(age, df = 2)` to capture this without imposing a linear constraint. |
| `intent` | Intentional trauma is consistently associated with worse PTSD prognosis. Nested within Study 2 — moderator tested within Study 2 only (Section 9.1). |
| `tq` | Prior trauma burden (TQ); cumulative trauma is a dose-response risk factor for chronic PTSD. |
| `study` | Two cohorts with different follow-up windows, ED mixes, and inclusion criteria (Section 2.1). Dominant T1-dropout predictor (OR 0.16) — essential as both a precision and MAR-plausibility covariate. |
| `p_hospital` | Public vs. private hospital contrast (see Section 3.2). Controls for any care-channel differences in baseline severity, follow-up adherence, or trauma type. |

**VIF check** (complete-case N=331). Variance Inflation Factor measures how much the variance of a regression coefficient is inflated by collinearity with the other covariates. A VIF of 1 means no collinearity; values above 5 are typically flagged as problematic, above 10 as serious. Maximum VIF in this model = 2.19 (for `pcl_t0`). No covariate approaches 5.0. Despite the near-nesting of `intent` within Study 2, VIF(`intent`) = 1.36 — well within the safe range.

```r
dd <- d[complete.cases(d[, c("pcl_t0","bdi_0","pdeq","tq","sex","educ","age",
                              "intent","p_hospital","study")]), ]
X <- model.matrix(~ pcl_t0 + bdi_0 + pdeq + tq + sex + educ + ns(age, df = 2) +
                  intent + p_hospital + factor(study), data = dd)[, -1]

vif_manual <- function(X) {
  sapply(seq_len(ncol(X)), function(j) {
    r2j <- summary(lm(X[, j] ~ X[, -j]))$r.squared
    1 / (1 - r2j)
  }) %>% setNames(colnames(X))
}
vif_manual(X)
```

### 6.2 Random effects: `random = ~1 | id`

Random intercept per subject, no random slope. At most 3 timepoints with ~50% attrition makes random-slope estimation unstable. The objective is mean treatment effects, not individual trajectories.

**Provider clustering.** ICC_provider (pooled) = 0.027, 95% CI [0.000, 0.082]; Study 2 alone (5 providers) = 0.038 [0.000, 0.148]. Both estimates are below the 0.05 point-estimate threshold typically used to motivate inclusion of a provider random effect. Importantly, the 5 Study 2 providers are a strict subset of the 15 Study 1 providers (Section 3.1), so the provider random effect is identified from within-provider variation that spans both studies — it is *not* confounded with `study` despite each study having its own provider count. Provider enters as a sensitivity analysis in Section 10.2; the primary model omits the provider level because ICC is below the inclusion threshold and the small per-cluster N (especially for the 5-provider Study 2) makes the variance component unreliable.

```r
suppressPackageStartupMessages({
  library(dplyr); library(tidyr); library(nlme); library(lme4)
})
d <- readRDS("outputs/analysis_wide.rds")
pivot_to_long <- readRDS("outputs/pivot_to_long.rds")

dl <- pivot_to_long(d %>% mutate(pcl_0 = pcl_t0))
dl_cc <- dl[!is.na(dl$pcl) & !is.na(dl$pcl_0), ]

m_null_prov <- lme(pcl ~ 1, random = ~1 | provider/id,
                   data = dl_cc, method = "REML",
                   control = lmeControl(opt = "optim"))
VarCorr(m_null_prov)

m4 <- lmer(pcl ~ 1 + (1|provider) + (1|id), data = dl_cc, REML = TRUE)
set.seed(12345)
b <- bootMer(m4, FUN = function(mm) {
  vc <- as.data.frame(VarCorr(mm))
  vp <- vc$vcov[vc$grp == "provider"]
  vi <- vc$vcov[vc$grp == "id"]
  vr <- attr(VarCorr(mm), "sc")^2
  vp / (vp + vi + vr)
}, nsim = 500, re.form = NA, use.u = FALSE, type = "parametric",
parallel = "multicore", ncpus = 4)
quantile(b$t, c(0.025, 0.975), na.rm = TRUE)
```

### 6.3 Assumption checks

**Note on `pcl_0` vs. `pcl_t0`.** These two variables are definitionally equal (`pcl_0 ≡ pcl_t0`) but enter the model in different roles: `pcl_0` is a *time-invariant subject-level covariate* (the same value attached to every row for a given subject — i.e., baseline severity used as an ANCOVA adjustment), while `pcl_t0` is the *outcome value at time 0* (one row per subject, the baseline measurement of the longitudinal PCL outcome). The roles are different even though the values are identical. After multiple imputation we enforce the identity explicitly via `pcl_0 <- pcl_t0` (Section 7.4) to ensure both representations stay in sync.

Complete-case fit (646 long-format rows, 331 subjects):

```r
suppressPackageStartupMessages({
  library(dplyr); library(tidyr); library(nlme); library(splines); library(ggplot2)
})
d <- readRDS("outputs/analysis_wide.rds")
pivot_to_long <- readRDS("outputs/pivot_to_long.rds")
dl <- pivot_to_long(d %>% mutate(pcl_0 = pcl_t0))
dl_cc <- dl[!is.na(dl$pcl) & !is.na(dl$pcl_0) & !is.na(dl$bdi_0) & !is.na(dl$pdeq) &
            !is.na(dl$tq) & !is.na(dl$educ) & !is.na(dl$age) & !is.na(dl$intent), ]

m_primary_cc <- lme(pcl ~ t01*pfa + t12*pfa + pcl_0 + bdi_0 + pdeq + tq + sex +
                    educ + ns(age, df = 2) + intent + p_hospital + factor(study),
                    random = ~1 | id, data = dl_cc, method = "ML",
                    control = lmeControl(opt = "optim"))
```

- **Residual normality.** Shapiro-Wilk rejects (W = 0.9298, p = 8.0e-17), but with n = 646 the test is hyper-sensitive and rejects on trivial departures. QQ plots show moderate tail heaviness, not gross non-normality. The Central Limit Theorem (CLT) protects fixed-effect inference here: with n in the hundreds, the sampling distribution of regression coefficients converges to normal regardless of the residual distribution, so the p-values and CIs for the fixed effects remain valid.
- **Heteroscedasticity.** Residual SD: T0 = 4.39 (n = 331), T1 = 11.96 (n = 165), endpoint = 12.52 (n = 150). The 3× ratio between T0 and follow-up is too large to ignore — a homoscedastic LMM would underestimate uncertainty at follow-up and overstate it at baseline. The fix is `weights = varIdent(form = ~1 | factor(time))`, which allows the residual variance to differ by timepoint; this is used in all primary fits. The T0 compression is partly artefactual: `pcl_0` is a near-perfect predictor of `pcl` at T0 (the tautology discussed in Section 6.4 and Appendix B), so the within-T0 residuals collapse toward zero.
- **Outliers.** 12 observations (1.9%) exceed |z| > 3 (max 4.80). Within the expected range for n = 646; not influential after winsorization sensitivity (not shown).

**Summary verdict.** Heteroscedasticity is addressed structurally via `varIdent`. Residual non-normality is statistically present but practically negligible for fixed-effect inference at this sample size. No assumption is violated to a degree that would invalidate the primary results; the only methodologically substantive consequence is the choice to fit the primary MI model on follow-up observations only, which interacts with the varIdent specification (Section 6.4 and Appendix B).

### 6.4 Piecewise model

Time is parameterized as two piecewise slopes: `t01 = min(time, 1)` (baseline → 1 month) and `t12 = max(time − 1, 0)` (1 month → endpoint). The piecewise form captures the empirically observed trajectory shape (control arm approximately flat T0→T1, then declining T1→T2) and allows phase-specific moderation analysis — important because PFA is theoretically an early-phase intervention.

**Primary main-effect model:**

```
pcl_ij = β₀ + β₁·t01 + β₂·t12 + β₃·pfa + β₄·(t01·pfa) + β₅·(t12·pfa)
       + β₆·study + γ'·X + u_i + ε_ij
```

β₄ (`t01:pfa`) and β₅ (`t12:pfa`) are the pooled phase-specific PFA effects.

**Moderator-screen model** (one per moderator):

```
pcl_ij = ... + β₆·mod + β₇·(t01·mod) + β₈·(t12·mod)
       + β₉·(pfa·mod) + β₁₀·(t01·pfa·mod) + β₁₁·(t12·pfa·mod) + ...
```

β₁₀ and β₁₁ (three-way interactions) are the coefficients of primary interest.

**R implementation (all primary fits):**

```r
# Section 8 — pooled main effect (MI; follow-up observations only — see note below)
m_main <- lme(pcl ~ t12 * pfa +
              pcl_0 + bdi_0 + pdeq + tq + sex + educ + ns(age, df = 2) +
              intent + p_hospital + factor(study),
              random = ~ 1 | id,
              weights = varIdent(form = ~ 1 | factor(time)),
              data = dl_m_fu, method = "ML",   # dl_m_fu = dl_m[dl_m$time > 0, ]
              control = lmeControl(opt = "optim"))

# Section 9 — moderator screen (one per moderator)
m_mod  <- lme(pcl ~ t12 * pfa * mod +
              pcl_0 + bdi_0 + pdeq + tq + sex + educ + ns(age, df = 2) +
              intent + p_hospital + factor(study),
              random = ~ 1 | id,
              weights = varIdent(form = ~ 1 | factor(time)),
              data = dl_m_fu, method = "ML",
              control = lmeControl(opt = "optim"))
```

**Note on follow-up-only parameterization.** Including time = 0 observations in the MI long format creates a numerical issue: `pcl_0 ≡ pcl` at time = 0 (because `pcl_0` is reconstructed as `pcl_t0`). After full imputation, this exact equality holds for all 387 subjects at time = 0, driving the time = 0 residual variance to near zero. `varIdent`, which estimates a separate residual SD per timepoint, cannot distinguish a near-zero variance component from a degenerate model — the result is numerical singularity across all 20 imputations. The standard ANCOVA-LMM resolution is to treat baseline as a pure covariate and model only follow-up outcomes (time = 1 and time = 2). Under this parameterization, the `pfa` main effect captures the arm difference at 1 month conditional on `pcl_0` — equivalent to `t01:pfa` in the 3-timepoint formulation (since the baseline arm difference is zero by randomization). The `t12:pfa` interaction retains its original interpretation (incremental arm difference from 1 month to endpoint).

This choice is methodologically standard for randomized-trial longitudinal analysis (the ANCOVA-with-baseline-covariate approach; see e.g. Liu et al., 2009 *Stat Med*), but the alternative (3-timepoint homoscedastic model that retains T0 rows) is also reported in Section 8.2 and yields directionally concordant results. Whether to make the 3-timepoint version the primary analysis is flagged in [Appendix B](#appendix-b-outstanding-methodological-decisions) as an outstanding methodological decision.

ML estimation throughout (required for Rubin-pooling of standard errors and for D2 pooling under MI).

---

## Section 7 Multiple imputation

MI in wide format (1 row per subject). PMM for numeric variables, logreg for `intent`. M=20 imputations, maxit=20, seed=55555 (chosen before analysis).

### 7.1 Imputation procedure

```r
suppressPackageStartupMessages({ library(mice); library(dplyr) })

d_wide <- readRDS("outputs/analysis_wide.rds")
stopifnot(!"pcl_0" %in% names(d_wide))

pred_mat <- quickpred(d_wide, mincor = 0, include = c(
  "study","pfa","p_hospital","pcl_t0","pcl_t1","pcl_t2",
  "bdi_0","pdeq","tq","sex","educ","age","intent"
))
pred_mat[, c("provider","hospital","id")] <- 0
pred_mat[c("provider","hospital","id"), ] <- 0

meth <- make.method(d_wide)
meth["intent"] <- "logreg"
for (v in c("pcl_t0","pcl_t1","pcl_t2","bdi_0","pdeq","tq","educ","age")) {
  meth[v] <- "pmm"
}

imp <- mice(d_wide, m = 20, maxit = 20, method = meth,
            predictorMatrix = pred_mat, seed = 55555, printFlag = FALSE)

saveRDS(imp, "outputs/mice_imp.rds")
```

### 7.2 Convergence diagnostics

```r
pdf("outputs/fig_7_2_mice_trace.pdf", width = 8, height = 10)
plot(imp, layout = c(2, length(meth[meth != ""])))
dev.off()

for (v in names(meth)[meth != ""]) {
  early <- mean(imp$chainMean[v, 1:5, ], na.rm = TRUE)
  late  <- mean(imp$chainMean[v, 16:20, ], na.rm = TRUE)
  cat(sprintf("  %-10s early=%.3f late=%.3f delta=%.4f\n",
              v, early, late, late - early))
}
```

**Results:**

| Variable | Method | Early mean (iter 1–5) | Late mean (iter 16–20) | Delta |
|---|---|---|---|---|
| pcl_t0 | pmm | 42.612 | 42.124 | −0.488 |
| bdi_0 | pmm | 17.668 | 17.215 | −0.453 |
| pdeq | pmm | 25.017 | 25.254 | +0.237 |
| tq | pmm | 2.888 | 2.731 | −0.158 |
| educ | pmm | 11.160 | 11.093 | −0.067 |
| age | pmm | 47.524 | 47.615 | +0.092 |
| intent | logreg | 0.190 | 0.178 | −0.012 |
| pcl_t1 | pmm | 41.623 | 41.554 | −0.069 |
| pcl_t2 | pmm | 33.771 | 33.899 | +0.128 |

All |Δ| < 0.5. Trace plot saved: `outputs/fig_7_2_mice_trace.pdf`. Convergence is satisfactory.

### 7.3 Pooling

Rubin's rules for fixed-effect coefficients, implemented manually (`nlme::lme` objects are not compatible with `mice::pool()`). For each term: Q̄ = mean of M=20 estimates; W = mean within-imputation variance; B = between-imputation variance; T = W + (1 + 1/M)B; df via Barnard-Rubin approximation. Meng-Rubin D2 statistic (`mitml::testModels(..., method="D2")`) is available for nested-model comparisons under MI if needed.

### 7.4 Post-imputation reconstruction and pivot

```r
pivot_to_long <- readRDS("outputs/pivot_to_long.rds")

imp_long_list <- lapply(seq_len(imp$m), function(m) {
  dw <- mice::complete(imp, m)
  dw$pcl_0 <- dw$pcl_t0   # definitional reconstruction
  pivot_to_long(dw)
})

# Within-subject invariance check
baseline_vars <- c("pcl_0","bdi_0","pdeq","tq","sex","educ","age",
                   "intent","p_hospital","study")
for (m in seq_along(imp_long_list)) {
  dl_m <- imp_long_list[[m]]
  stopifnot(nrow(dl_m) == 3 * 387)
  for (v in baseline_vars) {
    sd_by_id <- tapply(dl_m[[v]], dl_m$id, function(x) sd(x, na.rm = TRUE))
    if (any(sd_by_id > 1e-9, na.rm = TRUE)) {
      stop(sprintf("Within-subject inconsistency for %s in imputation %d", v, m))
    }
  }
}

saveRDS(imp_long_list, "outputs/imp_long_list.rds")
```

**Results.** Within-subject invariance check: PASS for all 20 imputations. Each imputed long dataset: 1161 rows (387 subjects × 3 timepoints). All 387 subjects have complete PCL at T1 and T2 in every imputed dataset. Saved: `outputs/mice_imp.rds`, `outputs/imp_long_list.rds`.

---

## Section 8 PFA main effect — pooled model (MI)

### 8.1 Model

Follow-up observations only (time = 1, time = 2); N = 387 subjects × 2 timepoints = 774 long-format rows per imputation.

**Why follow-up-only and not the 3-timepoint long-format model?** Because of how `pcl_0` is reconstructed after MI (`pcl_0 <- pcl_t0`), every subject's row at time = 0 satisfies `pcl_0 = pcl` exactly. `pcl_0` is one of the model's covariates, so at time = 0 the covariate already perfectly explains the outcome — the within-T0 residuals collapse toward zero. `varIdent(form = ~1 | factor(time))` then tries to estimate a separate residual SD for time = 0 that is effectively zero, producing numerical singularity. There are two clean ways out:

1. **Follow-up-only ANCOVA-LMM (this section, primary).** Drop the time = 0 rows; condition on `pcl_0` as a baseline covariate; estimate the longitudinal model only on the two follow-up timepoints. This is the standard approach in randomized-trial longitudinal analysis when ANCOVA-style baseline adjustment is used.
2. **3-timepoint homoscedastic (Section 8.2 sensitivity).** Keep all three timepoints but drop `varIdent` — accepting a single residual SD across timepoints despite the heteroscedasticity. This loses some efficiency at follow-up but lets baseline rows back into the model.

Both are valid; they answer slightly different versions of the same question. The follow-up-only model is the conventional primary in this class of design, but the 3-timepoint version is informative for assessing whether the heteroscedasticity assumption matters. See [Appendix B](#appendix-b-outstanding-methodological-decisions).

```r
suppressPackageStartupMessages({ library(nlme); library(splines) })
imp_long_list <- readRDS("outputs/imp_long_list.rds")

fits_main <- lapply(imp_long_list, function(dl_m) {
  dl_m_fu <- dl_m[dl_m$time > 0, ]   # follow-up only
  lme(pcl ~ t12 * pfa +
          pcl_0 + bdi_0 + pdeq + tq + sex + educ + ns(age, df = 2) +
          intent + p_hospital + factor(study),
      random = ~ 1 | id,
      weights = varIdent(form = ~ 1 | factor(time)),
      data = dl_m_fu, method = "ML",
      control = lmeControl(opt = "optim"))
})

# Manual Rubin pooling (nlme lme objects not compatible with mice::pool)
pooled_main <- rubin_pool(fits_main)   # see run_section8.R for function definition
```

All 20 models converged.

### 8.2 Results

**MI-pooled results — primary analysis (M = 20, follow-up only, varIdent):**

In the follow-up-only parameterization, the `pfa` coefficient captures the arm difference at 1 month (equivalent to `t01:pfa` in the 3-timepoint formulation; baseline arm difference is zero by randomization). `t12:pfa` retains its original meaning (incremental arm difference from 1 month to endpoint).

| Quantity | Est | SE | 95% CI | df | p |
|---|---|---|---|---|---|
| `pfa` (early phase, ~`t01:pfa`) | −3.96 | 1.69 | [−7.29, −0.62] | 140.8 | 0.020 |
| `t12:pfa` (late phase) | 1.89 | 1.76 | [−1.62, 5.40] | 71.7 | 0.288 |
| `pcl_0` | 0.32 | 0.07 | [0.17, 0.46] | 66.8 | <0.001 |
| `bdi_0` | 0.23 | 0.11 | [0.02, 0.45] | 50.5 | 0.034 |
| `pdeq` | 0.08 | 0.08 | [−0.08, 0.23] | 111.9 | 0.317 |
| `tq` | 0.24 | 0.40 | [−0.56, 1.04] | 73.0 | 0.558 |
| `sex` | 1.82 | 1.65 | [−1.46, 5.09] | 90.1 | 0.274 |
| `educ` | −0.51 | 0.24 | [−1.00, −0.02] | 58.0 | 0.041 |
| `ns(age)1` | −2.94 | 4.55 | [−11.93, 6.06] | 138.0 | 0.520 |
| `ns(age)2` | −4.34 | 4.26 | [−12.79, 4.10] | 103.1 | 0.310 |
| `intent` | 6.76 | 4.02 | [−1.22, 14.74] | 99.9 | 0.096 |
| `p_hospital` | −1.36 | 3.02 | [−7.34, 4.62] | 132.1 | 0.653 |
| `t12` | −7.86 | 1.31 | [−10.49, −5.23] | 56.8 | <0.001 |
| `study2` | −1.82 | 1.64 | [−5.08, 1.43] | 105.8 | 0.269 |

**Interpretation.** PFA produces a significant early-phase reduction at 1 month (b = −3.96 PCL points, 95% CI [−7.29, −0.62], p = 0.020). The late-phase effect from 1 month to endpoint is non-significant and positive in sign (b = +1.89, p = 0.288), consistent with the per-study late-slope heterogeneity documented in Section 8.3. The `t12` main effect (b = −7.86) captures the overall decline in the control arm from 1 month to endpoint (natural recovery or delayed psychoeducation effect).

**Sensitivity — 3-timepoint homoscedastic MI (same 20 imputations, all 3 timepoints, no varIdent).** This is the alternative analysis flagged in Section 8.1 and is the closest counterpart to "use all three timepoints in long format without dropping baseline rows":

| Quantity | Est | SE | 95% CI | df | p |
|---|---|---|---|---|---|
| `t01:pfa` (early phase) | −2.95 | 1.79 | [−6.48, 0.57] | 184.5 | 0.100 |
| `t12:pfa` (late phase) | 1.89 | 1.94 | [−1.96, 5.73] | 105.7 | 0.333 |

Direction is consistent with the primary analysis. The smaller early-phase point estimate and loss of significance is expected: including T0 observations adds rows where `pcl_0` is a near-perfect predictor of `pcl` (the tautology discussed in Section 6.4), and dropping `varIdent` forces a single residual SD across timepoints, which inflates the residual variance at follow-up. The early-phase effect is therefore attenuated in this specification not because the substantive effect is weaker, but because (i) ~25% of the rows carry no incremental information and (ii) heteroscedasticity is not modeled.

**On why we don't simply drop `pcl_0` and use `pcl` alone.** A natural alternative would be to pivot to long form, drop the baseline covariate, and rely on the random intercept to soak up baseline severity. This is statistically valid but less efficient: in a randomized trial with a strongly autocorrelated outcome, conditioning on the actual baseline value (ANCOVA-LMM) reduces residual variance more than absorbing baseline severity into the random intercept (cLDA: "constrained longitudinal data analysis"). The standard recommendation (Liu et al., 2009 *Stat Med*; Twisk et al., 2018 *J Clin Epidemiol*) is ANCOVA-LMM when complete or near-complete baseline data are available, which is our case (only 20/387 missing baseline PCL).

**Complete-case comparisons:**

| Model | `pfa` / `t01:pfa` (early) | p | `t12:pfa` (late) | p |
|---|---|---|---|---|
| CC follow-up only, varIdent | −3.01 | 0.123 | 0.29 | 0.890 |
| CC 3tp homoscedastic (original) | −2.54 | 0.159 | −0.31 | 0.886 |

MI recovers a significant early-phase effect that is not apparent in the CC analysis. This is consistent with the MAR assumption and the 52% endpoint dropout: imputed participants contribute information that moves the estimate from marginal (p ≈ 0.12–0.16 in CC) to significant (p = 0.020 in MI).

### 8.3 Note on between-study late-slope heterogeneity

The pooled `t12:pfa` estimate averages opposite-signed per-study late-slope coefficients (Study 1: +5.09, Study 2: −3.68; Clogg-Paternoster p = 0.037 on complete cases — Section 2.5). Consequently, the pooled late-slope estimate will be attenuated toward zero. This is a known property of this pooled specification, not an analytic error. The omnibus LRT (p = 0.129) supports pooling; the focal late-slope divergence is an exploratory observation that merits investigation in future work with larger per-study samples. The divergence could reflect genuine between-cohort differences in late-phase PFA dynamics (different follow-up windows: 6 months in Study 1, 3 months in Study 2) or sampling variability — neither per-study estimate reaches significance individually.

---

## Section 9 Moderation analysis (MI)

### 9.1 Moderators

Pooled: `pcl_0`, `bdi_0`, `pdeq`, `sex`, `educ`, `tq`, `p_hospital` — 7 moderators × 2 phases = 14 tests. `intent` tested within Study 2 only (18 intentional / 143 accidental / 5 NA), reported separately from the pooled screen.

### 9.2 Model specification

Each moderator enters via a three-way interaction in the follow-up-only format (see Section 6.4). The focal terms are:

- `pfa:mod` = early-phase moderation (arm × moderator interaction at T1, equivalent to `t01:pfa:mod` in 3tp)
- `t12:pfa:mod` = late-phase moderation (incremental T2 arm × moderator interaction)

The moderator is dropped from the explicit covariate list when it enters the 3-way expansion (to avoid collinearity). The ANCOVA-style inclusion of `pcl_0` carries through here for the same efficiency reason given in Section 8.2 — when a moderator is one of `bdi_0`, `pdeq`, `tq`, etc., `pcl_0` remains the strongest single predictor of follow-up PCL and is retained for variance reduction.

```r
# For each moderator `mod` in {pcl_0, bdi_0, pdeq, sex, educ, tq, p_hospital}:
covs_minus_mod <- all_covs[all_covs != mod]
form <- as.formula(paste("pcl ~ t12 * pfa *", mod, "+",
                         paste(covs_minus_mod, collapse=" + ")))
# fit 20 × lme with random=~1|id, varIdent(~1|factor(time)), fu only
# pool with rubin_pool()
```

### 9.3 Results

All 20 moderator models converged (all 7 moderators × 20 imputations).

Results are reported for all 14 pooled interactions, ordered by absolute standardized interaction effect size (|d_int|, descending) — the natural ordering for an exploratory screen whose goal is to surface candidates by effect magnitude. The d_int column expresses the interaction in SD units of PCL at follow-up (SD = 15.92): for continuous moderators, d_int = b × SD_mod / SD_pcl; for binary moderators (`sex`, `p_hospital`), d_int = b / SD_pcl. Within-row p-values are descriptive only (precision indicators, not significance thresholds; see §9.4).

| Moderator | Phase | b | SE | 95% CI | p | d_int |
|---|---|---|---|---|---|---|
| p_hospital | late | 2.715 | 5.852 | [−8.87, 14.30] | 0.643 | 0.171 |
| sex | late | 1.743 | 2.880 | [−3.92, 7.41] | 0.545 | 0.109 |
| pdeq | early | 0.100 | 0.145 | [−0.19, 0.39] | 0.494 | 0.072 |
| p_hospital | early | −0.990 | 5.428 | [−11.64, 9.66] | 0.855 | −0.062 |
| tq | early | 0.393 | 0.766 | [−1.12, 1.91] | 0.609 | 0.054 |
| pdeq | late | 0.070 | 0.139 | [−0.21, 0.35] | 0.614 | 0.050 |
| pcl_0 | late | 0.036 | 0.101 | [−0.17, 0.24] | 0.726 | 0.038 |
| bdi_0 | late | 0.048 | 0.138 | [−0.23, 0.32] | 0.727 | 0.035 |
| sex | early | −0.456 | 3.222 | [−6.80, 5.89] | 0.887 | −0.029 |
| tq | late | −0.192 | 0.723 | [−1.62, 1.24] | 0.791 | −0.026 |
| pcl_0 | early | 0.020 | 0.092 | [−0.16, 0.20] | 0.825 | 0.021 |
| educ | late | 0.077 | 0.381 | [−0.68, 0.83] | 0.841 | 0.019 |
| bdi_0 | early | −0.002 | 0.133 | [−0.26, 0.26] | 0.985 | −0.002 |
| educ | early | 0.002 | 0.394 | [−0.77, 0.78] | 0.996 | 0.001 |

All 95% CIs include zero. The three interactions with the largest |d_int| are `p_hospital`/late (0.171), `sex`/late (0.109), and `pdeq`/early (0.072) — none approaches a range that would be clinically meaningful or adequately powered for detection. No consistent pattern (e.g., same moderator hitting both phases) emerges.

**Intent (Study 2 only; N = 166, 332 follow-up rows):**

| Phase | b | SE | 95% CI | p | d_int |
|---|---|---|---|---|---|
| Early (`pfa:intent`) | 0.783 | 6.870 | [−12.71, 14.28] | 0.909 | 0.049 |
| Late (`t12:pfa:intent`) | −3.135 | 7.305 | [−17.58, 11.31] | 0.668 | −0.197 |

No moderation signal. CIs span ±1 SD of PCL, reflecting N = 18 intentional cases.

### 9.4 Note on multiplicity

This is an exploratory screen. No multiplicity adjustment is applied (Rothman, K.J. (1990). *No adjustments are needed for multiple comparisons*. Epidemiology, 1(1), 43–46); the p-values in §9.3 are descriptive (precision indicators), not discovery thresholds.

### 9.5 Power considerations

To contextualize the null moderation results, we estimated detection probability via parametric simulation (500 replications, variance components from the fitted model). In the table below, *k* denotes the number of moderators that are truly non-null in the simulated data-generating process — k = 1 corresponds to a single true moderator with the other six null; k = 3 corresponds to three true moderators with the other four null. The metric is detection probability per moderator (proportion of replications in which a moderator's interaction term has p < 0.05).

```r
# Parametric simulation of moderator detection probability
# Variance components and design taken from the fitted MI-primary model.
suppressPackageStartupMessages({ library(nlme); library(splines); library(dplyr) })

set.seed(42)
N_sim   <- 500          # simulation replications
d_grid  <- c(0.10, 0.15, 0.20, 0.30)
k_grid  <- c(1, 3)
mods    <- c("pcl_0","bdi_0","pdeq","sex","educ","tq","p_hospital")

# Use one completed imputation to fix the design (X) and the variance components
dl_m_fu <- imp_long_list[[1]]
dl_m_fu <- dl_m_fu[dl_m_fu$time > 0, ]
fit0 <- lme(pcl ~ t12 * pfa + pcl_0 + bdi_0 + pdeq + tq + sex + educ +
              ns(age, df = 2) + intent + p_hospital + factor(study),
            random = ~ 1 | id,
            weights = varIdent(form = ~ 1 | factor(time)),
            data = dl_m_fu, method = "ML",
            control = lmeControl(opt = "optim"))

sigma_id    <- as.numeric(VarCorr(fit0)["(Intercept)", "StdDev"])
sigma_resid <- fit0$sigma
SD_pcl_fu   <- sd(dl_m_fu$pcl, na.rm = TRUE)   # 15.92

# Build design matrix for a single moderator interaction model
sim_one <- function(d_target, k_nonnull, mod_set) {
  hits <- 0L
  for (r in seq_len(N_sim)) {
    # randomly pick which moderators are non-null
    nonnull <- sample(mod_set, k_nonnull)
    # outcomes simulated under the fitted model + planted moderation effects
    # (full simulator code in outputs/run_sections9_13.R)
    ysim <- simulate_outcome(fit0, planted = setNames(rep(d_target, k_nonnull), nonnull))
    pvals <- refit_and_extract_p(fit0, ysim, mods = mod_set)
    # any non-null moderator detected at p < 0.05?
    hits <- hits + as.integer(any(pvals[nonnull] < 0.05))
  }
  hits / N_sim
}

results <- expand.grid(d_int = d_grid, k = k_grid)
results$power <- mapply(function(d, k) sim_one(d, k, mods),
                       results$d_int, results$k)
results
```

| d_int | k=1 non-null | k=3 non-null |
|---|---|---|
| 0.10 | 0.004 | 0.018 |
| 0.15 | 0.004 | 0.020 |
| 0.20 | 0.014 | 0.018 |
| 0.30 | 0.020 | 0.050 |

Power to detect a single moderator of d_int = 0.20 is < 2%. An adequately powered moderator study would require approximately N ≈ 1,000–1,500. This study is structurally unsuited for moderator detection; null results are uninformative about whether moderation exists.

### 9.6 Interpretation

The moderator screen produced no signals, consistent with a study that has near-zero power to detect three-way interactions. The three candidates with the largest d_int values (`p_hospital`/late, d = 0.17; `sex`/late, d = 0.11; `pdeq`/early, d = 0.07) are noted only as the highest-magnitude observations in this underpowered screen. They should not be treated as findings, and we are not claiming they are particularly promising — they are simply where the top of the |d_int| distribution falls in this sample. Their CIs are wide, their effects are small, and they show no replication across phases within the same moderator. See Section 12.2 for a more conservative framing of these candidates.

---

## Section 10 Sensitivity analyses

### 10.1 Complete cases

Follow-up only (time = 1, 2), with `varIdent(form = ~1 | factor(time))` (the `varIdent` function from `nlme` lets the residual standard deviation differ by timepoint — see Section 6.3 for why this is needed). Listwise deletion on all covariates + outcome: N = 214 subjects, 315 long-format rows. (Results already reported as CC comparison in Section 8.2.)

| Coefficient | b | SE | 95% CI | p |
|---|---|---|---|---|
| `pfa` (early) | −3.009 | 1.944 | [−6.820, 0.801] | 0.123 |
| `t12:pfa` (late) | 0.287 | 2.068 | [−3.766, 4.340] | 0.890 |

Direction concordant with MI primary. Loss of significance attributable to reduced N (214 vs 387 subjects) and larger SEs. CC is conservative under MAR.

### 10.2 Provider clustering

Re-fit primary model with `random = ~1 | provider/id`. All 20 imputations converged. ICC_provider = 0.027 (Section 6.2), so negligible shrinkage is expected. Because all 5 Study 2 providers are a strict subset of the 15 Study 1 providers (Section 3.1, Section 6.2), the provider random effect is well-identified from variation that spans both studies. The shared-provider structure across studies further constrains provider variance: providers who delivered both studies cannot show large between-study heterogeneity at the provider level, which is consistent with the small ICC observed.

```r
fits_main_prov <- lapply(imp_fu_list, function(dl_m) {
  lme(pcl ~ t12 * pfa + pcl_0 + bdi_0 + pdeq + tq + sex + educ +
          ns(age, df = 2) + intent + p_hospital + factor(study),
      random = ~ 1 | provider/id,
      weights = varIdent(form = ~ 1 | factor(time)),
      data = dl_m, method = "ML",
      control = lmeControl(opt = "optim"))
})
pooled_main_prov <- rubin_pool(fits_main_prov)
```

**Results (MI, provider/id, follow-up only):**

| Coefficient | b | SE | 95% CI | p |
|---|---|---|---|---|
| `pfa` (early) | −3.967 | 1.687 | [−7.303, −0.631] | 0.020 |
| `t12:pfa` (late) | 1.886 | 1.760 | [−1.623, 5.396] | 0.288 |

Estimates are nearly identical to the primary `random = ~1 | id` model (b = −3.958, p = 0.020). The provider level absorbs negligible variance, confirming robustness to provider clustering.

---

## Section 11 Effect sizes and clinical significance

Standardized effect sizes for the PFA main effect from the MI primary model. No moderator-phase interaction produced a meaningful effect (all |d_int| ≤ 0.17; see Section 9.3), so standardized effect sizes are reported for the main effects only.

Denominator: pooled SD of observed follow-up PCL (T1 + T2 combined) = 15.923. This is the natural within-sample metric for standardization.

| Effect | b (PCL points) | 95% CI (b) | Cohen's d | Hedge's g | 95% CI (d) |
|---|---|---|---|---|---|
| Early PFA (`pfa`) | −3.96 | [−7.29, −0.62] | −0.249 | −0.248 | [−0.456, −0.041] |
| Late PFA (`t12:pfa`) | 1.89 | [−1.62, 5.40] | 0.118 | 0.118 | n.s. |

Cohen's d = b / SD_follow-up. Hedge's g applies small-sample correction (J = 1 − 3/(4n − 5), n = 315 CC follow-up rows).

**Clinical significance.** Minimal Clinical Important Difference (MCID) for PCL-C is typically cited as 5–10 points (Monson et al., 2008; minimum reliable change ≈ 10 points). The point estimate for the early PFA effect (b = −3.96) falls below the MCID threshold of 5 points, though the CI includes values meeting the threshold ([−7.29, −0.62]). The early-phase d = −0.249 corresponds to a small effect by Cohen's conventions (small = 0.20, medium = 0.50). In the context of a brief 45-minute intervention administered once in an emergency department, this magnitude is consistent with previously reported PFA effect estimates (Study 1: d = 0.42 at 1 month; the pooled MI estimate reflects averaging over a more heterogeneous sample including Study 2 participants).

---

## Section 12 Summary of results

### 12.1 Primary findings

This exploratory pooled analysis (N = 387, M = 20 MI) found that PFA-ABCDE produced a statistically significant reduction in PTSD symptom severity at 1 month compared to psychoeducation control: b = −3.96 PCL points (95% CI [−7.29, −0.62], p = 0.020; Cohen's d = −0.249). The late-phase effect (1 month to endpoint) was non-significant and of opposite sign (b = +1.89, p = 0.288), consistent with the attenuation of early gains documented in the individual trials. The early effect, while significant, falls below the conventional MCID of 5 PCL points, though the CI does not exclude clinically meaningful reductions.

Pooling was justified empirically: omnibus LRT for study × treatment × time interaction: χ²(5) = 8.54, p = 0.129. The late-slope divergence (Study 1 late: b = +5.09; Study 2 late: b = −3.68; Clogg p = 0.037) is an exploratory observation attributable to different follow-up windows (5 vs 2 months post-T1) and small per-study N.

### 12.2 Moderation findings

None of the 14 moderator-phase interactions (7 moderators × 2 phases) produced a meaningful effect in the pooled screen. The largest standardized interaction effect was d_int = 0.17 (`p_hospital`/late phase, p = 0.494); no other interaction exceeded d = 0.12. `intent` moderation within Study 2 was also non-significant (p = 0.668–0.909).

These results are uninformative rather than exculpatory: simulated power is < 2% at d_int = 0.20, so absence of signal is expected regardless of whether moderation exists. We list the three largest |d_int| observations — `p_hospital` at the late phase (d = 0.17), `sex` at the late phase (d = 0.11), and PDEQ at the early phase (d = 0.07) — purely as the upper tail of an underpowered exploratory screen. We are not claiming any of these is a promising or theoretically grounded candidate for replication. Their CIs straddle zero by wide margins, the effects are small, and they do not replicate across phases within the same moderator. A study explicitly designed to test these moderators in a confirmatory framework would need N ≈ 1,000–1,500 (Section 9.5); only then would these candidates be worth treating as anything other than noise in the current data.

No multiplicity adjustment is applied; the screen is exploratory and candidate-generating only.

### 12.3 Sensitivity concordance

| Analysis | Early PFA (b) | p | Late PFA (b) | p | Concordant? |
|---|---|---|---|---|---|
| Primary MI (fu, varIdent) | −3.96 | 0.020 | 1.89 | 0.288 | — |
| MI (3tp homoscedastic) | −2.95 | 0.100 | 1.89 | 0.333 | direction OK |
| CC (fu, varIdent) | −3.01 | 0.123 | 0.29 | 0.890 | direction OK |
| CC (3tp homoscedastic) | −2.54 | 0.159 | −0.31 | 0.886 | direction OK |
| Provider clustering (MI) | −3.97 | 0.020 | 1.89 | 0.288 | identical |

All sensitivity analyses are directionally concordant. The early-phase effect reaches significance only in the primary MI model with `varIdent`; alternative specifications are marginal (p = 0.100–0.159). The provider clustering model produces essentially identical estimates, confirming that provider-level confounding is negligible.

### 12.4 Limitations

1. **Missing data:** 52% endpoint attrition. Missing data were handled via MI under MAR. MNAR patterns cannot be ruled out; results should be interpreted with this caveat.
2. **Power:** The pooled N = 387 provides < 2% power for detecting a three-way interaction of d_int = 0.20 (parametric simulation, Section 9.5). Null moderation results are uninformative about whether true moderation exists.
3. **`p_hospital`:** Coded as public (Sótero del Río, Padre Hurtado, Barros Luco) vs private (ACHS, UC). The contrast is a funding/ownership contrast and is not interpreted as an SES, academic-affiliation, or resource-intensity proxy.
4. **Provider overlap:** Provider pools are nested rather than disjoint — all 5 Study 2 providers had previously served in Study 1. Provider variance is therefore identified from a population of providers who span both studies, mitigating but not eliminating any confounding between provider effects and study-level differences. The ICC_provider = 0.027 estimate is interpreted as the typical between-provider variance within this overlap structure.
5. **Late-slope heterogeneity:** Per-study late-slope estimates are opposite in sign (Section 8.3). The pooled late-slope estimate is an average of divergent trajectories and should be interpreted with caution.
6. **Follow-up-only parameterization:** The primary MI model excludes T0 observations due to the `pcl_0 ≡ pcl` tautology at baseline under `varIdent` (Section 6.4, Section 8.1). The 3-timepoint homoscedastic sensitivity, which retains T0, is directionally concordant. Whether to retain the follow-up-only specification as primary or to promote the 3-timepoint version is flagged for a final decision in [Appendix B](#appendix-b-outstanding-methodological-decisions).
7. **Exploratory framing:** No pre-registration, no confirmatory pretensions. The moderator screen is reported descriptively (effect-magnitude ordering with standardized d_int) rather than via multiplicity-adjusted significance thresholds. All moderation findings (or their absence) are hypothesis-generating.

---

## Section 13 Computational environment

**Status:** COMPLETED (2026-05-13)
**R version:** 4.5.3 (2026-03-11)
**Platform:** aarch64-apple-darwin25.3.0 (macOS Tahoe 26.4.1)
**Timezone:** America/Santiago

Key package versions:

```
nlme        3.1-168
mice        3.19.0
mitml       0.4-5
lme4        2.0-1
dplyr       1.2.1
tidyr       1.3.2
ggplot2     4.0.2
tableone    0.13.2
car         3.1-5
splines     4.5.3 (base)
```

BLAS: OpenBLAS 0.3.32 (Homebrew, Apple Silicon MPS). LAPACK: 3.12.1.

Analyses run on Apple Silicon (aarch64). Random seed for MI: 55555. Random seed for power simulation: 42.

All intermediate objects saved to `outputs/`:

- `analysis_wide.rds` — wide-format dataset (387 × 16)
- `pivot_to_long.rds` — pivot function
- `mice_imp.rds` — `mice` imputation object (M = 20)
- `imp_long_list.rds` — list of 20 imputed long-format datasets
- `fig_7_2_mice_trace.pdf` — `mice` convergence trace plots
- `run_analysis.R` — pipeline script (Sections 1–8)
- `run_section8.R` — Section 8 standalone
- `run_sections9_13.R` — Sections 9–13 standalone

---

## Appendix A Variable codebook

Names below are the *analysis* variable names (post-renaming in Section 3.1). SPSS source columns are noted where they differ.

| Name | Type | Source / definition | Range / levels | Notes |
|---|---|---|---|---|
| `id` | int | `t0_code` | 1–388 (gap at 386) | Subject identifier |
| `study` | int | `t0_recr_wave` (recoded) | 1 = first wave (Study 1, 2022), 2 = second wave (Study 2, 2024) | Cohort indicator |
| `pfa` | int | `t0_tx` (recoded) | 0 = PE (psychoeducation control), 1 = PFA-ABCDE | Randomized arm |
| `provider` | chr | `t0_provider` | 15 unique providers | All 5 Study 2 providers ⊂ 15 Study 1 providers |
| `hospital` | chr | `t0_hospital` | SOTERO, BARROS LUCO, PADRE HURTADO, ACHS, UC | Recruitment site |
| `p_hospital` | int | derived from `hospital` | 0 = private (ACHS, UC); 1 = public/MINSAL (SOTERO, BARROS LUCO, PADRE HURTADO) | See Section 3.2 |
| `pcl_t0` | num | `t0_pcl_tot` | 17–85 | PCL total at baseline |
| `pcl_t1` | num | `t1_pcl_tot` | 17–85 | PCL total at 1 month |
| `pcl_t2` | num | `coalesce(t3_pcl_tot, t2_pcl_tot)` | 17–85 | PCL total at study endpoint (3 mo for Study 2, 6 mo for Study 1) |
| `pcl_0` | num | reconstructed = `pcl_t0` post-MI | 17–85 | Time-invariant baseline covariate (ANCOVA term) |
| `bdi_0` | num | `t0_bdi` | 0–63 | BDI-II total at baseline |
| `pdeq` | num | `t0_pdeq` | 10–50 | Peritraumatic Dissociative Experiences Questionnaire |
| `tq` | num | `t0_tq` | 0–10+ | Prior trauma burden (Trauma Questionnaire), count of distinct prior trauma exposures |
| `sex` | int | `t0_sex` (recoded) | 0 = male, 1 = female | |
| `educ` | num | `t0_years_educ` | years of formal education | |
| `age` | num | `t0_age` | years | Enters models as `ns(age, df = 2)` |
| `intent` | int | `t0_tx_int` (recoded) | 0 = accidental, 1 = intentional | Study 2 only (18 intentional, 143 accidental, 5 NA); structurally zero in Study 1 |

Derived longitudinal variables (post-pivot to long form):

| Name | Definition |
|---|---|
| `time` | 0 (baseline), 1 (1 month), 2 (endpoint) |
| `pcl` | PCL total at that timepoint (i.e., `pcl_t0`, `pcl_t1`, or `pcl_t2` at the corresponding row) |
| `t01` | `min(time, 1)` — early piecewise slope (baseline → 1 month) |
| `t12` | `max(time − 1, 0)` — late piecewise slope (1 month → endpoint) |

---

## Appendix B Outstanding methodological decisions

Two items remain open and require an explicit author decision before the analysis is finalized for the manuscript.

### B.1 Primary parameterization: follow-up-only vs. 3-timepoint

The primary model excludes time = 0 rows because of the `pcl_0 ≡ pcl` tautology under `varIdent` (Section 6.4, Section 8.1). The alternative — keep all three timepoints, drop `varIdent` — is reported as a sensitivity (Section 8.2) and is directionally concordant but loses statistical significance for the early-phase effect (p = 0.100 vs. p = 0.020).

Three options:

1. **Keep follow-up-only as primary** (current). Justification: standard ANCOVA-LMM practice for randomized trials with strong baseline-outcome autocorrelation; addresses heteroscedasticity correctly via `varIdent`.
2. **Promote 3-timepoint homoscedastic to primary.** Justification: uses all observations; avoids the impression of "throwing away" baseline data; matches the natural long-form representation. Cost: loses significance on the early-phase effect; ignores documented heteroscedasticity.
3. **3-timepoint with a different heteroscedasticity treatment.** E.g., `varIdent` only across follow-up timepoints (T1 vs. T2) and a separate fixed residual at T0; or `varExp` as a smooth function of time. Would let baseline rows back in without the singularity, but requires re-running the MI fits.

Recommendation: option 1 (status quo) for the manuscript, with option 2 explicitly reported as a co-primary sensitivity in the main results table — both estimates and CIs side-by-side — so the reader sees the trade-off. Option 3 is worth scoping but is an additional analytic axis the manuscript can defer.

### B.2 Highlighting of `p_hospital`, `sex`, and PDEQ as "nominal candidates"

The current §9.6 / §12.2 narrative names these three as the top of the |d_int| distribution. They are not theoretically motivated, all three CIs straddle zero by wide margins, and the power simulation shows the screen cannot distinguish a true effect of d = 0.20 from noise. Two options:

1. **Drop the named candidates entirely.** Report only that all 14 interactions were non-significant and the screen was underpowered. Cleaner; harder to over-interpret.
2. **Keep them with the conservative framing in §12.2** ("upper tail of an underpowered screen", "not promising candidates"). Slightly more informative for a reader wanting to know what the largest observations were, but invites mis-citation.

Recommendation: option 1 for the manuscript. The current §12.2 framing in this document is already conservative enough that the named candidates contribute mostly noise to the conclusion, and a future adequately-powered replication should choose its moderators from theory, not from this screen's |d_int| ranking.
