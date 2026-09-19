CREATE OR REPLACE VIEW v_daily_revenue AS
SELECT
    DATE(o.order_purchase_timestamp) AS order_date,
    COUNT(DISTINCT o.order_id)       AS orders,
    ROUND(SUM(i.price), 2)           AS revenue,
    ROUND(SUM(i.freight_value), 2)   AS freight
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE(o.order_purchase_timestamp);


CREATE OR REPLACE VIEW v_delivery_performance AS
SELECT
    DATE_TRUNC('month', order_purchase_timestamp)::date AS month,
    COUNT(*) AS delivered_orders,
    ROUND(AVG(
        EXTRACT(EPOCH FROM
            (order_delivered_customer_date
             - order_purchase_timestamp)) / 86400
    )::numeric, 1) AS avg_delivery_days,
    ROUND(100.0 * AVG(
        CASE
            WHEN order_delivered_customer_date
                 > order_estimated_delivery_date
            THEN 1 ELSE 0
        END
    ), 1) AS pct_late
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
GROUP BY DATE_TRUNC('month', order_purchase_timestamp);


CREATE OR REPLACE VIEW v_category_revenue AS
SELECT
    COALESCE(p.product_category_name, 'unknown') AS category,
    COUNT(*)                 AS items_sold,
    ROUND(SUM(i.price), 2)   AS revenue
FROM order_items i
JOIN products p ON p.product_id = i.product_id
JOIN orders o   ON o.order_id = i.order_id
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(p.product_category_name, 'unknown');