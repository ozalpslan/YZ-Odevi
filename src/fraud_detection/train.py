from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from fraud_detection.config import (
    DEFAULT_DATASET,
    FIGURES_DIR,
    METRICS_PATH,
    MODEL_PATH,
    MODELS_DIR,
    REPORTS_DIR,
    SAMPLE_DATASET,
    SCALER_PATH,
)
from fraud_detection.data import load_creditcard_csv, prepare_features, summarize_dataset
from fraud_detection.evaluate import evaluate_binary_model
from fraud_detection.plots import plot_class_distribution, plot_confusion_matrix, plot_pr_curve, plot_roc_curve
from fraud_detection.rules import RuleBasedFraudDetector


def train_pipeline(dataset_path: Path, sample_limit: int | None = None, write_artifacts: bool = True) -> pd.DataFrame:
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="sklearn")
    if write_artifacts:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_creditcard_csv(dataset_path)
    if sample_limit:
        fraud = df[df["Class"] == 1]
        legit = df[df["Class"] == 0].sample(
            n=max(sample_limit - len(fraud), 1),
            random_state=42,
            replace=len(df[df["Class"] == 0]) < max(sample_limit - len(fraud), 1),
        )
        df = pd.concat([legit, fraud]).sample(frac=1, random_state=42).reset_index(drop=True)

    summary = summarize_dataset(df)
    if write_artifacts:
        (REPORTS_DIR / "dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        plot_class_distribution(df, FIGURES_DIR / "class_distribution.png")

    prepared = prepare_features(df)

    models = {
        "Rule-Based Baseline": RuleBasedFraudDetector().fit(prepared.x_train, prepared.y_train),
        "Logistic Regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=500, random_state=42, solver="liblinear"),
        ).fit(prepared.x_train, prepared.y_train),
        "Random Forest": RandomForestClassifier(
            n_estimators=160,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=42,
        ).fit(prepared.x_train, prepared.y_train),
    }

    isolation = IsolationForest(contamination=max(float(prepared.y_train.mean()), 0.001), random_state=42, n_jobs=-1)
    isolation.fit(prepared.x_train)
    models["Isolation Forest"] = IsolationForestAdapter(isolation)

    rows = [evaluate_binary_model(name, model, prepared.x_test, prepared.y_test) for name, model in models.items()]
    metrics = pd.DataFrame(rows).sort_values(["pr_auc", "recall"], ascending=False)
    if not write_artifacts:
        return metrics

    metrics.to_csv(METRICS_PATH, index=False)

    best_model = models["Random Forest"]
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(prepared.scaler, SCALER_PATH)
    plot_confusion_matrix(best_model, prepared.x_test, prepared.y_test, FIGURES_DIR / "confusion_matrix_random_forest.png")
    plot_roc_curve(models, prepared.x_test, prepared.y_test, FIGURES_DIR / "roc_curve.png")
    plot_pr_curve(models, prepared.x_test, prepared.y_test, FIGURES_DIR / "precision_recall_curve.png")
    return metrics


class IsolationForestAdapter:
    def __init__(self, model: IsolationForest):
        self.model = model

    def predict(self, x: pd.DataFrame):
        return (self.model.predict(x) == -1).astype(int)

    def decision_function(self, x: pd.DataFrame):
        return -self.model.decision_function(x)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and evaluate fraud detection models.")
    parser.add_argument("--dataset", type=Path, default=None, help="Path to creditcard.csv.")
    parser.add_argument("--sample-limit", type=int, default=None, help="Optional row limit for quick local runs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = args.dataset or (DEFAULT_DATASET if DEFAULT_DATASET.exists() else SAMPLE_DATASET)
    metrics = train_pipeline(dataset, sample_limit=args.sample_limit)
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
