DROP TABLE IF EXISTS analytics_did_placebo_date;

CREATE TABLE analytics_did_placebo_date AS
SELECT
    u.user_id,
    CASE WHEN p.price_version = 'new_price' THEN 1 ELSE 0 END AS treated,
    CASE WHEN u.signup_date < DATE '2024-03-01' THEN 1 ELSE 0 END AS pre_period,
    CASE WHEN u.signup_date >= DATE '2024-03-01' THEN 1 ELSE 0 END AS post_period,
    CASE WHEN e.user_id IS NOT NULL THEN 1 ELSE 0 END AS converted,
    COALESCE(SUM(r.amount), 0) AS revenue
FROM users u
JOIN pricing_exposure p
  ON u.user_id = p.user_id
LEFT JOIN events e
  ON u.user_id = e.user_id
LEFT JOIN revenue r
  ON u.user_id = r.user_id
GROUP BY u.user_id, p.price_version, u.signup_date, e.user_id;

DROP TABLE IF EXISTS analytics_did_placebo_treat;

CREATE TABLE analytics_did_placebo_treat AS
SELECT
    user_id,
    CASE WHEN random() < 0.5 THEN 1 ELSE 0 END AS treated,
    post_period,
    converted,
    revenue
FROM analytics_did;

DROP TABLE IF EXISTS analytics_negative_control;

CREATE TABLE analytics_negative_control AS
SELECT
    u.user_id,
    CASE WHEN p.price_version = 'new_price' THEN 1 ELSE 0 END AS treated,
    CASE WHEN u.signup_date >= DATE '2024-04-01' THEN 1 ELSE 0 END AS post_period,
    CASE WHEN u.signup_date < DATE '2024-04-01' THEN 1 ELSE 0 END AS outcome_pre_period_user
FROM users u
JOIN pricing_exposure p
  ON u.user_id = p.user_id;
