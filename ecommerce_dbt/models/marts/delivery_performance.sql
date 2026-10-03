SELECT
    DATE_TRUNC('month', order_purchase_timestamp)::date AS month,
    COUNT(*) AS delivered_orders,
    ROUND(AVG(
        EXTRACT(EPOCH FROM
            (order_delivered_customer_date - order_purchase_timestamp)
        ) / 86400
    )::numeric, 1) AS avg_delivery_days,
    ROUND(100.0 * AVG(
        CASE
            WHEN order_delivered_customer_date > order_estimated_delivery_date
            THEN 1 ELSE 0
        END
    ), 1) AS pct_late
FROM {{ source('public', 'orders') }}
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
GROUP BY DATE_TRUNC('month', order_purchase_timestamp)