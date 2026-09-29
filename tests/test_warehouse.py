import os
import pytest
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://"
    "ecommerce_user:ecommerce_password@localhost:5433/ecommerce",
)

@pytest.fixture(scope="module")
def conn():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        yield connection


def scalar(conn, sql):
    return conn.execute(text(sql)).scalar()


@pytest.mark.parametrize(
    "table, expected",
    [
        ("dw.dim_customer", 99441),
        ("dw.dim_product", 32951),
        ("dw.dim_seller", 3095),
        ("dw.dim_date", 774),
        ("dw.fact_sales", 112650),
    ],
)
def test_warehouse_row_counts(conn, table, expected):
    assert scalar(conn, f"""SELECT COUNT(*) FROM {table}""") == expected


def test_fact_revenue_matches_raw(conn):
    sql = """
        SELECT
          (SELECT ROUND(SUM(price), 2) FROM dw.fact_sales)
        - (SELECT ROUND(SUM(price), 2) FROM order_items)
    """
    assert scalar(conn, sql) == 0


def test_fact_freight_matches_raw(conn):
    sql = """
        SELECT
          (SELECT ROUND(SUM(freight_value), 2) FROM dw.fact_sales)
        - (SELECT ROUND(SUM(freight_value), 2) FROM order_items)
    """
    assert scalar(conn, sql) == 0


def test_total_amount_is_price_plus_freight(conn):
    sql = """
        SELECT COUNT(*) FROM dw.fact_sales
        WHERE ROUND(total_amount, 2) <> ROUND(price + freight_value, 2)
    """
    assert scalar(conn, sql) == 0


def test_no_null_categories_in_dim_product(conn):
    sql = """
        SELECT COUNT(*) FROM dw.dim_product
        WHERE category IS NULL
    """
    assert scalar(conn, sql) == 0


def test_every_fact_row_has_a_date(conn):
    sql = """
        SELECT COUNT(*) FROM dw.fact_sales f
        LEFT JOIN dw.dim_date d ON d.date_id = f.date_id
        WHERE d.date_id IS NULL
    """
    assert scalar(conn, sql) == 0


def test_delivered_rows_match_raw_orders(conn):
    sql = """
        SELECT
          (SELECT COUNT(*) FROM dw.fact_sales
             WHERE order_status = 'delivered')
        - (SELECT COUNT(*) FROM order_items i
             JOIN orders o ON o.order_id = i.order_id
             WHERE o.order_status = 'delivered')
    """
    assert scalar(conn, sql) == 0