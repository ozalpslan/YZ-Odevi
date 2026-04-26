from __future__ import annotations

import numpy as np
import pandas as pd


class RuleBasedFraudDetector:
    """Transparent baseline using amount and short-window transaction density."""

    def __init__(self, amount_quantile: float = 0.995, z_threshold: float = 3.0, score_threshold: int = 2):
        self.amount_quantile = amount_quantile
        self.z_threshold = z_threshold
        self.score_threshold = score_threshold
        self.high_amount_threshold_: float | None = None
        self.amount_mean_: float | None = None
        self.amount_std_: float | None = None

    def fit(self, x: pd.DataFrame, y: pd.Series | None = None) -> "RuleBasedFraudDetector":
        del y
        self.high_amount_threshold_ = float(x["Amount"].quantile(self.amount_quantile))
        self.amount_mean_ = float(x["Amount"].mean())
        self.amount_std_ = float(x["Amount"].std(ddof=0) or 1.0)
        return self

    def risk_score(self, x: pd.DataFrame) -> pd.Series:
        self._check_fitted()
        scores = pd.Series(0, index=x.index, dtype=int)
        amount_z = (x["Amount"] - self.amount_mean_) / self.amount_std_

        scores += (x["Amount"] >= self.high_amount_threshold_).astype(int)
        scores += (amount_z >= self.z_threshold).astype(int)

        if "hour_of_day" in x.columns:
            hourly_count = x.groupby("hour_of_day")["Amount"].transform("count")
            dense_hours = hourly_count >= np.percentile(hourly_count, 95)
            scores += dense_hours.astype(int)

        if "Amount_scaled" in x.columns:
            scores += (x["Amount_scaled"] > self.z_threshold).astype(int)

        return scores

    def predict(self, x: pd.DataFrame) -> np.ndarray:
        return (self.risk_score(x) >= self.score_threshold).astype(int).to_numpy()

    def predict_proba(self, x: pd.DataFrame) -> np.ndarray:
        score = self.risk_score(x).clip(0, 4) / 4.0
        return np.column_stack([1 - score, score])

    def _check_fitted(self) -> None:
        if self.high_amount_threshold_ is None or self.amount_mean_ is None or self.amount_std_ is None:
            raise RuntimeError("RuleBasedFraudDetector must be fitted before prediction.")
