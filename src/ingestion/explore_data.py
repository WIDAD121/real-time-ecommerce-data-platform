import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"


# List of datasets
datasets = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]


def explore_dataset(filename):
    """Load and display basic information about a dataset."""

    file_path = DATA_DIR / filename

    print("\n" + "=" * 70)
    print(f"DATASET: {filename}")
    print("=" * 70)

    df = pd.read_csv(file_path)

    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nData types:")
    print(df.dtypes)


if __name__ == "__main__":
    for dataset in datasets:
        explore_dataset(dataset)