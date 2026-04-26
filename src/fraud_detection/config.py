from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

DEFAULT_DATASET = DATA_RAW_DIR / "creditcard.csv"
SAMPLE_DATASET = DATA_SAMPLE_DIR / "creditcard_sample.csv"
MODEL_PATH = MODELS_DIR / "fraud_random_forest.joblib"
SCALER_PATH = MODELS_DIR / "amount_scaler.joblib"
METRICS_PATH = REPORTS_DIR / "metrics.csv"
