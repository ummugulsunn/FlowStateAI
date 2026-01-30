# Library Usage Guide — FlowStateAI

Bu belge, FlowStateAI'nin "Bilişsel Yük (Cognitive Load) Tahmini" çalışmasında neden `pynput`, `keyboard` ve `mouse` kütüphanelerini kullandığımızı teknik ama anlaşılır bir dille açıklar. Amaç, Elif ve Hiranur'un veri toplama yaklaşımını rahatça takip edebilmesidir.

## Neden bu kütüphaneler?
- **pynput**: Tek bir arayüzle hem klavye hem fare olaylarını yakalayabildiğimiz, olay tabanlı (event-driven) bir dinleyici sağlar. Asenkron dinleme sayesinde ana iş parçacığını bloklamadan veri toplayabiliriz.
- **keyboard** ve **mouse** (pynput alt modülleri): Donanım seviyesinde düşük gecikmeli olay yakalama sağlar; tuş basış zamanlarını (press/release) ve fare hareketlerini (move/click/scroll) yüksek zaman çözünürlüğüyle alabiliriz.

## Bilişsel Yük bağlamında hangi verileri topluyoruz?
- **Klavye dinamikleri**
  - **Dwell time**: Bir tuşa basılı tutma süresi. Stres veya yorgunluk arttığında ortalama dwell time uzayabilir veya tutarsızlaşabilir.
  - **Flight time**: Ardışık iki tuş arasındaki süre. Bilişsel yük yükseldiğinde tepki süreleri uzar; flight time dağılımındaki kayma bu etkiyi yansıtabilir.
  - **Ritim ve tutarlılık**: Tuşlama ritmindeki kırılmalar, dikkatin bölündüğünü veya zihinsel eforun arttığını gösterebilir.
- **Fare dinamikleri**
  - **Velocity (hız)**: İki konum arasındaki öklid mesafesi / geçen süre. Yorgunluk veya kararsızlık durumunda hızda dalgalanmalar ve ani yavaşlamalar/ivmelenmeler görülebilir.
  - **Acceleration / jerk paterni**: Hızdaki ani değişimler (ivme) motor kontrolün zorlandığı anları işaret edebilir.
  - **Click interval**: Ardışık tıklamalar arası süre. Dikkat dağınıklığında veya bilişsel yükte artışta tıklama ritmi değişebilir.
  - **Scroll rhythm**: Scroll periyotları ve adım büyüklükleri, bilgi arama stratejilerindeki değişimlere işaret edebilir.

## Kütüphanelerin rolü
- **Olay yakalama (event capture)**: `pynput.keyboard.Listener` ve `pynput.mouse.Listener` ile press/release/move/click/scroll olaylarını gerçek zamanlı alırız.
- **Zaman damgası (timestamping)**: Her olay anında yüksek çözünürlüklü `time.time()` damgası eklenir; dwell/flight/velocity gibi süre ve hız hesaplamaları için temel veri budur.
- **Ham veriyi özelliklere dönüştürme**:
  - Klavye: press_time, release_time → dwell time; ardışık tuş olayları → flight time.
  - Fare: ardışık konumlar → mesafe ve velocity; ardışık tıklamalar → click interval.
- **Non-blocking mimari**: Olaylar bir Queue'ya atılır, ayrı bir yazıcı thread JSON satırlarını diske ekler. Böylece olay kaçırmadan sürekli dinleme yapabiliriz.

## Cognitive Load tahmini için neden önemli?
- **Hız ve ritim duyarlılığı**: Bilişsel yük arttığında motor tepkiler yavaşlar veya düzensizleşir; dwell/flight ve velocity/acceleration bu değişimleri niceliksel olarak yakalar.
- **Pasif ve intrusif olmayan**: EEG veya eye-tracking gibi kurulumlar olmadan, sadece klavye/fare davranışından çıkarım yaparız; ölçeklenebilir ve düşük maliyetlidir.
- **Zaman serisi girdi**: Toplanan olaylar zaman serisi şeklinde modellere (RF, XGBoost, LSTM, Bi-LSTM, CNN-LSTM) beslenir. Özelliklerin zaman içindeki desenleri bilişsel durumu sınıflandırmada kilit rol oynar.

## Uygulama ipuçları
- Dinleyicileri başlatırken ana thread'i bloklamayın; ayrı thread'ler veya daemon listener kullanın.
- Kuyrukların dolma ihtimaline karşı (yüksek frekanslı hareketlerde) hataya toleranslı olun; önemli olayları kaybetmemek için makul kuyruk boyutu seçin veya backpressure stratejisi uygulayın.
- JSON satır formatını tutarlı tutun (`timestamp`, `event_type`, `data`) ki etiketleme ve model eğitim pipeline'ları kolayca entegre olsun.
- Zaman senkronizasyonu önemlidir: Saat kayması veya farklı kaynaklar arası offset varsa normalize edin.




