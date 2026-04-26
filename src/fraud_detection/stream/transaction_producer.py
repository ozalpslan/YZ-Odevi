from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
from kafka import KafkaProducer

from fraud_detection.config import SAMPLE_DATASET


def stream_transactions(
    dataset: Path,
    bootstrap_servers: str,
    topic: str,
    limit: int,
    delay_seconds: float,
) -> None:
    df = pd.read_csv(dataset).head(limit)
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    for _, row in df.iterrows():
        event = row.to_dict()
        event["event_type"] = "credit_card_transaction"
        producer.send(topic, event)
        print(f"sent transaction class={int(event.get('Class', -1))} amount={event.get('Amount'):.2f}")
        time.sleep(delay_seconds)

    producer.flush()
    producer.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish credit-card-like transactions to Kafka.")
    parser.add_argument("--dataset", type=Path, default=SAMPLE_DATASET)
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="transactions")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--delay-seconds", type=float, default=0.05)
    args = parser.parse_args()
    stream_transactions(args.dataset, args.bootstrap_servers, args.topic, args.limit, args.delay_seconds)


if __name__ == "__main__":
    main()
