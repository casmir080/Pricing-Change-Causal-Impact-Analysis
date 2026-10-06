
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    signup_date DATE NOT NULL,
    country TEXT NOT NULL,
    device_type TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pricing_exposure (
    user_id INTEGER PRIMARY KEY,
    exposure_date DATE NOT NULL,
    price_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    user_id INTEGER NOT NULL,
    event_date DATE NOT NULL,
    event_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS revenue (
    user_id INTEGER NOT NULL,
    event_date DATE NOT NULL,
    amount NUMERIC NOT NULL
);
