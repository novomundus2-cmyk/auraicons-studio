import json
import random
import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "financial_transactions"
CV_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = CV_ROOT / "04_database_lakehouse" / "financial_lakehouse.db"

DEVICES = ["iOS-18", "Android-15", "Web-Chrome", "Web-Safari"]


def load_dimensions_from_db():
    if not DB_PATH.exists():
        return (
            [("user_1001", "ES", "LOW")],
            [("merch_001", "Groceries Global Store #1", "groceries")],
        )
    conn = sqlite3.connect(DB_PATH)
    users = conn.execute("SELECT user_id, country, risk_tier FROM dim_users").fetchall()
    merchants = conn.execute("SELECT merchant_id, merchant_name, category FROM dim_merchants").fetchall()
    conn.close()
    print(
        f"📦 Base de datos conectada: {len(users)} usuarios y {len(merchants)} comercios desde {DB_PATH.name}"
    )
    return users, merchants


def create_kafka_producer():
    print(f"🔌 Conectando a Kafka (KRaft) en {KAFKA_BOOTSTRAP_SERVERS}...")
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
        acks="all",
        retries=5,
        max_in_flight_requests_per_connection=5,
    )
    print("✅ Conectado a Kafka exitosamente.")
    return producer


def generate_transaction(users, merchants):
    user_id, country, risk_tier = random.choice(users)
    merchant_id, merchant_name, category = random.choice(merchants)
    amount = round(random.uniform(8.0, 950.0), 2)

    if random.random() < 0.05:
        amount = round(random.uniform(3200.0, 12000.0), 2)

    return {
        "transaction_id": f"txn_{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "merchant_id": merchant_id,
        "merchant_name": merchant_name,
        "amount": amount,
        "currency": "EUR",
        "merchant_category": category,
        "device": random.choice(DEVICES),
        "country": country,
        "risk_tier": risk_tier,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def main():
    users, merchants = load_dimensions_from_db()
    producer = create_kafka_producer()
    count = 0
    print(f"🚀 Emitiendo eventos desde {DB_PATH.name} hacia '{TOPIC_NAME}'...\n")

    try:
        while True:
            txn = generate_transaction(users, merchants)
            producer.send(TOPIC_NAME, key=txn["user_id"], value=txn)
            count += 1

            if count % 10 == 0:
                print(
                    f"-> [{count}] {txn['transaction_id']} | {txn['user_id']} ({txn['country']}) "
                    f"| €{txn['amount']} | {txn['merchant_category']}"
                )

            time.sleep(random.uniform(0.1, 0.4))
    except KeyboardInterrupt:
        print("\n⏹ Deteniendo productor...")
    finally:
        producer.flush()
        producer.close()
        print(f"Total transacciones emitidas: {count}")


if __name__ == "__main__":
    main()
