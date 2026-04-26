from pathlib import Path

from fraud_detection.data import load_creditcard_csv, prepare_features
from fraud_detection.generate_sample_data import generate_sample


def test_sample_dataset_can_be_loaded_and_split(tmp_path: Path):
    dataset = generate_sample(tmp_path / "creditcard_sample.csv", rows=1000, fraud_rate=0.02)
    df = load_creditcard_csv(dataset)
    prepared = prepare_features(df)

    assert len(prepared.x_train) > len(prepared.x_test)
    assert "Amount_scaled" in prepared.x_train.columns
    assert prepared.y_train.mean() > 0
    assert prepared.y_test.mean() > 0
