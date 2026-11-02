import sqlite3
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg as _avg, col, count, from_json, sum as _sum, to_timestamp, when, window
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

DB_PATH = Path("/opt/bitnami/spark/database/financial_lakehouse.db")
LOCAL_FALLBACK_DB = (
    Path(__file__).resolve().parent.parent.parent / "04_database_lakehouse" / "financial_lakehouse.db"
)


def get_db_path() -> Path:
    return DB_PATH if DB_PATH.parent.exists() else LOCAL_FALLBACK_DB


def save_microbatch_to_sqlite(batch_df, batch_id: int) -> None:
    rows = batch_df.collect()
    if not rows:
        return
    target_db = get_db_path()
    conn = sqlite3.connect(target_db)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS streaming_window_sinks (
            window_start TEXT NOT NULL,
            window_end TEXT NOT NULL,
            merchant_category TEXT NOT NULL,
            txn_count INTEGER NOT NULL,
            total_volume_eur REAL NOT NULL,
            avg_txn_amount REAL NOT NULL,
            suspicious_txn_count INTEGER NOT NULL,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    payload = [
        (
            str(r["window"]["start"]),
            str(r["window"]["end"]),
            str(r["merchant_category"]),
            int(r["txn_count"]),
            round(float(r["total_volume_eur"]), 2),
            round(float(r["avg_txn_amount"]), 2),
            int(r["suspicious_txn_count"]),
        )
        for r in rows
    ]
    conn.executemany(
        """
        INSERT INTO streaming_window_sinks
        (window_start, window_end, merchant_category, txn_count, total_volume_eur, avg_txn_amount, suspicious_txn_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        payload,
    )
    conn.commit()
    conn.close()
    print(f"💾 [Batch #{batch_id}] {len(payload)} agregaciones guardadas en {target_db.name}")


def build_spark_session():
    return (
        SparkSession.builder.appName("RealTimeTransactionAnalytics")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .getOrCreate()
    )


def main():
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    schema = StructType(
        [
            StructField("transaction_id", StringType(), False),
            StructField("user_id", StringType(), False),
            StructField("merchant_id", StringType(), True),
            StructField("merchant_name", StringType(), True),
            StructField("amount", DoubleType(), False),
            StructField("currency", StringType(), True),
            StructField("merchant_category", StringType(), True),
            StructField("device", StringType(), True),
            StructField("country", StringType(), True),
            StructField("risk_tier", StringType(), True),
            StructField("timestamp", StringType(), False),
        ]
    )

    kafka_raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka:29092")
        .option("subscribe", "financial_transactions")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed_stream = (
        kafka_raw.selectExpr("CAST(key AS STRING) as user_key", "CAST(value AS STRING) as json_payload")
        .select(from_json(col("json_payload"), schema).alias("data"))
        .select("data.*")
        .withColumn("event_time", to_timestamp(col("timestamp")))
    )

    windowed_aggregates = (
        parsed_stream.withWatermark("event_time", "10 minutes")
        .groupBy(window(col("event_time"), "1 minute"), col("merchant_category"))
        .agg(
            count("transaction_id").alias("txn_count"),
            _sum("amount").alias("total_volume_eur"),
            _avg("amount").alias("avg_txn_amount"),
            _sum(when(col("amount") > 2500, 1).otherwise(0)).alias("suspicious_txn_count"),
        )
    )

    query = (
        windowed_aggregates.writeStream.outputMode("update")
        .foreachBatch(save_microbatch_to_sqlite)
        .trigger(processingTime="10 seconds")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
