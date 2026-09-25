import json
import random
import time
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer
from sqlalchemy import create_engine, text

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "orders"

DATABASE_URL = (
    "postgresql+psycopg://"
    "ecommerce_user:ecommerce_password@localhost:5433/ecommerce"
)

EVENT_TYPES = ["product_view", "add_to_cart", "order_placed", "payment_confirmed"]


def load_real_ids():
    """Pull a sample of real customer_ids and product_ids from Postgres."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        customers = conn.execute(
            text("SELECT customer_id FROM customers ORDER BY random() LIMIT 2000")
        ).scalars().all()
        products = conn.execute(
            text("SELECT product_id FROM products ORDER BY random() LIMIT 2000")
        ).scalars().all()
    print(f"Loaded {len(customers)} real customer_ids and "
          f"{len(products)} real product_ids from Postgres")
    return customers, products


def make_event(customers, products):
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(EVENT_TYPES),
        "customer_id": random.choice(customers),
        "product_id": random.choice(products),
        "amount": round(random.uniform(10, 500), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery FAILED: {err}")
    else:
        print(f"Delivered to {msg.topic()} [partition {msg.partition()}]")


def main():
    customers, products = load_real_ids()
    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})

    print(f"Producing events to topic '{TOPIC}'. Press Ctrl+C to stop.")
    try:
        while True:
            event = make_event(customers, products)
            producer.produce(
                TOPIC,
                key=event["customer_id"],
                value=json.dumps(event),
                callback=delivery_report,
            )
            producer.poll(0)
            print("Sent:", event)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        producer.flush()


if __name__ == "__main__":
    main()