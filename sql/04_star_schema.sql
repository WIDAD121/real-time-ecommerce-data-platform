DROP SCHEMA IF EXISTS dw CASCADE;
CREATE SCHEMA dw;

-- Dimension: date
CREATE TABLE dw.dim_date AS
SELECT
    TO_CHAR(d, 'YYYYMMDD')::int  AS date_id,
    d::date                      AS full_date,
    EXTRACT(YEAR FROM d)::int    AS year,
    EXTRACT(MONTH FROM d)::int   AS month,
    TO_CHAR(d, 'Month')          AS month_name,
    EXTRACT(DAY FROM d)::int     AS day,
    TO_CHAR(d, 'Day')            AS day_name,
    EXTRACT(ISODOW FROM d) IN (6, 7) AS is_weekend
FROM generate_series(
    (SELECT MIN(DATE(order_purchase_timestamp)) FROM orders),
    (SELECT MAX(DATE(order_purchase_timestamp)) FROM orders),
    INTERVAL '1 day'
) AS d;
ALTER TABLE dw.dim_date ADD PRIMARY KEY (date_id);

-- Dimension: customer
CREATE TABLE dw.dim_customer AS
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM customers;
ALTER TABLE dw.dim_customer ADD PRIMARY KEY (customer_id);

-- Dimension: product (with English category)
CREATE TABLE dw.dim_product AS
SELECT
    p.product_id,
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    p.product_weight_g,
    p.product_photos_qty
FROM products p
LEFT JOIN category_translation t
       ON t.product_category_name = p.product_category_name;
ALTER TABLE dw.dim_product ADD PRIMARY KEY (product_id);

-- Dimension: seller
CREATE TABLE dw.dim_seller AS
SELECT
    seller_id,
    seller_city,
    seller_state
FROM sellers;
ALTER TABLE dw.dim_seller ADD PRIMARY KEY (seller_id);

-- Fact: one row per order item
CREATE TABLE dw.fact_sales AS
SELECT
    i.order_id,
    i.order_item_id,
    o.customer_id,
    i.product_id,
    i.seller_id,
    TO_CHAR(o.order_purchase_timestamp, 'YYYYMMDD')::int AS date_id,
    o.order_status,
    i.price,
    i.freight_value,
    i.price + i.freight_value AS total_amount
FROM order_items i
JOIN orders o ON o.order_id = i.order_id;

ALTER TABLE dw.fact_sales ADD PRIMARY KEY (order_id, order_item_id);
ALTER TABLE dw.fact_sales
    ADD FOREIGN KEY (customer_id) REFERENCES dw.dim_customer(customer_id);
ALTER TABLE dw.fact_sales
    ADD FOREIGN KEY (product_id) REFERENCES dw.dim_product(product_id);
ALTER TABLE dw.fact_sales
    ADD FOREIGN KEY (seller_id) REFERENCES dw.dim_seller(seller_id);
ALTER TABLE dw.fact_sales
    ADD FOREIGN KEY (date_id) REFERENCES dw.dim_date(date_id);