from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StringType, DoubleType

KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "orders"

schema = (
    StructType()
    .add("event_id", StringType())
    .add("event_type", StringType())
    .add("customer_id", StringType())
    .add("product_id", StringType())
    .add("amount", DoubleType())
    .add("timestamp", StringType())
)

spark = (
    SparkSession.builder
    .appName("stream-orders")
    .master("local[*]")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

raw = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
    .option("subscribe", TOPIC)
    .option("startingOffsets", "earliest")
    .load()
)

events = (
    raw.selectExpr("CAST(value AS STRING) AS json_str")
    .select(F.from_json("json_str", schema).alias("e"))
    .select("e.*")
    .withColumn("event_time", F.to_timestamp("timestamp"))
)

live_counts = (
    events
    .withWatermark("event_time", "1 minute")
    .groupBy(
        F.window("event_time", "30 seconds"),
        "event_type",
    )
    .agg(
        F.count("*").alias("event_count"),
        F.round(F.sum("amount"), 2).alias("total_amount"),
    )
    .orderBy("window")
)

query = (
    live_counts.writeStream
    .outputMode("complete")
    .format("console")
    .option("truncate", "false")
    .start()
)

query.awaitTermination()