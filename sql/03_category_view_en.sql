CREATE OR REPLACE VIEW v_category_revenue_en AS
SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    COUNT(*)               AS items_sold,
    ROUND(SUM(i.price), 2) AS revenue
FROM order_items i
JOIN orders o   ON o.order_id = i.order_id
JOIN products p ON p.product_id = i.product_id
LEFT JOIN category_translation t
       ON t.product_category_name = p.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY 1;
