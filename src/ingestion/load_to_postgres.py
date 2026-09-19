import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg://"
    "ecommerce_user:ecommerce_password@localhost:5433/ecommerce"
)

engine = create_engine(DATABASE_URL)


# ============================================================
# DATASET -> POSTGRESQL TABLE MAPPING
# (order matters because of foreign keys)
# ============================================================

tables = {
    "olist_customers_dataset.csv": "customers",
    "olist_sellers_dataset.csv": "sellers",
    "olist_products_dataset.csv": "products",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews",
}


# ============================================================
# DATE COLUMNS
# ============================================================

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp",
]


# ============================================================
# HELPERS
# ============================================================

def already_loaded(table_name):
    """Return True if the table already contains rows."""
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    return count > 0


def load_table(filename, table_name):
    """Load one CSV file into one PostgreSQL table."""

    file_path = DATA_DIR / filename

    print()
    print("=" * 50)
    print(f"Loading {filename} -> {table_name}")
    print("=" * 50)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # Fix misspelled column names in the Olist products file
    df = df.rename(
        columns={
            "product_name_lenght": "product_name_length",
            "product_description_lenght": "product_description_length",
        }
    )

    # Convert date/time columns
    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=2000,
    )

    print(f"Loaded into PostgreSQL table: {table_name}")


# ============================================================
# MAIN
# Usage:
#   python src\ingestion\load_to_postgres.py            (all empty tables)
#   python src\ingestion\load_to_postgres.py payments   (one table)
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("Olist -> PostgreSQL Data Ingestion")
    print("=" * 50)

    wanted = set(sys.argv[1:])

    for filename, table_name in tables.items():

        if wanted and table_name not in wanted:
            continue

        if already_loaded(table_name):
            print(f"Skipping {table_name} (already has data)")
            continue

        try:
            load_table(filename, table_name)
        except SQLAlchemyError as e:
            print(f"\nFAILED loading {table_name}:")
            print(str(e.orig)[:800])
            sys.exit(1)

    print()
    print("=" * 50)
    print("INGESTION COMPLETED")
    print("=" * 50)