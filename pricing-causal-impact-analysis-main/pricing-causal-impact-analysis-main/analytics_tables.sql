DROP TABLE IF EXISTS analytics_user_level;

CREATE TABLE analytics_user_level AS
SELECT
    u.user_id,

    CASE
        WHEN p.price_version = 'new_price' THEN 1
        ELSE 0
    END AS treated,

    u.signup_date,
    u.country,
    u.device_type,
    u.acquisition_channel,

    CASE
        WHEN u.signup_date < DATE '2024-04-01' THEN 1
        ELSE 0
    END AS pre_period,

    CASE
        WHEN u.signup_date >= DATE '2024-04-01' THEN 1
        ELSE 0
    END AS post_period,

    CASE
        WHEN e.user_id IS NOT NULL THEN 1
        ELSE 0
    END AS converted,

    COALESCE(SUM(r.amount), 0) AS revenue

FROM users u
JOIN pricing_exposure p
  ON u.user_id = p.user_id
LEFT JOIN events e
  ON u.user_id = e.user_id
LEFT JOIN revenue r
  ON u.user_id = r.user_id

GROUP BY
    u.user_id,
    p.price_version,
    u.signup_date,
    u.country,
    u.device_type,
    u.acquisition_channel,
    e.user_id;

DROP TABLE IF EXISTS analytics_did;

CREATE TABLE analytics_did AS
SELECT
    user_id,
    treated,
    pre_period,
    post_period,
    converted,
    revenue
FROM analytics_user_level;

DROP TABLE IF EXISTS psm_base;

CREATE TABLE psm_base AS
SELECT
    u.user_id,
    CASE WHEN p.price_version = 'new_price' THEN 1 ELSE 0 END AS treated,
    u.country,
    u.device_type,
    u.acquisition_channel,
    CASE WHEN u.signup_date < DATE '2024-04-01' THEN 1 ELSE 0 END AS pre_period_user,
    CASE WHEN e.user_id IS NOT NULL THEN 1 ELSE 0 END AS converted,
    COALESCE(SUM(r.amount), 0) AS revenue
FROM users u
JOIN pricing_exposure p
  ON u.user_id = p.user_id
LEFT JOIN events e
  ON u.user_id = e.user_id
LEFT JOIN revenue r
  ON u.user_id = r.user_id
GROUP BY
    u.user_id,
    p.price_version,
    u.country,
    u.device_type,
    u.acquisition_channel,
    u.signup_date,
    e.user_id;
