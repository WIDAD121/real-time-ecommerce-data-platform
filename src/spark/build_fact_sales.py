from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

BASE_DIR = Path(__file__).resolve().parents[2]
RAW = BASE_DIR / "data" / "raw"
OUT = BASE_DIR / "data" / "processed" / "fact_sales"

EXPECTED_ROWS = 112650
EXPECTED_REVENUE = 13591643.70

spark = (
    SparkSession.builder
    .appName("build-fact-sales")
    .master("local[*]")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

orders = spark.read.csv(
    str(RAW / "olist_orders_dataset.csv"),
    header=True, inferSchema=True,
)
items = spark.read.csv(
    str(RAW / "olist_order_items_dataset.csv"),
    header=True, inferSchema=True,
)

fact = (
    items.join(orders, "order_id")
    .select(
        "order_id",
        "order_item_id",
        "customer_id",
        "product_id",
        "seller_id",
        F.date_format(
            F.to_timestamp("order_purchase_timestamp"), "yyyyMMdd"
        ).cast("int").alias("date_id"),
        "order_status",
        F.col("price").cast("decimal(10,2)").alias("price"),
        F.col("freight_value").cast("decimal(10,2)").alias("freight_value"),
    )
    .withColumn("total_amount", F.col("price") + F.col("freight_value"))
)

# ---------------- validate against the SQL warehouse ----------------
rows = fact.count()
revenue = float(fact.agg(F.round(F.sum("price"), 2)).first()[0])

print()
print("Spark fact rows   :", rows, "(expected", EXPECTED_ROWS, ")")
print("Spark fact revenue:", revenue, "(expected", EXPECTED_REVENUE, ")")

assert rows == EXPECTED_ROWS, "Row count does not match the SQL warehouse"
assert abs(revenue - EXPECTED_REVENUE) < 0.01, "Revenue does not match"
print("VALIDATION PASSED: Spark matches the SQL warehouse")

# ---------------- try writing Parquet ----------------
try:
    fact.write.mode("overwrite").parquet(str(OUT))
    print("Parquet written to:", OUT)
except Exception as e:
    print()
    print("PARQUET WRITE FAILED (validation above still counts):")
    print(str(e)[:400])

spark.stop()
