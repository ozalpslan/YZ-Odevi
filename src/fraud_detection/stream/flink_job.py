from __future__ import annotations

"""PyFlink job sketch for windowed fraud features.

This job is intentionally lightweight: it demonstrates where Flink sits in the
architecture. The Python model consumer remains the reproducible local inference
path because PyFlink setup is heavier on student machines.
"""

import argparse


def build_job(bootstrap_servers: str, input_topic: str, output_topic: str) -> str:
    return f"""
Flink stream job design:
  source: Kafka({bootstrap_servers}, topic={input_topic})
  parse: JSON transaction events
  window: tumbling 5-minute event-time windows
  features:
    - transaction_count
    - high_amount_count
    - total_amount
    - average_amount
  sink: Kafka(topic={output_topic})
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the planned Flink window-processing job.")
    parser.add_argument("--bootstrap-servers", default="kafka:29092")
    parser.add_argument("--input-topic", default="transactions")
    parser.add_argument("--output-topic", default="flink-window-features")
    args = parser.parse_args()
    print(build_job(args.bootstrap_servers, args.input_topic, args.output_topic))


if __name__ == "__main__":
    main()
