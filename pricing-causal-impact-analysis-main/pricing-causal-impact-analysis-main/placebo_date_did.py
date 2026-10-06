import pandas as pd
from sqlalchemy import create_engine
import statsmodels.api as sm

engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/experiments")

df = pd.read_sql("""
    SELECT treated, post_period, converted
    FROM public.analytics_did_placebo_date
""", engine)

df["interaction"] = df["treated"] * df["post_period"]

X = sm.add_constant(df[["treated", "post_period", "interaction"]], has_constant="add")
y = df["converted"]

m = sm.OLS(y, X).fit(cov_type="HC3")

print("placebo_date coef:", m.params["interaction"])
print("placebo_date se:", m.bse["interaction"])
print("placebo_date pvalue:", m.pvalues["interaction"])
