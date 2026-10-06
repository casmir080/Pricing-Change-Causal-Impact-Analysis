import pandas as pd
from sqlalchemy import create_engine
import statsmodels.api as sm

engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/experiments")

df = pd.read_sql("""
    SELECT treated, post_period, outcome_pre_period_user
    FROM public.analytics_negative_control
""", engine)

df["interaction"] = df["treated"] * df["post_period"]

X = sm.add_constant(df[["treated", "post_period", "interaction"]], has_constant="add")
y = df["outcome_pre_period_user"]

m = sm.OLS(y, X).fit(cov_type="HC3")

print("neg_control coef:", m.params["interaction"])
print("neg_control se:", m.bse["interaction"])
print("neg_control pvalue:", m.pvalues["interaction"])
