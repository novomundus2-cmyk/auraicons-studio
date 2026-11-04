#!/usr/bin/env python3
"""Laboratorio PySpark Random Forest; demo local explícita y BigQuery opcional.

Ejemplo local: python train_rf_bigquery.py --demo
BigQuery requiere credenciales y un conector compatibles en el entorno elegido.
Las escrituras solo ocurren al proporcionar --output_table o --model_output.
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import unquote, urlsplit

from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.base import Estimator, Transformer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import Imputer, OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.functions import vector_to_array
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, rand, when
from pyspark.sql.functions import round as spark_round
from pyspark.sql.types import NumericType, StringType

NUMERIC_COLUMNS = ("amount", "customer_age", "transaction_hour", "distance_from_home")
CATEGORICAL_COLUMNS = ("category", "device_type", "merchant_country")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demo", action="store_true", help="Usar solo datos sintéticos locales"
    )
    parser.add_argument("--project_id", default=os.getenv("GCP_PROJECT_ID"))
    parser.add_argument("--dataset", default=os.getenv("BQ_DATASET", "fraud_analytics"))
    parser.add_argument(
        "--input_table", default=os.getenv("BQ_TABLE", "my_transactions")
    )
    parser.add_argument(
        "--output_table", help="Tabla nueva de destino; no se sobrescriben tablas"
    )
    parser.add_argument("--gcs_bucket", default=os.getenv("GCS_STAGING_BUCKET"))
    parser.add_argument(
        "--model_output", help="Ruta nueva para guardar el PipelineModel completo"
    )
    args = parser.parse_args(argv)
    if not args.demo and (not args.project_id or args.project_id == "tu-proyecto-gcp"):
        parser.error("Indica --demo o un --project_id real para leer BigQuery")
    if args.demo and args.output_table:
        parser.error("El modo demo solo permite guardar modelos en rutas locales")
    if args.demo and args.model_output:
        location = urlsplit(args.model_output)
        if location.scheme not in ("", "file") or location.netloc:
            parser.error("El modo demo solo permite guardar modelos en rutas locales")
        if location.scheme == "file" and (
            not location.path.startswith("/") or location.query or location.fragment
        ):
            parser.error("Indica una URI file absoluta sin query ni fragmento")
        local_path = unquote(location.path) if location.scheme else args.model_output
        # Explicitar file evita heredar un filesystem remoto de la configuración Hadoop.
        args.model_output = Path(local_path).expanduser().resolve().as_uri()
    return args


def init_spark(
    app_name: str,
    gcs_bucket: str | None = None,
    dataset: str | None = None,
    *,
    demo: bool = False,
) -> SparkSession:
    builder = SparkSession.builder.appName(app_name)
    if demo:
        builder = builder.master("local[2]").config("spark.sql.shuffle.partitions", "2")
    else:
        builder = builder.config(
            "spark.jars.packages",
            "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1",
        )
        if dataset:
            builder = builder.config("viewsEnabled", "true").config(
                "materializationDataset", dataset
            )
        if gcs_bucket:
            builder = builder.config("temporaryGcsBucket", gcs_bucket)
    return builder.getOrCreate()


def synthetic_transactions(spark: SparkSession, rows: int = 10000) -> DataFrame:
    """Generar datos didácticos, sin inferir resultados sobre fraude real."""
    return (
        spark.range(rows)
        .withColumnRenamed("id", "transaction_id")
        .select(
            col("transaction_id"),
            spark_round(rand(seed=1) * 1200 + 5.0, 2).alias("amount"),
            (rand(seed=2) * 60 + 18).cast("int").alias("customer_age"),
            (rand(seed=3) * 24).cast("int").alias("transaction_hour"),
            spark_round(rand(seed=4) * 150 + 0.5, 2).alias("distance_from_home"),
            when(rand(seed=5) < 0.4, "retail").otherwise("grocery").alias("category"),
            when(rand(seed=6) < 0.6, "mobile").otherwise("web").alias("device_type"),
            when(rand(seed=7) < 0.8, "ES").otherwise("OTHER").alias("merchant_country"),
            when(col("transaction_id") % 45 == 0, 1).otherwise(0).alias("is_fraud"),
        )
    )


def load_data(spark: SparkSession, full_table_path: str) -> DataFrame:
    """Propagar los errores de lectura; nunca sustituir datos reales por una demo."""
    return spark.read.format("bigquery").option("table", full_table_path).load()


def validate_training_data(df: DataFrame) -> None:
    required = {"transaction_id", "is_fraud", *NUMERIC_COLUMNS, *CATEGORICAL_COLUMNS}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(missing))}")
    for name in (*NUMERIC_COLUMNS, "is_fraud"):
        if not isinstance(df.schema[name].dataType, NumericType):
            raise TypeError(f"La columna {name} debe ser numérica")
    for name in CATEGORICAL_COLUMNS:
        if not isinstance(df.schema[name].dataType, StringType):
            raise TypeError(f"La columna {name} debe ser texto")
    invalid = col("is_fraud").isNull() | ~col("is_fraud").isin(0, 1)
    if df.filter(invalid).limit(1).count():
        raise ValueError("is_fraud solo admite 0 y 1, sin nulos")


def class_counts(df: DataFrame) -> dict[int, int]:
    counts = {
        int(row["label"]): row["count"] for row in df.groupBy("label").count().collect()
    }
    if set(counts) != {0, 1}:
        raise ValueError(
            "Cada partición de entrenamiento/evaluación necesita ambas clases"
        )
    return counts


def feature_stages() -> list[Estimator | Transformer]:
    indexers = [
        StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep")
        for c in CATEGORICAL_COLUMNS
    ]
    encoders = [
        OneHotEncoder(inputCol=f"{c}_idx", outputCol=f"{c}_vec", handleInvalid="keep")
        for c in CATEGORICAL_COLUMNS
    ]
    imputed = [f"{c}_imp" for c in NUMERIC_COLUMNS]
    imputer = Imputer(
        inputCols=list(NUMERIC_COLUMNS), outputCols=imputed, strategy="median"
    )
    assembler = VectorAssembler(
        inputCols=imputed + [f"{c}_vec" for c in CATEGORICAL_COLUMNS],
        outputCol="features",
    )
    return [*indexers, *encoders, imputer, assembler]


def build_and_train_pipeline(
    df: DataFrame,
    *,
    num_trees: Sequence[int] = (30, 60),
    max_depths: Sequence[int] = (5, 8),
    num_folds: int = 3,
) -> tuple[PipelineModel, DataFrame]:
    validate_training_data(df)
    train_df, test_df = df.withColumn(
        "label", col("is_fraud").cast("double")
    ).randomSplit([0.8, 0.2], seed=42)
    counts = class_counts(train_df)
    class_counts(test_df)
    if min(counts.values()) < num_folds:
        raise ValueError("Hay pocos ejemplos por clase para los folds solicitados")
    total = sum(counts.values())
    train_df = train_df.withColumn(
        "class_weight",
        when(col("label") == 1, total / (2.0 * counts[1])).otherwise(
            total / (2.0 * counts[0])
        ),
    )
    rf = RandomForestClassifier(
        featuresCol="features", labelCol="label", weightCol="class_weight", seed=42
    )
    pipeline = Pipeline(stages=[*feature_stages(), rf])
    grid = (
        ParamGridBuilder()
        .addGrid(rf.numTrees, list(num_trees))
        .addGrid(rf.maxDepth, list(max_depths))
        .build()
    )
    evaluator = BinaryClassificationEvaluator(
        labelCol="label", metricName="areaUnderPR"
    )
    # CrossValidator vuelve a ajustar también el preprocesado dentro de cada fold.
    crossval = CrossValidator(
        estimator=pipeline,
        estimatorParamMaps=grid,
        evaluator=evaluator,
        numFolds=num_folds,
        seed=42,
    )
    model = crossval.fit(train_df).bestModel
    predictions = model.transform(test_df)
    print(f"PR-AUC (test): {evaluator.evaluate(predictions):.4f}")
    evaluator.setMetricName("areaUnderROC")
    print(f"ROC-AUC (test): {evaluator.evaluate(predictions):.4f}")
    return model, predictions


def scored_rows(predictions: DataFrame) -> DataFrame:
    return predictions.select(
        "transaction_id",
        "amount",
        "label",
        "prediction",
        vector_to_array("probability")[1].alias("fraud_probability"),
    )


def main() -> None:
    args = parse_args()
    spark = init_spark(
        "PySpark_BigQuery_RF_Lab", args.gcs_bucket, args.dataset, demo=args.demo
    )
    try:
        data = (
            synthetic_transactions(spark)
            if args.demo
            else load_data(
                spark, f"{args.project_id}.{args.dataset}.{args.input_table}"
            )
        )
        model, predictions = build_and_train_pipeline(data)
        if args.model_output:
            model.write().save(args.model_output)
        scored = scored_rows(predictions)
        if args.output_table:
            table = f"{args.project_id}.{args.dataset}.{args.output_table}"
            scored.write.format("bigquery").option("table", table).mode(
                "errorifexists"
            ).save()
        else:
            scored.show(5)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
