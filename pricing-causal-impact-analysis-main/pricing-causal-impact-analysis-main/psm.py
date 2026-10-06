import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import statsmodels.api as sm

engine = create_engine("postgresql+psycopg2://postgres:443302@localhost:5432/experiments")

df = pd.read_sql("SELECT * FROM public.psm_base", engine)

df["treated"] = pd.to_numeric(df["treated"], errors="raise").astype(int)

df["converted"] = pd.to_numeric(df["converted"], errors="coerce").fillna(0).astype(int)
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)

covariates = ["country", "device_type", "acquisition_channel", "pre_period_user"]
df["pre_period_user"] = pd.to_numeric(df["pre_period_user"], errors="raise").astype(int)

for c in ["country", "device_type", "acquisition_channel"]:
    df[c] = df[c].astype(str).str.strip()

X = pd.get_dummies(df[covariates], drop_first=True, dtype=float)

X = sm.add_constant(X, has_constant="add")

if (X.dtypes == "object").any():
    bad = X.columns[X.dtypes == "object"].tolist()
    raise TypeError(f"Non-numeric columns in X: {bad}")

if np.isnan(X.to_numpy()).any():
    raise ValueError("NaNs found in X after encoding. Check source columns for nulls.")

y = df["treated"].astype(int)

print("X shape:", X.shape, "y shape:", y.shape)
print("Treated counts:\n", y.value_counts())

glm = sm.GLM(y, X, family=sm.families.Binomial()).fit()

df["pscore"] = glm.predict(X).clip(1e-6, 1 - 1e-6)

print("\nPropensity score summary:")
print(df["pscore"].describe())

print("\nTop coefficients (by abs value):")
coef = glm.params.drop("const").sort_values(key=np.abs, ascending=False).head(10)
print(coef)

t = df.loc[df["treated"] == 1, "pscore"]
c = df.loc[df["treated"] == 0, "pscore"]
lower = max(t.min(), c.min())
upper = min(t.max(), c.max())

df_cs = df[(df["pscore"] >= lower) & (df["pscore"] <= upper)].copy()

print("\nCommon support range:", float(lower), float(upper))
print("After common support treated counts:\n", df_cs["treated"].value_counts())

treated_df = df_cs[df_cs["treated"] == 1].sort_values("pscore").copy()
control_df = df_cs[df_cs["treated"] == 0].sort_values("pscore").copy()

control_scores = control_df["pscore"].to_numpy()
control_idx = control_df.index.to_numpy()

used = np.zeros(len(control_scores), dtype=bool)
pairs = []

for tidx, ts in zip(treated_df.index.to_numpy(), treated_df["pscore"].to_numpy()):
    diffs = np.abs(control_scores - ts)
    diffs[used] = np.inf
    j = int(np.argmin(diffs))
    if np.isinf(diffs[j]):
        continue
    used[j] = True
    pairs.append((tidx, control_idx[j], float(diffs[j])))

match_df = pd.DataFrame(pairs, columns=["treated_index", "control_index", "abs_diff"])
print("\nMatched pairs:", len(match_df))
print("Match distance summary:\n", match_df["abs_diff"].describe())

def smd(x_t, x_c):
    x_t = np.asarray(x_t, dtype=float)
    x_c = np.asarray(x_c, dtype=float)
    denom = np.sqrt(0.5 * (x_t.var(ddof=1) + x_c.var(ddof=1)))
    return 0.0 if denom == 0 else (x_t.mean() - x_c.mean()) / denom

t_matched = df_cs.loc[match_df["treated_index"]].copy()
c_matched = df_cs.loc[match_df["control_index"]].copy()

Z_all = pd.get_dummies(df_cs[covariates], drop_first=True, dtype=float)
Z_t_before = Z_all[df_cs["treated"] == 1]
Z_c_before = Z_all[df_cs["treated"] == 0]

Z_t_after = pd.get_dummies(t_matched[covariates], drop_first=True, dtype=float)
Z_c_after = pd.get_dummies(c_matched[covariates], drop_first=True, dtype=float)
Z_t_after, Z_c_after = Z_t_after.align(Z_c_after, join="outer", axis=1, fill_value=0.0)

balance = []
for col in Z_all.columns:
    balance.append((col, smd(Z_t_before[col], Z_c_before[col]), smd(Z_t_after.get(col, 0), Z_c_after.get(col, 0))))
bal = pd.DataFrame(balance, columns=["feature", "smd_before", "smd_after"])
bal["abs_before"] = bal["smd_before"].abs()
bal["abs_after"] = bal["smd_after"].abs()

print("\nMax |SMD| before:", float(bal["abs_before"].max()))
print("Max |SMD| after:", float(bal["abs_after"].max()))
print("\nWorst balance after matching:")
print(bal.sort_values("abs_after", ascending=False).head(10)[["feature", "smd_before", "smd_after"]])

att_conv = t_matched["converted"].mean() - c_matched["converted"].mean()
att_rev = t_matched["revenue"].mean() - c_matched["revenue"].mean()

print("\nATT conversion (pp):", round(att_conv * 100, 3))
print("ATT revenue:", round(att_rev, 3))

B = 300
rng = np.random.default_rng(42)
pair_idx = np.arange(len(match_df))

att_conv_bs = np.empty(B)
att_rev_bs = np.empty(B)

t_rows = t_matched.reset_index(drop=True)
c_rows = c_matched.reset_index(drop=True)

for b in range(B):
    s = rng.choice(pair_idx, size=len(pair_idx), replace=True)
    att_conv_bs[b] = t_rows.loc[s, "converted"].mean() - c_rows.loc[s, "converted"].mean()
    att_rev_bs[b] = t_rows.loc[s, "revenue"].mean() - c_rows.loc[s, "revenue"].mean()

c_lo, c_hi = np.quantile(att_conv_bs, [0.025, 0.975])
r_lo, r_hi = np.quantile(att_rev_bs, [0.025, 0.975])

print("ATT conversion 95% CI (pp):", round(c_lo * 100, 3), "to", round(c_hi * 100, 3))
print("ATT revenue 95% CI:", round(r_lo, 3), "to", round(r_hi, 3))
