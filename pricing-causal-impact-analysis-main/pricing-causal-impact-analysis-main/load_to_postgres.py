import os
import pandas as pd
from sqlalchemy import create_engine, text

# ---- DB config (local learning setup) ----
DB_USER = "postgres"
DB_PASSWORD = 
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "experiments"

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

users = pd.read_csv("python/users.csv", parse_dates=["signup_date"])
pricing_exposure = pd.read_csv("python/pricing_exposure.csv", parse_dates=["exposure_date"])
events_df = pd.read_csv("python/events.csv", parse_dates=["event_date"])
revenue_df = pd.read_csv("python/revenue.csv", parse_dates=["event_date"])

users.columns = [c.strip() for c in users.columns]
pricing_exposure.columns = [c.strip() for c in pricing_exposure.columns]
events_df.columns = [c.strip() for c in events_df.columns]
revenue_df.columns = [c.strip() for c in revenue_df.columns]

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE revenue RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE events RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE pricing_exposure RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))

users.to_sql("users", engine, if_exists="append", index=False, method="multi", chunksize=5000)
pricing_exposure.to_sql("pricing_exposure", engine, if_exists="append", index=False, method="multi", chunksize=5000)
events_df.to_sql("events", engine, if_exists="append", index=False, method="multi", chunksize=5000)
revenue_df.to_sql("revenue", engine, if_exists="append", index=False, method="multi", chunksize=5000)

with engine.connect() as conn:
    for table in ["users", "pricing_exposure", "events", "revenue"]:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
        print(f"{table}: {count}")

print("Load complete.")
