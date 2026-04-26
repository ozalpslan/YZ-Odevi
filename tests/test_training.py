from pathlib import Path

from fraud_detection.generate_sample_data import generate_sample
from fraud_detection.train import train_pipeline


def test_training_pipeline_outputs_metrics(tmp_path: Path):
    dataset = generate_sample(tmp_path / "creditcard_sample.csv", rows=1200, fraud_rate=0.025)
    metrics = train_pipeline(dataset, write_artifacts=False)

    assert {"model", "precision", "recall", "f1", "roc_auc", "pr_auc"}.issubset(metrics.columns)
    assert len(metrics) >= 4
    assert "Random Forest" in set(metrics["model"])
