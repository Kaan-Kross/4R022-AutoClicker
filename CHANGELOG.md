# 📜 Değişiklik Günlüğü / Changelog

Biçim [Keep a Changelog](https://keepachangelog.com/) esas alınmıştır. Sürüm numaralandırması: `MAJOR.MINOR.PATCH` (+ `b` = beta).

---

## [1.0V Beta] — 2026-10-19  ·  `v1.0.0b1`

> 🎉 **4R022 AutoClicker'ın ilk herkese açık beta sürümü.**

### ✨ Eklenenler

#### 🖱️ Tıklama motoru
- Sol / sağ / orta fare tuşu desteği.
- **Tek tıklama**, **çift tıklama** ve **otomatik seri tıklama** (seri başına tıklama sayısı ve seri içi bekleme ayarlanabilir).
- Tıklama aralığı **saat · dakika · saniye · milisaniye** olarak girilir; seçilen aralığın tık/sn karşılığı canlı gösterilir.
- Tıklama sayısı: **belirli sayı** veya **sınırsız**.
- **Kaymasız zamanlayıcı**: kaba bekleme + son milisaniyelerde hassas bekleme; duraklama veya takılma sonrası "yakalama patlaması" yapmaz.
- Başlat / Durdur / Duraklat-Devam düğmeleri ve kısayolları.
- **Duraklat ve devam et**: sayaçlar sıfırlanmaz, duraklama süresi geçen süreye sayılmaz.

#### 🎯 Hedefleme
- **Mevcut konum**, **sabit nokta (X/Y)** ve **çoklu hedef** modları.
- Hedef listesi: satır ekleme/silme, yukarı-aşağı taşıma, etiketleme, tümünü temizleme.
- **3 saniyelik geri sayımla** konum yakalama ve **"Hedef ekle" kısayolu** (varsayılan `F9`).
- Geçiş sırası: **sırayla**, **rastgele**, **ileri-geri (ping-pong)**.
- Konum sapması (jitter) ve aktif hedef göstergesi.

#### ⚙️ Gelişmiş ayarlar
- Başlangıç gecikmesi, basılı tutma süresi, **rastgele aralık (min–maks)**, döngü sayısı, azami çalışma süresi.
- Döngü tanımı: çoklu hedefte listede 1 tam tur; diğer modlarda 1 tıklama işlemi. Tıklama sayısı ve döngüden hangisi önce dolarsa işlem biter.

#### 🛑 KillSwitch ve güvenlik
- **Acil durdur** kısayolu (`Ctrl+Shift+F12`) ve büyük kırmızı arayüz düğmesi.
- **Köşe güvenliği**: imleç sol üst köşeye götürülünce işlem durur.
- **Otomatik kapatma**: kesintisiz çalışma süresi dolunca durdurur; isteğe bağlı olarak uygulamadan çıkar.
- **Watchdog**: tıklama iş parçacığı yanıt vermezse fare tuşlarını serbest bırakır.
- Üst üste 5 tıklama hatasında motor kendini durdurur; iş bitince/hatada basılı kalmış tuşlar her zaman bırakılır.
- Durdur ve KillSwitch, arayüzden bağımsız olarak kısayol iş parçacığında çalışır.
- **Tuş koruması**: arka plandayken Başlat / Duraklat / Hedef-ekle yalnızca çift basışla tetiklenir.

#### ⌨️ Kısayollar
- **Her tuş** ve Ctrl / Shift / Alt / Cmd kombinasyonları herhangi bir eyleme atanabilir ("bir tuşa basın" yakalama modu).
- Çakışma denetimi, varsayılana dönme, tuş tekrarı (auto-repeat) filtresi, kaçırılan tuş-bırakma olayına karşı kurtarma.

#### 📊 İstatistik ve performans
- Toplam tıklama, geçen süre, ortalama CPS, **anlık CPS**, tepe CPS, hata sayısı ve son 60 saniyelik canlı grafik.
- **Oturum geçmişi** (tarih, süre, tıklama, ort./tepe CPS, tür/mod, bitiş nedeni).
- **Uygulama giriş-çıkış takibi** ve oturum başlangıç/bitiş kayıtları.
- **TXT · JSON · CSV** dışa aktarma (CSV Excel uyumlu UTF-8 BOM ile); dışa aktarma klasörünü seçme ve uygulamadan açma.
- **Profesyonel görev takip günlüğü** (Bilgi/Uyarı/Hata filtresi, canlı dil değişimine uyumlu), **hata günlüğü**, **tanılama** ekranı (OS, motor, kısayol dinleyicisi, izin ipuçları, yollar).
- Çalışma durumunu gösteren **küçük, sürüklenebilir durum paneli**.

#### ⚡ CPS Testi
- **15 / 30 / 60 saniye** testleri; ilk tıklama testi başlatır; tıklama *basış anında* sayılır.
- Canlı sayaç, ilerleme çubuğu, saniye başına tıklama grafiği.
- Ayrıntılı sonuçlar: toplam, ortalama, tepe (en iyi 1 sn), skor, tutarlılık %, ortalama/en hızlı/en yavaş aralık, ilk-ikinci yarı CPS (yorulma), **seviye** (Çaylak → Efsane).
- Süre başına **kişisel rekor** takibi, test geçmişi ve dışa aktarma.

#### 🧩 Eklenti sistemi
- Olay tabanlı eklentiler: `start`, `stop`, `pause`, `resume`, `session`.
- Eklentiler varsayılan olarak **kapalı**; hatalı eklenti uygulamayı çökertmez.
- İki örnek eklenti: *Session Notes*, *Beep On Stop*.

#### 🎨 Arayüz, diller ve erişilebilirlik
- **4R022 logosu** kenar çubuğunda ve Hakkında bölümünde vurgulu; logodan türetilmiş uygulama ve tepsi simgeleri (`.ico`, `.icns`, `.png`).
- **Koyu tema** (siyah zemin, **bordo yazılar** — 4R022'ye özel) ve **Beyaz tema**; anında değişir.
- **Türkçe · English · Русский** — uygulamayı yeniden başlatmadan değişir (günlük kayıtları dahil).
- Yazı boyutu %80–160, tam klavye gezintisi (`Ctrl+1…7`), erişilebilir bileşen adları, görünür odak çerçeveleri.
- 7 sayfa: Ana Sayfa · Gelişmiş · CPS Testi · İstatistikler · Günlükler · Eklentiler · Ayarlar.

#### 🫥 Arka plan ve sistem tepsisi
- Pencere kapatılınca arka planda çalışmaya devam eder; tepsi simgesi sağ tık menüsü: **Pencere göster/gizle · Ana Sayfa · CPS · Ayarlar · Başlat/Durdur · KillSwitch · Çıkış**.
- Tepsiye küçültülmüş başlama, her zaman üstte kalma, çıkışta onay isteme seçenekleri.

#### 🖥️ Platform desteği
- **Windows** (`win32` motoru), **macOS** ve **Linux/X11** (`pynput`); `pyautogui` isteğe bağlı yedek.
- Otomatik motor seçimi ve yedek zinciri; hiçbir motor yoksa güvenli *boş* motor + tanılama açıklaması.

#### 🏗️ Mimari
- **Core** (GUI'siz) + **Worker** sistemi: `ClickWorker` (hassas tıklama iş parçacığı) ve `TaskPool` (genel amaçlı arka plan işleri).
- Arayüz, motoru tıklama başına sinyalle değil 10 Hz anlık görüntüyle okur → yüksek CPS'de yavaşlama yok.
- Atomik, bozulmaya dayanıklı ayar kaydı; bozuk `config.json` yedeklenip varsayılana dönülür.
- Bozuk JSONL satırları atlanır, kalan kayıtlar korunur.

#### 🤖 Build, test ve dosyalama
- **Otomatik build sistemi** (`Build/build.py`): ortam denetimi → testler → self-test → PyInstaller → **derlenmiş uygulamayı doğrulama** → paketleme → SHA-256 → rapor; renkli, animasyonlu konsol çıktısı ve `--ci` düz modu.
- **GitHub Actions**: `ci.yml` (3 işletim sisteminde test + GUI self-test + build dry-run + otomatik ekran görüntüsü) ve `build.yml` (etiketle 3 platform derleme + Release).
- `Build/screenshots.py` ile README ekran görüntülerinin otomatik üretimi.
- 38 birim testi + `--selftest` / `--selftest-gui` kendi kendine test modları; TR/EN/RU çeviri bütünlüğü testi.
- Profesyonel depo yapısı: `Main/` (kaynak), `Build/` (build sistemi), `docs/`, `.github/`, README (TR + EN), CHANGELOG, LICENSE (MIT).

### ⚠️ Bilinen sınırlamalar (Beta)
- Linux **Wayland** oturumlarında genel kısayollar ve sentetik tıklamalar kısıtlıdır; X11 önerilir.
- macOS'ta *Erişilebilirlik* ve *Girdi İzleme* izinleri verilmelidir.
- Yükseltilmiş (yönetici) pencerelere tıklamak için AutoClicker da yönetici çalıştırılmalıdır (Windows).
- Çok yüksek hız (0 ms aralık) işlemciyi yoğun kullanır; dikkatle kullanın.
- Windows/macOS imzalı değildir; ilk açılışta SmartScreen / Gatekeeper uyarısı görülebilir.

### 🔜 Planlananlar
- Kaydet-oynat (makro) modu · görüntü/renk tabanlı hedef bulma · profil sistemi · yeni diller.

[1.0V Beta]: ../../releases/tag/v1.0.0b1
