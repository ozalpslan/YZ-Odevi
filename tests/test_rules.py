from pathlib import Path

from fraud_detection.data import load_creditcard_csv, prepare_features
from fraud_detection.generate_sample_data import generate_sample
from fraud_detection.rules import RuleBasedFraudDetector


def test_rule_based_detector_predicts_binary_labels(tmp_path: Path):
    dataset = generate_sample(tmp_path / "creditcard_sample.csv", rows=1000, fraud_rate=0.02)
    prepared = prepare_features(load_creditcard_csv(dataset))
    detector = RuleBasedFraudDetector().fit(prepared.x_train, prepared.y_train)

    predictions = detector.predict(prepared.x_test)
    probabilities = detector.predict_proba(prepared.x_test)

    assert set(predictions).issubset({0, 1})
    assert probabilities.shape == (len(prepared.x_test), 2)
