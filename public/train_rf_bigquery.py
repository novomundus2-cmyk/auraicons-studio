#!/usr/bin/env python3
"""
train_rf_bigquery.py

Script para entrenamiento distribuido de Random Forest en PySpark conectado a Google Cloud BigQuery.
Apto para ejecución mediante:
  - gcloud dataproc jobs submit pyspark train_rf_bigquery.py ...
  - spark-submit --packages com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1 train_rf_bigquery.py
"""

import argparse
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, count, rand, round as spark_round
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, Imputer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator


def parse_args():
    parser = argparse.ArgumentParser(description="PySpark BigQuery Random Forest Pipeline")
    parser.add_argument("--project_id", default=os.getenv("GCP_PROJECT_ID", "tu-proyecto-gcp"), help="Google Cloud Project ID")
    parser.add_argument("--dataset", default=os.getenv("BQ_DATASET", "fraud_analytics"), help="BigQuery Dataset")
    parser.add_argument("--input_table", default=os.getenv("BQ_TABLE", "my_transactions"), help="BigQuery input table")
    parser.add_argument("--output_table", default=os.getenv("BQ_OUTPUT_TABLE", "transactions_scored"), help="BigQuery output table")
    parser.add_argument("--gcs_bucket", default=os.getenv("GCS_STAGING_BUCKET", "tu-bucket-staging-spark"), help="GCS staging bucket")
    parser.add_argument("--model_output", default=None, help="GCS path to save trained model")
    return parser.parse_args()


def init_spark(app_name: str, gcs_bucket: str, dataset: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1")
        .config("viewsEnabled", "true")
        .config("materializationDataset", dataset)
        .config("temporaryGcsBucket", gcs_bucket)
        .getOrCreate()
    )


def load_data(spark: SparkSession, full_table_path: str):
    try:
        print(f"[INFO] Leyendo tabla desde BigQuery: {full_table_path}...")
        df = spark.read.format("bigquery").option("table", full_table_path).load()
        print(f"[INFO] Filas leídas: {df.count()}")
        return df
    except Exception as e:
        print(f"[WARN] No se pudo leer BigQuery directamente ({str(e)[:100]}). Generando muestra sintética...")
        df_base = spark.range(0, 10000).withColumnRenamed("id", "transaction_id")
        return df_base.select(
            col("transaction_id"),
            spark_round(rand(seed=1) * 1200 + 5.0, 2).alias("amount"),
            (rand(seed=2) * 60 + 18).cast("int").alias("customer_age"),
            (rand(seed=3) * 24).cast("int").alias("transaction_hour"),
            spark_round(rand(seed=4) * 150 + 0.5, 2).alias("distance_from_home"),
            when(rand(seed=5) < 0.4, "retail")
                .when(rand(seed=5) < 0.7, "grocery")
                .when(rand(seed=5) < 0.9, "travel")
                .otherwise("electronics").alias("category"),
            when(rand(seed=6) < 0.6, "mobile")
                .when(rand(seed=6) < 0.9, "web")
                .otherwise("pos").alias("device_type"),
            when(rand(seed=7) < 0.8, "ES")
                .when(rand(seed=7) < 0.95, "US")
                .otherwise("OTHER").alias("merchant_country"),
            when((col("transaction_id") % 45 == 0) | ((rand(seed=8) > 0.92) & (col("transaction_id") % 15 == 0)), 1)
                .otherwise(0).alias("is_fraud")
        )


def build_and_train_pipeline(df):
    total_rows = df.count()
    count_fraud = df.filter(col("is_fraud") == 1).count()
    count_normal = total_rows - count_fraud

    weight_fraud = total_rows / (2.0 * count_fraud) if count_fraud > 0 else 1.0
    weight_normal = total_rows / (2.0 * count_normal) if count_normal > 0 else 1.0

    df_weighted = df.withColumn(
        "class_weight",
        when(col("is_fraud") == 1, weight_fraud).otherwise(weight_normal)
    ).withColumn("label", col("is_fraud").cast("double"))

    numeric_cols = ["amount", "customer_age", "transaction_hour", "distance_from_home"]
    categorical_cols = ["category", "device_type", "merchant_country"]

    indexers = [StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep") for c in categorical_cols]
    encoders = [OneHotEncoder(inputCol=f"{c}_idx", outputCol=f"{c}_vec") for c in categorical_cols]
    imputer = Imputer(inputCols=numeric_cols, outputCols=[f"{c}_imp" for c in numeric_cols], strategy="median")
    feature_inputs = [f"{c}_imp" for c in numeric_cols] + [f"{c}_vec" for c in categorical_cols]
    assembler = VectorAssembler(inputCols=feature_inputs, outputCol="features")

    prep_pipeline = Pipeline(stages=indexers + encoders + [imputer, assembler])
    prep_model = prep_pipeline.fit(df_weighted)
    df_processed = prep_model.transform(df_weighted)

    train_df, test_df = df_processed.randomSplit([0.8, 0.2], seed=42)

    rf = RandomForestClassifier(featuresCol="features", labelCol="label", weightCol="class_weight", seed=42)
    param_grid = ParamGridBuilder().addGrid(rf.numTrees, [30, 60]).addGrid(rf.maxDepth, [5, 8]).build()
    evaluator_pr = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderPR")

    crossval = CrossValidator(estimator=rf, estimatorParamMaps=param_grid, evaluator=evaluator_pr, numFolds=3, seed=42)
    print("[INFO] Entrenando modelo con validación cruzada...")
    cv_model = crossval.fit(train_df)
    best_model = cv_model.bestModel

    predictions = best_model.transform(test_df)
    pr_auc = evaluator_pr.evaluate(predictions)
    evaluator_roc = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    roc_auc = evaluator_roc.evaluate(predictions)

    print("=" * 45)
    print(f"MÉTRICAS DEL MODELO (TEST):")
    print(f"  - PR-AUC:  {pr_auc:.4f}")
    print(f"  - ROC-AUC: {roc_auc:.4f}")
    print("=" * 45)

    return best_model, predictions


def main():
    args = parse_args()
    spark = init_spark("PySpark_BigQuery_RF_Runner", args.gcs_bucket, args.dataset)

    full_table = f"{args.project_id}.{args.dataset}.{args.input_table}"
    df = load_data(spark, full_table)
    model, predictions = build_and_train_pipeline(df)

    if args.model_output:
        print(f"[INFO] Guardando modelo en: {args.model_output}")
        model.write().overwrite().save(args.model_output)

    output_table_full = f"{args.project_id}.{args.dataset}.{args.output_table}"
    df_scored = predictions.select(
        "transaction_id", "amount", "label", "prediction", col("probability").cast("string").alias("probability_vector")
    )

    try:
        print(f"[INFO] Guardando predicciones en BigQuery: {output_table_full}...")
        df_scored.write.format("bigquery").option("table", output_table_full).mode("overwrite").save()
        print("[INFO] Predicciones persistidas correctamente.")
    except Exception as e:
        print(f"[WARN] No se pudo escribir en BigQuery ({str(e)[:90]}). Mostrando 5 resultados locales:")
        df_scored.show(5)

    spark.stop()


if __name__ == "__main__":
    main()
