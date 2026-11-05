"""Validate the producer's client configuration without a broker or database."""

import importlib.util
import json
import socket
import unittest
from pathlib import Path
from unittest.mock import patch

from kafka import KafkaProducer

PRODUCER_PATH = (
    Path(__file__).resolve().parents[1]
    / "CV/02_streaming_platform/producers/transaction_producer.py"
)


class KafkaProducerCompatibilityTests(unittest.TestCase):
    def test_configuration_and_serializers_with_real_client(self):
        spec = importlib.util.spec_from_file_location(
            "transaction_producer", PRODUCER_PATH
        )
        module = importlib.util.module_from_spec(spec)
        with patch.object(
            socket.socket, "connect", side_effect=AssertionError("No network")
        ):
            spec.loader.exec_module(module)
            with patch.object(module, "KafkaProducer") as factory:
                module.create_kafka_producer()
            options = factory.call_args.kwargs
            self.assertEqual(options["bootstrap_servers"], ["localhost:9092"])
            self.assertEqual(options["acks"], "all")
            self.assertEqual(options["retries"], 5)
            # An explicit protocol version avoids broker discovery. An empty
            # bootstrap list keeps the real client entirely local for this test.
            options["bootstrap_servers"] = []
            options["api_version"] = (2, 5, 0)
            producer = KafkaProducer(**options)
            try:
                transaction = module.generate_transaction(
                    [("user_test", "ES", "LOW")],
                    [("merchant_test", "Test merchant", "groceries")],
                )
                encoded = producer.config["value_serializer"](transaction)
                self.assertEqual(json.loads(encoded), transaction)
                self.assertEqual(
                    producer.config["key_serializer"](transaction["user_id"]),
                    b"user_test",
                )
            finally:
                producer.close(timeout=0)


if __name__ == "__main__":
    unittest.main()
