from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer

from fraud_detection.config import MODEL_PATH, SCALER_PATH
from fraud_detection.data import add_time_features


def prepare_event(event: dict, scaler) -> pd.DataFrame:
    frame = pd.DataFrame([event])
    if "event_type" in frame.columns:
        frame = frame.drop(columns=["event_type"])
    if "Class" in frame.columns:
        frame = frame.drop(columns=["Class"])
    frame = add_time_features(frame)
    frame["Amount_scaled"] = scaler.transform(frame[["Amount"]])
    return frame


def run_detector(
    bootstrap_servers: str,
    input_topic: str,
    output_topic: str,
    model_path: Path,
    scaler_path: Path,
) -> None:
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    consumer = KafkaConsumer(
        input_topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="fraud-detector",
    )
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    for message in consumer:
        event = message.value
        x = prepare_event(event, scaler)
        probability = float(model.predict_proba(x)[0, 1])
        prediction = int(probability >= 0.5)
        alert = {
            "transaction_time": event.get("Time"),
            "amount": event.get("Amount"),
            "fraud_probability": probability,
            "fraud_prediction": prediction,
            "actual_class": event.get("Class"),
        }
        producer.send(output_topic, alert)
        producer.flush()
        print(f"alert prediction={prediction} probability={probability:.4f} amount={alert['amount']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Consume Kafka transactions and publish fraud alerts.")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--input-topic", default="transactions")
    parser.add_argument("--output-topic", default="fraud-alerts")
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument("--scaler-path", type=Path, default=SCALER_PATH)
    args = parser.parse_args()
    run_detector(args.bootstrap_servers, args.input_topic, args.output_topic, args.model_path, args.scaler_path)


if __name__ == "__main__":
    main()
