SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    COUNT(*)               AS items_sold,
    ROUND(SUM(i.price), 2) AS revenue
FROM {{ source('public', 'order_items') }} i
JOIN {{ source('public', 'orders') }} o
    ON o.order_id = i.order_id
JOIN {{ source('public', 'products') }} p
    ON p.product_id = i.product_id
LEFT JOIN {{ source('public', 'category_translation') }} t
    ON t.product_category_name = p.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY revenue DESC