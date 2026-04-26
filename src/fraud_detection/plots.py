from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    auc,
    precision_recall_curve,
    roc_curve,
)

from fraud_detection.evaluate import positive_scores


def _save(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_class_distribution(df: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(6, 4))
    ax = sns.countplot(data=df, x="Class", hue="Class", palette=["#4C78A8", "#E45756"], legend=False)
    ax.set_title("Class Distribution")
    ax.set_xlabel("Class (0=Legitimate, 1=Fraud)")
    ax.set_ylabel("Transaction Count")
    _save(path)


def plot_confusion_matrix(model, x: pd.DataFrame, y: pd.Series, path: Path) -> None:
    plt.figure(figsize=(5, 4))
    ConfusionMatrixDisplay.from_estimator(model, x, y, labels=[0, 1], cmap="Blues", colorbar=False)
    plt.title("Random Forest Confusion Matrix")
    _save(path)


def plot_roc_curve(models: dict[str, object], x: pd.DataFrame, y: pd.Series, path: Path) -> None:
    plt.figure(figsize=(7, 5))
    ax = plt.gca()
    for name, model in models.items():
        fpr, tpr, _ = roc_curve(y, positive_scores(model, x))
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc(fpr, tpr):.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="#666666", label="Random")
    ax.set_title("ROC Curve Comparison")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend()
    _save(path)


def plot_pr_curve(models: dict[str, object], x: pd.DataFrame, y: pd.Series, path: Path) -> None:
    plt.figure(figsize=(7, 5))
    ax = plt.gca()
    for name, model in models.items():
        precision, recall, _ = precision_recall_curve(y, positive_scores(model, x))
        ax.plot(recall, precision, label=name)
    ax.set_title("Precision-Recall Curve Comparison")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend()
    _save(path)
