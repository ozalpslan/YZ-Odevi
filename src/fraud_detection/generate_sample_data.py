from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from fraud_detection.config import SAMPLE_DATASET


def generate_sample(path: Path = SAMPLE_DATASET, rows: int = 6000, fraud_rate: float = 0.012) -> Path:
    rng = np.random.default_rng(42)
    fraud_count = max(10, int(rows * fraud_rate))
    legit_count = rows - fraud_count

    time = np.sort(rng.integers(0, 172800, size=rows))
    amount_legit = rng.gamma(shape=2.0, scale=38.0, size=legit_count)
    amount_fraud = rng.gamma(shape=3.0, scale=140.0, size=fraud_count) + 220
    amount = np.concatenate([amount_legit, amount_fraud])

    features = {}
    for i in range(1, 29):
        legit_feature = rng.normal(0, 1, legit_count)
        fraud_shift = rng.normal(0.8 if i in {3, 7, 10, 14, 17} else 0.2, 1.25, fraud_count)
        features[f"V{i}"] = np.concatenate([legit_feature, fraud_shift])

    df = pd.DataFrame({"Time": time, **features, "Amount": amount, "Class": [0] * legit_count + [1] * fraud_count})
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a small creditcard-like sample dataset for local demos.")
    parser.add_argument("--rows", type=int, default=6000)
    parser.add_argument("--output", type=Path, default=SAMPLE_DATASET)
    args = parser.parse_args()
    output = generate_sample(args.output, rows=args.rows)
    print(f"Sample dataset written to {output}")


if __name__ == "__main__":
    main()
