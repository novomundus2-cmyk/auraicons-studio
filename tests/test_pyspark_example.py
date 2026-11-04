"""Regresiones locales del ejemplo; nunca acceden a BigQuery ni GCS."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat, lit, when

MODULE_PATH = Path(__file__).resolve().parents[1] / "public/train_rf_bigquery.py"
spec = importlib.util.spec_from_file_location("rf_example", MODULE_PATH)
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class ArgumentSafetyTests(unittest.TestCase):
    def test_demo_rejects_remote_output(self):
        for args in (
            ["--demo", "--output_table", "scored"],
            ["--demo", "--model_output", "gs://bucket/model"],
            ["--demo", "--model_output", "gs:/bucket/model"],
            ["--demo", "--model_output", "hdfs:/models/demo"],
            ["--demo", "--model_output", "file://remote/models/demo"],
            ["--demo", "--model_output", "//remote/models/demo"],
            ["--demo", "--model_output", "file:relative-model"],
        ):
            with (
                self.subTest(args=args),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                example.parse_args(args)

    def test_no_cloud_read_without_project(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            example.parse_args([])

    def test_demo_has_no_default_writes(self):
        args = example.parse_args(["--demo"])
        self.assertIsNone(args.output_table)
        self.assertIsNone(args.model_output)
        for path in ("local-model", "file:/tmp/local-model", "/tmp/local-model"):
            with self.subTest(path=path):
                parsed = example.parse_args(["--demo", "--model_output", path])
                self.assertTrue(parsed.model_output.startswith("file:///"))

    def test_read_failure_propagates(self):
        spark = Mock()
        spark.read.format.return_value.option.return_value.load.side_effect = (
            RuntimeError("read denied")
        )
        with self.assertRaisesRegex(RuntimeError, "read denied"):
            example.load_data(spark, "project.dataset.table")


class LocalSparkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = (
            SparkSession.builder.master("local[2]")
            .appName("rf-example-regression")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )
        cls.spark.sparkContext.setLogLevel("ERROR")
        cls.data = (
            example.synthetic_transactions(cls.spark, 240)
            .withColumn(
                "is_fraud", when(col("transaction_id") % 3 == 0, 1).otherwise(0)
            )
            .withColumn("category", concat(lit("merchant-"), col("transaction_id")))
        )

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_missing_and_invalid_labels_fail(self):
        with self.assertRaisesRegex(ValueError, "Faltan columnas"):
            example.validate_training_data(self.data.drop("amount"))
        with self.assertRaisesRegex(ValueError, "solo admite"):
            example.validate_training_data(self.data.withColumn("is_fraud", lit(2)))
        with self.assertRaisesRegex(ValueError, "ambas clases"):
            example.class_counts(self.data.withColumn("label", lit(0.0)))

    def test_training_isolated_and_full_model_roundtrips(self):
        model, predictions = example.build_and_train_pipeline(
            self.data,
            num_trees=(3,),
            max_depths=(2,),
            num_folds=2,
        )
        rows = predictions.select("transaction_id", "category", "prediction").collect()
        self.assertGreater(len(rows), 0)
        learned_categories = set(model.stages[0].labels)
        self.assertTrue(all(row.category not in learned_categories for row in rows))
        self.assertEqual(len(model.stages), 9)
        probabilities = (
            example.scored_rows(predictions).select("fraud_probability").collect()
        )
        self.assertTrue(all(0 <= row.fraud_probability <= 1 for row in probabilities))
        with tempfile.TemporaryDirectory(prefix="rf-model-test-") as directory:
            path = str(Path(directory) / "model")
            model.write().save(path)
            restored = PipelineModel.load(path)
            actual = {
                row.transaction_id: row.prediction
                for row in restored.transform(self.data)
                .select("transaction_id", "prediction")
                .collect()
            }
            self.assertTrue(
                all(actual[row.transaction_id] == row.prediction for row in rows)
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
