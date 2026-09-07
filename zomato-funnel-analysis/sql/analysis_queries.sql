-- =============================================================================
--  Zomato Food Delivery — SQL Analysis Queries
--  Author: [Your Name]
--  Purpose: Product analytics queries that can run on the generated dataset.
--           Demonstrates SQL proficiency for Product Analyst interviews.
--  Note: These queries are written for SQLite / PostgreSQL compatibility.
--        Load the CSVs into a database to run them.
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 1: Overall Funnel Conversion Rates
-- Business Question: What is the step-wise and overall conversion rate?
-- ─────────────────────────────────────────────────────────────────────────────

WITH funnel_counts AS (
    SELECT
        event_type,
        COUNT(*) AS event_count,
        COUNT(DISTINCT user_id) AS unique_users
    FROM funnel_events
    GROUP BY event_type
),
ordered_funnel AS (
    SELECT
        event_type,
        event_count,
        unique_users,
        CASE event_type
            WHEN 'session_start'     THEN 1
            WHEN 'search'            THEN 2
            WHEN 'restaurant_click'  THEN 3
            WHEN 'add_to_cart'       THEN 4
            WHEN 'checkout_attempt'  THEN 5
            WHEN 'order_placed'      THEN 6
        END AS stage_order
    FROM funnel_counts
    WHERE event_type NOT IN ('payment_failed')
)
SELECT
    event_type AS stage,
    event_count,
    unique_users,
    ROUND(event_count * 100.0 / 
        (SELECT event_count FROM ordered_funnel WHERE stage_order = 1), 2
    ) AS pct_of_sessions,
    ROUND(event_count * 100.0 / 
        LAG(event_count) OVER (ORDER BY stage_order), 2
    ) AS step_conversion_rate
FROM ordered_funnel
ORDER BY stage_order;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 2: Funnel Conversion by User Segment
-- Business Question: How do New vs Returning vs Power users convert?
-- ─────────────────────────────────────────────────────────────────────────────

WITH segment_funnel AS (
    SELECT
        user_segment,
        event_type,
        COUNT(*) AS cnt
    FROM funnel_events
    WHERE event_type IN ('session_start', 'order_placed')
    GROUP BY user_segment, event_type
)
SELECT
    s.user_segment,
    s.cnt AS sessions,
    COALESCE(o.cnt, 0) AS orders,
    ROUND(COALESCE(o.cnt, 0) * 100.0 / s.cnt, 2) AS conversion_rate
FROM segment_funnel s
LEFT JOIN segment_funnel o 
    ON s.user_segment = o.user_segment 
    AND o.event_type = 'order_placed'
WHERE s.event_type = 'session_start'
ORDER BY conversion_rate DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 3: Cart Abandonment Analysis
-- Business Question: What is the abandonment rate and what are the top reasons?
-- ─────────────────────────────────────────────────────────────────────────────

