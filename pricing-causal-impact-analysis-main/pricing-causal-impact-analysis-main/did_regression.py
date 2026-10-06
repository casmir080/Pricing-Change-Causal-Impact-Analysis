import pandas as pd
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "experiments"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
df = pd.read_sql("""
    SELECT
        treated,
        post_period,
        converted
    FROM public.analytics_did
""", engine)

print(df.head())
print(df.shape)
df["interaction"] = df["treated"] * df["post_period"]

print(df[["treated", "post_period", "interaction"]].head(10))
import statsmodels.api as sm

X = df[["treated", "post_period", "interaction"]]
X = sm.add_constant(X)

y = df["converted"]

model = sm.OLS(y, X).fit(cov_type="HC3")
print(model.summary())
coef = model.params["interaction"]
se = model.bse["interaction"]
pval = model.pvalues["interaction"]

print("\nDID interaction results")
print("coef:", round(coef, 6))
print("se:", round(se, 6))
print("pvalue:", round(pval, 6))
