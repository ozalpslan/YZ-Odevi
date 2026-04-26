# Dataset

Ana deney için Kaggle `Credit Card Fraud Detection` veri seti kullanılmalıdır:

https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Dosyayı şu konuma koyun:

```text
data/raw/creditcard.csv
```

Kaggle erişimi yoksa kodu ve grafikleri test etmek için küçük sentetik örnek veri üretilebilir:

```bash
python -m fraud_detection.generate_sample_data
```

Sentetik veri yalnızca teknik pipeline doğrulaması içindir. Akademik raporda ana veri seti olarak gerçek kredi kartı veri seti referans alınmalıdır.
