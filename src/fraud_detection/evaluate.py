from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def positive_scores(model, x: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(x)[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(x)
        return (scores - scores.min()) / (scores.max() - scores.min() + 1e-12)
    return model.predict(x)


def evaluate_binary_model(name: str, model, x: pd.DataFrame, y: pd.Series) -> dict[str, float | str]:
    y_pred = model.predict(x)
    scores = positive_scores(model, x)
    tn, fp, fn, tp = confusion_matrix(y, y_pred, labels=[0, 1]).ravel()
    return {
        "model": name,
        "precision": precision_score(y, y_pred, zero_division=0),
        "recall": recall_score(y, y_pred, zero_division=0),
        "f1": f1_score(y, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y, scores) if len(set(y)) > 1 else 0.0,
        "pr_auc": average_precision_score(y, scores) if len(set(y)) > 1 else 0.0,
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    }
