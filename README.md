# FlowStateAI — Bilişsel Yük Tahmin Sistemi

Klavye ve fare etkileşimlerinden pasif davranışsal veri toplayarak bilişsel yükü tahmin eden bir Python uygulaması.

## Proje Amacı

FlowStateAI, kullanıcının bilgisayarla etkileşimini (tuş vuruşları, fare hareketleri) analiz ederek bilişsel yük seviyesini (Düşük / Orta / Yüksek) tahmin etmeyi hedefler. EEG veya göz takibi gibi invaziv yöntemler yerine, pasif algılama (passive sensing) yaklaşımı kullanılır.

## Gereksinimler

- Python 3.11+
- pynput kütüphanesi

## Kurulum

```bash
# 1. Virtual environment oluştur
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Bağımlılıkları yükle
pip install -r requirements.txt
```

## Hızlı Başlangıç

### Veri Toplama

```bash
# Ctrl+C ile durdurana kadar çalışır
python data_collector.py

# Belirli süre için çalıştır (örn: 60 saniye)
python data_collector.py --duration 60

# Farklı çıktı klasörü belirt
python data_collector.py --output-dir my_sessions
```

### Veri Analizi

```bash
# Toplanan verileri analiz et
python data_analysis.py sessions/2026-01-30/session_sample_mixed.json
```

---

## Modüller

### 1. `data_collector.py` — Veri Toplama Modülü

Klavye ve fare olaylarını gerçek zamanlı toplar, JSON formatında kaydeder.

#### Özellikler

- **Klavye olayları**: Tuş basma (key_press), tuş bırakma (key_release)
- **Fare olayları**: Hareket (mouse_move), tıklama (mouse_click), kaydırma (mouse_scroll)
- **Thread-safe yazım**: Queue + writer thread ile I/O blokajı önlenir
- **Otomatik oturum yönetimi**: `sessions/YYYY-MM-DD/session_HHMMSS.json`

#### Kullanım (Kod içinden)

```python
from data_collector import AdvancedDataCollector

collector = AdvancedDataCollector()
collector.start()

# ... veri toplama devam eder ...

collector.stop()
```

#### Veri Formatı

Her olay JSON satırı olarak kaydedilir (newline-delimited JSON):

```json
{
  "timestamp": 1738234567.123,
  "event_type": "key_press",
  "data": {
    "key": "a",
    "press_time": 1738234567.123,
    "flight_time": 0.056
  }
}
```

#### Toplanan Metrikler

| Metrik | Açıklama | Bilişsel Yük İlişkisi |
|--------|----------|----------------------|
| **Dwell Time** | Tuşa basılı kalma süresi | Stres/yorgunlukta uzar |
| **Flight Time** | Ardışık tuşlar arası süre | Bilişsel yükte artar |
| **Velocity** | Fare hızı (px/s) | Yorgunlukta dalgalanır |
| **Click Interval** | Tıklamalar arası süre | Dikkat dağınıklığında değişir |

---

### 2. `data_analysis.py` — Veri Analiz Modülü

Toplanan logların bütünlüğünü ve anomalilerini kontrol eder.

#### Kullanım

```bash
python data_analysis.py <log_dosyası>
```

#### Çıktı Örneği

```
=== FlowStateAI Log Analysis ===
Total lines: 64
Valid JSON: 64 | Invalid JSON: 0
Event counts -> key_press: 22, key_release: 22, mouse_move: 12, mouse_click: 6, mouse_scroll: 2
Anomalies:
- Timestamp order violations: 0
- Extreme velocity (> 50000 px/s): 0
- Negative dwell/flight times: 0
```

---

### 3. `flow_logger.py` — Logging Modülü

Merkezi logging sistemi. Hem konsola hem dosyaya yazar.

```python
from flow_logger import setup_logger

logger = setup_logger()
logger.info("FlowStateAI başlatıldı.")
```

---

## Dosya Yapısı

```
FlowStateAI/
├── data_collector.py      # Ana veri toplama modülü
├── data_analysis.py       # Veri kalitesi analiz aracı
├── flow_logger.py         # Logging konfigürasyonu
├── calculator.py          # Yardımcı aritmetik fonksiyonlar
├── user_reg.py            # Kullanıcı kayıt sistemi (in-memory)
├── requirements.txt       # Python bağımlılıkları
├── library_usage_guide.md # Kütüphane kullanım rehberi (TR)
├── data_collector_report.md # Teknik rapor (TR)
└── sessions/              # Toplanan veriler
    └── YYYY-MM-DD/
        └── session_HHMMSS.json
```

---

## Örnek Veriler

Proje içinde 3 adet örnek veri dosyası bulunmaktadır:

| Dosya | İçerik | Event Sayısı |
|-------|--------|--------------|
| `session_sample_keyboard.json` | Sadece klavye olayları | 22 |
| `session_sample_mouse.json` | Sadece fare olayları | 20 |
| `session_sample_mixed.json` | Karışık (klavye + fare) | 23 |

Örnek analiz:

```bash
python data_analysis.py sessions/2026-01-30/session_sample_mixed.json
```

---

## Teknik Mimari

### Veri Pipeline'ı

```
User Input (klavye + fare)
    ↓
pynput Listener'ları (event capture)
    ↓
Queue (thread-safe buffer)
    ↓
Writer Thread (JSON serialization)
    ↓
Session Dosyası (newline-delimited JSON)
    ↓
Feature Extraction (dwell, flight, velocity...)
    ↓
Model (RF, XGBoost, LSTM, Bi-LSTM, CNN-LSTM)
    ↓
Cognitive Load Prediction (Low/Medium/High)
```

### Neden Bu Yaklaşım?

- **Pasif algılama**: EEG/eye-tracking gibi kurulumlar gerektirmez
- **Non-blocking I/O**: Event listener'lar bloklanmaz
- **Ölçeklenebilir**: Düşük maliyetli, her bilgisayarda çalışır
- **Zaman serisi uyumlu**: ML modelleri için uygun format

---

## Sorun Giderme

### macOS Erişim İzni

macOS'ta Accessibility izni gereklidir:
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Terminal (veya IDE) uygulamasını listeye ekleyin

### Linux Gereksinimi

```bash
# X11 için gerekli olabilir
sudo apt-get install python3-xlib
```

---

## Gelecek Geliştirmeler

- [ ] Gerçek zamanlı model entegrasyonu
- [ ] NASA-TLX etiketleme arayüzü
- [ ] Flutter frontend bağlantısı
- [ ] REST API endpoint'leri

---

## Ekip

**Backend (Python)**
- Havin
- Ümmügülsün

**Frontend (Flutter)**
- Elif
- Hiranur

---

## Lisans

Bu proje eğitim amaçlıdır.
