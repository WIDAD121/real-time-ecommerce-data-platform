from pathlib import Path

from pyspark.sql import SparkSession

BASE_DIR = Path(__file__).resolve().parents[2]
orders_csv = BASE_DIR / "data" / "raw" / "olist_orders_dataset.csv"

spark = (
    SparkSession.builder
    .appName("smoke-test")
    .master("local[*]")
    .getOrCreate()
)

df = spark.read.csv(str(orders_csv), header=True, inferSchema=True)

print("Spark version:", spark.version)
print("Orders rows:", df.count())
df.select("order_id", "order_status").show(5, truncate=False)

spark.stop()