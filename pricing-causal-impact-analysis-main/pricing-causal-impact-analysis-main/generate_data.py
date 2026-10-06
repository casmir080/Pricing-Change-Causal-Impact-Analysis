import numpy as np
import pandas as pd

SEED = 42
np.random.seed(SEED)

N_USERS = 50000
START_DATE = pd.Timestamp("2024-01-01")
DAYS = 180
ROLLOUT_DATE = pd.Timestamp("2024-04-01")

users = pd.DataFrame({
    "user_id": np.arange(1, N_USERS + 1),
    "signup_date": START_DATE + pd.to_timedelta(np.random.randint(0, DAYS, N_USERS), unit="D"),
    "country": np.random.choice(["US", "UK", "CA"], N_USERS, p=[0.5, 0.3, 0.2]),
    "device_type": np.random.choice(["mobile", "desktop"], N_USERS, p=[0.65, 0.35]),
    "acquisition_channel": np.random.choice(["organic", "paid", "referral"], N_USERS, p=[0.5, 0.35, 0.15]),
})

exposure_prob = (
    0.25
    + 0.15 * (users["device_type"].eq("mobile")).astype(int)
    + 0.20 * (users["acquisition_channel"].eq("paid")).astype(int)
)
exposure_prob = exposure_prob.clip(0, 0.95)

exposed = np.random.rand(N_USERS) < exposure_prob

pricing_exposure = pd.DataFrame({
    "user_id": users["user_id"],
    "exposure_date": ROLLOUT_DATE,
    "price_version": np.where(exposed, "new_price", "old_price"),
})

base_conversion = 0.12
price_penalty = np.where(pricing_exposure["price_version"].eq("new_price"), -0.02, 0.0)
conversion_prob = (base_conversion + price_penalty).clip(0.01, 0.80)

converted = np.random.rand(N_USERS) < conversion_prob

subscribe_delays = np.random.randint(1, 14, N_USERS)
subscribe_dates = users["signup_date"] + pd.to_timedelta(subscribe_delays, unit="D")

events_df = pd.DataFrame({
    "user_id": users.loc[converted, "user_id"].values,
    "event_date": subscribe_dates[converted].dt.date,
    "event_type": "subscribe",
})

old_price = 20.0
new_price = 22.0

price_map = pricing_exposure.set_index("user_id")["price_version"]
sub_user_ids = events_df["user_id"].values
sub_price_version = price_map.loc[sub_user_ids].values

amount = np.where(sub_price_version == "old_price", old_price, new_price)

revenue_df = pd.DataFrame({
    "user_id": events_df["user_id"].values,
    "event_date": events_df["event_date"].values,
    "amount": amount,
})

print("users:", users.shape)
print("pricing_exposure:", pricing_exposure.shape)
print("events:", events_df.shape)
print("revenue:", revenue_df.shape)

print(pricing_exposure["price_version"].value_counts(normalize=True).round(3))
print("conversion_rate:", round(events_df.shape[0] / N_USERS, 4))

users.to_csv("python/users.csv", index=False)
pricing_exposure.to_csv("python/pricing_exposure.csv", index=False)
events_df.to_csv("python/events.csv", index=False)
revenue_df.to_csv("python/revenue.csv", index=False)
