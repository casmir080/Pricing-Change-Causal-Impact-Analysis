Pricing Change Causal Impact Analysis

Product Experimentation | Difference-in-Differences | Propensity Score Matching

Overview

This project evaluates the causal impact of a pricing change on user conversion and revenue for a digital product.

A non-random rollout introduced selection bias, making raw metrics unreliable.
To support a real business decision, I applied causal inference methods and validated results with placebo and falsification tests.

Final outcome:
After bias correction, the price increase reduced conversion and revenue, leading to a recommendation to rollback or redesign the pricing change.

Business Problem

Leadership increased the price of a mid-tier plan to improve revenue.

Key questions:

Did the price change affect conversion?

Did the higher price compensate for any conversion loss?

Can we trust the observed effects given a non-random rollout?

This was not a clean A/B test. Exposure depended on user attributes, requiring causal analysis.

Data & Setup
Data Characteristics

User-level data

Non-random treatment assignment

Event-based conversion and revenue tracking

Stored and queried via PostgreSQL

Core Tables

users

pricing_exposure

events

revenue

Tooling

PostgreSQL (data storage & SQL logic)

Python (Pandas, NumPy, statsmodels)

VS Code

Experimental Design
Treatment

Users exposed to the new price

Control

Comparable users exposed to the old price

Challenges

Selection bias (mobile and paid users more likely treated)

Time effects

No randomized assignment

Methods Used
1. Difference-in-Differences (DiD)

Compared pre vs post trends between treated and control users

Robust standard errors

Parallel trend validation

Result:
Small positive effect, not statistically significant

2. Propensity Score Matching (Primary Method)

Logistic / GLM model to estimate treatment probability

One-to-one nearest-neighbor matching

Common support enforcement

Balance diagnostics using standardized mean differences (SMD)

Bootstrap confidence intervals

Why PSM mattered:
It directly corrected for non-random exposure and removed most selection bias.

3. Validation & Falsification Tests

To ensure credibility:

Placebo rollout date

Randomized placebo treatment

Negative control outcome

All tests behaved as expected and showed no false effects.

Key Results
Conversion Impact (PSM)

−2.36 percentage points

95% CI: −2.93 to −1.83

Statistically significant

Revenue Impact (PSM)

Negative ATT

Conversion loss outweighed price increase

Comparison of Methods
Method	Conversion Impact	Statistical Significance	Verdict
Raw metrics	Mixed	No	Misleading
DiD	+0.18 pp	No	Inconclusive
PSM	−2.36 pp	Yes	Trusted
Placebos	~0	Pass	Valid
Final Recommendation

Rollback or redesign the price increase.

After correcting for selection bias and validating with falsification tests:

Conversion dropped materially

Revenue per exposed user declined

Evidence does not support keeping the current pricing

Limitations

Unobserved confounders may still exist

Results apply to the rollout population

Randomized A/B test recommended for confirmation