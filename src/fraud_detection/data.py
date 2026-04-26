from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


TARGET_COLUMN = "Class"


@dataclass(frozen=True)
class PreparedData:
    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    scaler: StandardScaler


def load_creditcard_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}. Put Kaggle creditcard.csv there or run "
            "`python -m fraud_detection.generate_sample_data` for a small demo file."
        )

    df = pd.read_csv(path)
    required = {"Time", "Amount", TARGET_COLUMN}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    seconds_in_day = 24 * 60 * 60
    enriched["hour_of_day"] = ((enriched["Time"] % seconds_in_day) // 3600).astype(int)
    enriched["day_index"] = (enriched["Time"] // seconds_in_day).astype(int)
    return enriched


def prepare_features(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> PreparedData:
    df = add_time_features(df)
    x = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    scaler = StandardScaler()
    for frame in (x_train, x_test):
        if "Amount_scaled" in frame.columns:
            frame.drop(columns=["Amount_scaled"], inplace=True)

    x_train = x_train.copy()
    x_test = x_test.copy()
    x_train["Amount_scaled"] = scaler.fit_transform(x_train[["Amount"]])
    x_test["Amount_scaled"] = scaler.transform(x_test[["Amount"]])
    return PreparedData(x_train, x_test, y_train, y_test, scaler)


def summarize_dataset(df: pd.DataFrame) -> dict[str, float]:
    fraud_count = int(df[TARGET_COLUMN].sum())
    total = int(len(df))
    return {
        "total_transactions": total,
        "fraud_transactions": fraud_count,
        "legitimate_transactions": total - fraud_count,
        "fraud_rate": float(fraud_count / total) if total else np.nan,
        "missing_values": int(df.isna().sum().sum()),
    }
