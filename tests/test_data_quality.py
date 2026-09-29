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


# ------------------------------------------------------------
# Row counts (must match the source CSV files)
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "table, expected",
    [
        ("customers", 99441),
        ("sellers", 3095),
        ("products", 32951),
        ("orders", 99441),
        ("order_items", 112650),
        ("payments", 103886),
        ("reviews", 99224),
    ],
)
def test_row_counts(conn, table, expected):
    assert scalar(conn, f"""SELECT COUNT(*) FROM {table}""") == expected


# ------------------------------------------------------------
# Referential integrity (no orphan rows)
# ------------------------------------------------------------

def test_no_orphan_orders(conn):
    sql = """
        SELECT COUNT(*) FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """
    assert scalar(conn, sql) == 0


def test_no_orphan_order_items(conn):
    sql = """
        SELECT COUNT(*) FROM order_items i
        LEFT JOIN orders o   ON i.order_id = o.order_id
        LEFT JOIN products p ON i.product_id = p.product_id
        LEFT JOIN sellers s  ON i.seller_id = s.seller_id
        WHERE o.order_id IS NULL
           OR p.product_id IS NULL
           OR s.seller_id IS NULL
    """
    assert scalar(conn, sql) == 0


def test_no_orphan_payments_and_reviews(conn):
    sql = """
        SELECT
          (SELECT COUNT(*) FROM payments p
             LEFT JOIN orders o ON p.order_id = o.order_id
             WHERE o.order_id IS NULL)
        + (SELECT COUNT(*) FROM reviews r
             LEFT JOIN orders o ON r.order_id = o.order_id
             WHERE o.order_id IS NULL)
    """
    assert scalar(conn, sql) == 0


# ------------------------------------------------------------
# Null checks on important columns
# ------------------------------------------------------------

def test_orders_required_fields_not_null(conn):
    sql = """
        SELECT COUNT(*) FROM orders
        WHERE customer_id IS NULL
           OR order_status IS NULL
           OR order_purchase_timestamp IS NULL
    """
    assert scalar(conn, sql) == 0


# ------------------------------------------------------------
# Value ranges
# ------------------------------------------------------------

def test_prices_and_freight_not_negative(conn):
    sql = """
        SELECT COUNT(*) FROM order_items
        WHERE price < 0
           OR freight_value < 0
    """
    assert scalar(conn, sql) == 0


def test_payment_values_not_negative(conn):
    sql = """
        SELECT COUNT(*) FROM payments
        WHERE payment_value < 0
    """
    assert scalar(conn, sql) == 0


def test_review_scores_between_1_and_5(conn):
    sql = """
        SELECT COUNT(*) FROM reviews
        WHERE review_score NOT BETWEEN 1 AND 5
    """
    assert scalar(conn, sql) == 0


def test_order_status_values_are_known(conn):
    sql = """
        SELECT COUNT(*) FROM orders
        WHERE order_status NOT IN (
            'delivered', 'shipped', 'canceled', 'unavailable',
            'invoiced', 'processing', 'created', 'approved'
        )
    """
    assert scalar(conn, sql) == 0