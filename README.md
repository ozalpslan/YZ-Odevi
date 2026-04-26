# Finansal Anomali Tespiti

Bu proje, Yapay Zeka dersi araştırma ödevindeki `Finansal Anomali Tespiti` konusunu uçtan uca karşılar. Ana hedef, kredi kartı sahtekarlık tespitinde kural tabanlı yaklaşımı makine öğrenmesi modelleriyle ölçülebilir şekilde karşılaştırmaktır. Kafka ve Flink gerçek zamanlı akış mimarisini göstermek için destekleyici katman olarak eklenmiştir.

## İçerik

```text
data/                 dataset açıklaması ve örnek veri alanı
src/                  eğitim, değerlendirme ve streaming kodları
models/               eğitilmiş model çıktıları
reports/              akademik rapor, metrikler ve grafikler
tests/                pipeline testleri
docker-compose.yml    Kafka + Flink altyapısı
```

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

## Veri Seti

Ana deney için Kaggle Credit Card Fraud Detection veri setini indirin:

https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

CSV dosyasını şu konuma koyun:

```text
data/raw/creditcard.csv
```

Kaggle API anahtarınız varsa doğrudan indirme:

```bash
mkdir -p /tmp/codex-kaggle
cp "/path/to/kaggle.json" /tmp/codex-kaggle/kaggle.json
chmod 600 /tmp/codex-kaggle/kaggle.json
KAGGLE_CONFIG_DIR=/tmp/codex-kaggle kaggle datasets download -d mlg-ulb/creditcardfraud -p data/raw --unzip
```

Kaggle erişimi yoksa teknik pipeline'ı doğrulamak için örnek veri üretin:

```bash
python -m fraud_detection.generate_sample_data
```

## Offline Deney

```bash
python -m fraud_detection.train
```

Bu komut şunları üretir:

```text
models/fraud_random_forest.joblib
models/amount_scaler.joblib
reports/metrics.csv
reports/dataset_summary.json
reports/figures/class_distribution.png
reports/figures/confusion_matrix_random_forest.png
reports/figures/roc_curve.png
reports/figures/precision_recall_curve.png
```

## Kafka + Flink Demo

Önce altyapıyı başlatın:

```bash
docker compose up -d
```

Model henüz yoksa gerçek Kaggle verisiyle eğitin. Kaggle verisine erişim yoksa yalnızca teknik demoyu doğrulamak için örnek veri üretilebilir:

```bash
python -m fraud_detection.generate_sample_data
python -m fraud_detection.train
```

Bir terminalde fraud detector consumer'ı başlatın:

```bash
python -m fraud_detection.stream.fraud_detector
```

Başka bir terminalde transaction producer'ı çalıştırın:

```bash
python -m fraud_detection.stream.transaction_producer --limit 100
```

Flink'in projedeki konumunu görmek için:

```bash
python -m fraud_detection.stream.flink_job
```

Flink arayüzü:

```text
http://localhost:8081
```

## Test

```bash
pytest
```

## Rapor

Akademik rapor:

```text
reports/final_report.md
```

Final teslim raporu IEEE düzeninde hazırlanmıştır. Rapor; giriş, literatür taraması, teorik çerçeve, metodoloji, senaryo/veri analizi, sonuç/tartışma ve IEEE kaynakçayı içerir.

IEEE LaTeX çıktısı:

```text
reports/final_report_ieee.pdf
reports/latex/final_report_ieee.tex
```
