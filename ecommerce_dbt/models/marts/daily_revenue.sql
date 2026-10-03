SELECT
    DATE(o.order_purchase_timestamp) AS order_date,
    COUNT(DISTINCT o.order_id)       AS orders,
    ROUND(SUM(i.price), 2)           AS revenue,
    ROUND(SUM(i.freight_value), 2)   AS freight
FROM {{ source('public', 'orders') }} o
JOIN {{ source('public', 'order_items') }} i ON i.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE(o.order_purchase_timestamp)