-- 3a: Overall abandonment rate
SELECT
    COUNT(*) AS total_carts,
    SUM(CASE WHEN abandoned = 'True' THEN 1 ELSE 0 END) AS abandoned_carts,
    ROUND(SUM(CASE WHEN abandoned = 'True' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) 
        AS abandonment_rate_pct
FROM cart_events;

-- 3b: Abandonment reasons ranked
SELECT
    abandonment_reason,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_of_abandoned
FROM cart_events
WHERE abandoned = 'True'
    AND abandonment_reason IS NOT NULL
GROUP BY abandonment_reason
ORDER BY count DESC;

-- 3c: Abandonment rate by delivery fee bracket
SELECT
    CASE
        WHEN delivery_fee = 0 THEN 'Free (₹0)'
        WHEN delivery_fee <= 20 THEN '₹1-20'
        WHEN delivery_fee <= 40 THEN '₹21-40'
        ELSE '₹41+'
    END AS fee_bracket,
    COUNT(*) AS total_carts,
    SUM(CASE WHEN abandoned = 'True' THEN 1 ELSE 0 END) AS abandoned,
    ROUND(SUM(CASE WHEN abandoned = 'True' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) 
        AS abandonment_rate
FROM cart_events
GROUP BY fee_bracket
ORDER BY abandonment_rate;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 4: Peak Hours Analysis
-- Business Question: When are the highest-converting hours?
-- ─────────────────────────────────────────────────────────────────────────────

WITH hourly_data AS (
    SELECT
        s.hour_of_day,
        COUNT(DISTINCT CASE WHEN f.event_type = 'session_start' THEN f.session_id END) AS sessions,
        COUNT(DISTINCT CASE WHEN f.event_type = 'order_placed' THEN f.session_id END) AS orders
    FROM funnel_events f
    JOIN sessions s ON f.session_id = s.session_id
    GROUP BY s.hour_of_day
)
SELECT
    hour_of_day,
    sessions,
    orders,
    ROUND(orders * 100.0 / NULLIF(sessions, 0), 2) AS conversion_rate,
    CASE 
        WHEN hour_of_day BETWEEN 12 AND 14 THEN 'Lunch Peak'
        WHEN hour_of_day BETWEEN 19 AND 22 THEN 'Dinner Peak'
        ELSE 'Off-Peak'
    END AS time_slot
FROM hourly_data
ORDER BY hour_of_day;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 5: User Retention — Repeat Orders within 7 / 14 / 30 days
-- Business Question: What % of users reorder within different time windows?
-- ─────────────────────────────────────────────────────────────────────────────

WITH user_orders AS (
    SELECT
        user_id,
        timestamp AS order_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp) AS order_num
    FROM orders
),
first_and_second AS (
    SELECT
        a.user_id,
        a.order_date AS first_order,
        MIN(b.order_date) AS second_order
    FROM user_orders a
    LEFT JOIN user_orders b 
        ON a.user_id = b.user_id AND b.order_num > a.order_num
    WHERE a.order_num = 1
    GROUP BY a.user_id, a.order_date
)
SELECT
    COUNT(*) AS total_first_time_orderers,
    SUM(CASE WHEN julianday(second_order) - julianday(first_order) <= 7 THEN 1 ELSE 0 END) 
        AS reorder_within_7d,
    SUM(CASE WHEN julianday(second_order) - julianday(first_order) <= 14 THEN 1 ELSE 0 END) 
        AS reorder_within_14d,
    SUM(CASE WHEN julianday(second_order) - julianday(first_order) <= 30 THEN 1 ELSE 0 END) 
        AS reorder_within_30d,
    ROUND(SUM(CASE WHEN julianday(second_order) - julianday(first_order) <= 7 THEN 1 ELSE 0 END) 
        * 100.0 / COUNT(*), 2) AS pct_7d,
    ROUND(SUM(CASE WHEN julianday(second_order) - julianday(first_order) <= 14 THEN 1 ELSE 0 END) 
        * 100.0 / COUNT(*), 2) AS pct_14d,
    ROUND(SUM(CASE WHEN julianday(second_order) - julianday(first_order) <= 30 THEN 1 ELSE 0 END) 
        * 100.0 / COUNT(*), 2) AS pct_30d
FROM first_and_second;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 6: Restaurant Performance Scorecard
-- Business Question: Which restaurants are top/bottom performers?
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    r.restaurant_id,
    r.name,
    r.cuisine,
    r.city,
    r.rating AS listing_rating,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.final_order_value), 0) AS total_revenue,
    ROUND(AVG(o.final_order_value), 0) AS avg_order_value,
    ROUND(AVG(o.delivery_time_mins), 1) AS avg_delivery_time,
    ROUND(AVG(o.rating_given), 2) AS avg_order_rating,
    ROUND(SUM(CASE WHEN o.rating_given <= 2 THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(o.rating_given), 0), 2) AS pct_negative_ratings
FROM restaurants r
LEFT JOIN orders o ON r.restaurant_id = o.restaurant_id
GROUP BY r.restaurant_id, r.name, r.cuisine, r.city, r.rating
HAVING total_orders > 0
ORDER BY total_orders DESC
LIMIT 20;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 7: Coupon Impact on Conversion & AOV
-- Business Question: Do coupons improve conversion? At what cost?
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    CASE WHEN coupon_applied = 'True' THEN 'With Coupon' ELSE 'Without Coupon' END AS coupon_status,
    COUNT(*) AS total_carts,
    SUM(CASE WHEN abandoned = 'False' THEN 1 ELSE 0 END) AS completed,
    ROUND(SUM(CASE WHEN abandoned = 'False' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) 
        AS checkout_rate,
    ROUND(AVG(cart_value), 0) AS avg_cart_value,
    ROUND(AVG(CASE WHEN abandoned = 'False' THEN cart_value - discount + delivery_fee END), 0) 
        AS avg_final_value
FROM cart_events
GROUP BY coupon_status;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 8: City × Cuisine Revenue Matrix
-- Business Question: Which cuisine performs best in which city?
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    city,
    cuisine,
    COUNT(*) AS orders,
    ROUND(SUM(final_order_value), 0) AS revenue,
    ROUND(AVG(final_order_value), 0) AS aov
FROM orders
GROUP BY city, cuisine
HAVING orders >= 5
ORDER BY city, revenue DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 9: Payment Method Analysis
-- Business Question: How do payment methods affect order completion?
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_of_orders,
    ROUND(AVG(final_order_value), 0) AS avg_order_value,
    ROUND(SUM(final_order_value), 0) AS total_revenue
FROM orders
GROUP BY payment_method
ORDER BY total_orders DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 10: Weekly Trend — Orders, Revenue, AOV
-- Business Question: What is the growth trend over the analysis period?
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    strftime('%Y-W%W', timestamp) AS week,
    COUNT(*) AS orders,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(SUM(final_order_value), 0) AS revenue,
    ROUND(AVG(final_order_value), 0) AS aov,
    ROUND(AVG(delivery_time_mins), 1) AS avg_delivery_time
FROM orders
GROUP BY week
ORDER BY week;
