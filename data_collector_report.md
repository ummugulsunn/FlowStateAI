# Data Collector v1 Teknik Raporu — Hafta 2

## 1. Mimari
- **pynput tabanlı listener’lar:** Klavye (press/release) ve fare (move/click/scroll) olaylarını düşük gecikmeli ve olay tabanlı (event-driven) biçimde yakalar. Bu sayede ana akış bloklanmadan sürekli veri toplanır.
- **Threading + Queue:** Olaylar anlık olarak bir `Queue`’ya yazılır; ayrı bir yazar thread’i (writer) bu kuyruğu boşaltıp JSON satırlarını diske ekler. Böylece I/O gecikmeleri listener’ları etkilemez, veri kaybı riski azalır.
- **Oturum yönetimi:** Otomatik olarak `sessions/YYYY-MM-DD/session_HHMMSS.json` dosyaları oluşturulur; her oturum izole edilir ve zaman damgalı tutulur.

## 2. Veri Yapısı
- **JSON satır formatı (newline-delimited JSON):**  
  `{"timestamp": 1709..., "event_type": "mouse_move", "data": {"x": 100, "y": 200, "velocity": 45.2}}`
- **Yakalanan metrikler:**
  - **Velocity (mouse_move):** Ardışık konumların öklid mesafesi / geçen süre (px/s).
  - **Flight Time (key_press):** Bir tuşun basılması ile bir önceki tuşun bırakılması arasındaki süre.
  - **Dwell Time (key_release):** Bir tuşa basılı kalma süresi (press → release).
  - **Click Interval (mouse_click):** Ardışık tıklamalar arası süre.
  - **Scroll delta (mouse_scroll):** `dx`, `dy` değerleri.

## 3. Zorluklar ve Çözümler
- **Yüksek frekanslı mouse hareketleri:** Sürekli hareket yoğun queue trafiği yaratır. Çözüm: Non-blocking enqueue ve ayrı yazar thread ile I/O’dan ayrıştırma; gerekirse hız eşiği veya örnekleme (throttling) uygulanır.
- **Zamanlama hataları (dt=0 veya negatif):** Velocity ve süre hesaplarında `dt <= 0` durumları güvenli biçimde `None` olarak atanır; olası anomali raporlarına konu edilir.
- **Kuyruk taşması riski:** `put_nowait` kullanıldığında dolu kuyrukta event düşebilir; üretim ortamında metrik ve backpressure izlemesi önerilir.

## 4. Sonuç
- Data Collector v1, klavye ve fare etkileşimlerini gerçek zamanlı yakalayıp JSON formatında kalıcı olarak kaydetmektedir.
- Temel metrikler (velocity, flight time, dwell time, click interval) üretilmekte ve oturum bazlı dosyalarda saklanmaktadır.
- Mimari, I/O blokajına karşı dayanıklı olup ileride eklenecek filtreleme, örnekleme ve model entegrasyonlarına hazır durumdadır.

