<div align="center">

<a name="top"></a>

<img src="Main/autoclicker/assets/logo.png" width="280" alt="4R022 AutoClicker">

# 4R022 AutoClicker

**Professional AutoClick Application** · `1.5V Beta`

![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-9B1229?style=for-the-badge)
![macOS](https://img.shields.io/badge/macOS-12%2B-B3122B?style=for-the-badge)
![Linux](https://img.shields.io/badge/Linux-X11-7A0E20?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-444?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-444?style=for-the-badge)

### 🌍 [🇹🇷 Türkçe](#tr) · [🇬🇧 English](#en) · [🇷🇺 Русский](#ru)

</div>

---
---

<a name="tr"></a>

# 🇹🇷 TÜRKÇE

**4R022 AutoClicker**, masaüstü için geliştirilmiş, performans odaklı profesyonel bir otomatik tıklama uygulamasıdır. Kaymasız (drift-free) zamanlayıcı, çoklu hedef desteği, katmanlı güvenlik sistemi (KillSwitch), CPS testi, ayrıntılı istatistikler, eklenti sistemi ve 4R022'ye özel bordo/siyah arayüzü tek pakette sunar. Windows, macOS ve Linux üzerinde çalışır; arayüz dili ve tema **yeniden başlatma gerekmeden** değiştirilebilir.

## 📑 İçindekiler

[Hızlı Başlangıç](#tr-quick) · [Özellikler](#tr-features) · [Kısayollar](#tr-keys) · [Platformlar](#tr-platforms) · [Mimari](#tr-arch) · [Eklentiler](#tr-plugins) · [Veri Konumları](#tr-data) · [Build & CI](#tr-build) · [Testler](#tr-tests) · [Sorun Giderme](#tr-faq) · [Sorumlu Kullanım](#tr-legal)

<a name="tr-quick"></a>
## 🚀 Hızlı Başlangıç

**Hazır sürüm:** [Releases](https://github.com/Kaan-Kross/4R022-AutoClicker/releases) sayfasından platformunuza uygun paketi indirin, açın ve çalıştırın. Her sürümde doğrulama için `SHA256SUMS.txt` bulunur.

**Kaynaktan çalıştırma:**
```bash
git clone https://github.com/Kaan-Kross/4R022-AutoClicker.git
cd 4R022-AutoClicker
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python Main/main.py
```

**İlk tıklamanız (30 saniye):**
1. *Ana Sayfa*'da tıklama türünü ve aralığı seçin (varsayılan: sol tuş, 100 ms).
2. İmleci tıklanacak yere götürün.
3. `F6` ile başlatın, `F7` ile durdurun. Bir şeyler ters giderse `Ctrl+Shift+F12` (KillSwitch).

**Komut satırı seçenekleri**

| Seçenek | Açıklama |
|---|---|
| `--minimized` | Doğrudan sistem tepsisine küçültülmüş başlar |
| `--selftest` | Başsız (headless) kendi kendine test |
| `--selftest-gui` | Ek olarak tüm sayfaları 3 dil × 2 temada ekran dışı çizerek sınar |
| `--version` | Sürümü yazdırır |

<a name="tr-features"></a>
## ✨ Özellikler — Teker Teker

### 1️⃣ Tıklama Türü
**Sol, sağ ve orta** fare tuşları desteklenir. Seçim Ana Sayfa'daki *Tıklama* kartından yapılır ve her çalıştırmada o anki seçim kullanılır.

### 2️⃣ Tıklama Modları
- **Tek tıklama** — her turda bir tıklama.
- **Çift tıklama** — her turda 30 ms arayla iki tıklama.
- **Otomatik seri tıklama** — her turda *seri başına tıklama* kadar tıklama; seri içi bekleme (ms) *Gelişmiş* sayfasından ayarlanır.

### 3️⃣ Tıklama Aralığı
**Saat · dakika · saniye · milisaniye** alanlarıyla hassas aralık girilir. Seçilen aralığın *tık/sn* karşılığı anında gösterilir. Aralık `0` girilirse en yüksek olası hız kullanılır (işlemciyi yoğun kullanır — dikkatli olun).

### 4️⃣ Tıklama Sayısı
**Sınırsız** çalışabilir ya da **belirli bir sayıya** ulaşınca otomatik durur. Çift ve seri modlarda sayı, bireysel tıklamalar üzerinden tam olarak uygulanır (yarım seri bırakmaz, sınırı aşmaz).

### 5️⃣ Başlat / Durdur / Duraklat
Aksiyon çubuğundaki düğmelerden veya kısayollarla kontrol edilir. **Duraklat** sayaçları sıfırlamaz; duraklama süresi *geçen süre* ve *ortalama CPS* hesabına katılmaz. Devam edince zamanlayıcı yakalama patlaması yapmaz.

### 6️⃣ İmleç Konumu ve Çoklu Hedef
- **Mevcut konum** — imlecin olduğu yere tıklar.
- **Sabit nokta (X/Y)** — koordinatı elle girin veya **"Konum seç (3 sn)"** ile imleci istediğiniz yere götürüp yakalayın.
- **Birden fazla hedef** — hedef listesindeki noktalara sırayla tıklar. Liste *Gelişmiş* sayfasında düzenlenir: satır ekle/sil, **yukarı–aşağı taşı**, etiket ver, hücreleri çift tıklayarak düzenle, tümünü temizle.
- **Hedef ekle kısayolu** (`F9`) — her yerde imlecin bulunduğu noktayı listeye ekler.

### 7️⃣ Tıklama Dizisi
Çoklu hedefte geçiş sırası seçilir: **Sırayla**, **Rastgele** (her turda yeniden karıştırılır) veya **İleri-geri** (1-2-3-2-1…). Çalışırken *aktif hedef numarası* gösterilir.

### 8️⃣ Başlangıç Gecikmesi
Başlat'a bastıktan sonra tıklamalar başlamadan önce beklenecek süre (0,1 sn hassasiyetle, en çok 1 saat). Bekleme sırasında durumda *"Başlangıç gecikmesi"* görünür ve istediğiniz an iptal edebilirsiniz.

### 9️⃣ Rastgele Aralık ve Konum Sapması
- **Rastgele aralık** — her tıklama arası, belirlediğiniz *min–maks* ms arasında rastgele seçilir.
- **Konum sapması (jitter)** — hedef noktaya ± piksel kadar sapma ekler.

### 🔟 Basılı Tutma Süresi
Fare tuşunun kaç milisaniye basılı kalacağını belirler. Durdurma veya hata durumunda tuş **her zaman serbest bırakılır**.

### 1️⃣1️⃣ Döngü Sistemi ve Süre Sınırı
- **Döngü sayısı** — çoklu hedefte 1 döngü = hedef listesinde 1 tam tur; diğer modlarda 1 döngü = 1 tıklama işlemi (`0` = sınırsız).
- **Azami çalışma süresi** — süre dolunca otomatik durur.
- Tıklama sayısı, döngü ve süre sınırlarından hangisi önce dolarsa işlem biter; neden oturum geçmişine yazılır.

### 1️⃣2️⃣ Kısayol Tuşları
**Her tuş** — ve `Ctrl` / `Shift` / `Alt` / `Cmd` kombinasyonları — herhangi bir eyleme atanabilir. *Kısayol tuşları* kartında düğmeye tıklayıp istediğiniz tuşa basmanız yeterlidir. Çakışmalar otomatik reddedilir; tek tuşla varsayılana dönebilirsiniz.

### 1️⃣3️⃣ KillSwitch — Acil Durum ve Otomatik Kapatma
Birden çok bağımsız güvenlik katmanı:
- **Kısayol** (`Ctrl+Shift+F12`) ve büyük kırmızı **ACİL DURDUR** düğmesi.
- **Köşe güvenliği** — imleci ekranın sol üst köşesine götürmek işlemi durdurur.
- **Otomatik kapatma** — belirlediğiniz dakika kadar kesintisiz çalışınca durdurur.
- **"KillSwitch'te uygulamadan da çık"** seçeneği.
- **Watchdog** — tıklama iş parçacığı yanıt vermezse tüm fare tuşlarını serbest bırakır.
- **Hata eşiği** — üst üste 5 tıklama hatasında motor kendini durdurur.
- Durdur ve KillSwitch, arayüz meşgul olsa bile doğrudan kısayol iş parçacığında çalışır.

### 1️⃣4️⃣ Tuş Koruması
Açıkken, uygulama arka plandaysa **Başlat / Duraklat / Hedef ekle** kısayolları yanlışlıkla tetiklenmesin diye art arda **iki kez** basılmayı ister. **Durdur ve KillSwitch her zaman tek basışla** çalışır.

### 1️⃣5️⃣ İstatistik ve Performans
Canlı kutucuklar: **toplam tıklama, geçen süre, ortalama CPS, anlık CPS, tepe CPS, hata sayısı** ve son 60 saniyelik **canlı grafik**. Çalışma durumu *Ana Sayfa* üzerindeki özet kutucuklarda da görünür.

### 1️⃣6️⃣ Oturum Geçmişi ve Uygulama Giriş-Çıkış Takibi
Her çalıştırma tarih, süre, tıklama, ortalama/tepe CPS, tür/mod ve **bitiş nedeniyle** kaydedilir. Ayrı bir sekmede **uygulama giriş/çıkış**, oturum başlangıç/bitiş ve güncelleme olayları izlenir.

### 1️⃣7️⃣ Dışa Aktarma (TXT · JSON · CSV)
Oturum geçmişi veya etkinlik kaydı tek tıkla **TXT, JSON ya da CSV** (Excel uyumlu UTF-8) olarak dışa aktarılır. Dışa aktarma klasörünü Ayarlar'dan **butonla seçebilir**, istediğiniz an **klasörü açıp** dosyaları görebilirsiniz.

### 1️⃣8️⃣ Günlükler, Hata Günlüğü ve Tanılama
- **Görev takibi** — her olay (başlat, durdur, duraklat, KillSwitch, dışa aktarma, eklenti …) saat ve seviye ile listelenir; *Bilgi/Uyarı/Hata* filtresi, temizleme ve TXT dışa aktarma vardır. Kayıtlar **dil değişince de doğru dilde** görünür.
- **Hata günlüğü** — döner dosyalara yazılan hata kayıtları.
- **Tanılama** — işletim sistemi, Python, aktif motor, kısayol dinleyicisi durumu, izin ipuçları ve dosya yolları; panoya kopyalanabilir.

### 1️⃣9️⃣ CPS Testi
- **15 / 30 / 60 saniyelik** testler; **ilk tıklama testi başlatır**.
- Fare tuşlarından herhangi biri ya da `Boşluk`/`Enter` ile tıklanır; tıklama *basış anında* sayılır.
- Canlı sayaç, kalan süre, anlık CPS, ilerleme çubuğu ve **saniye başına tıklama grafiği**.
- Sonuç: toplam, ortalama CPS, **tepe CPS (en iyi 1 sn)**, skor, **tutarlılık %**, ortalama/en hızlı/en yavaş tıklama aralığı, ilk yarı–ikinci yarı CPS (yorulma analizi) ve **seviye** (Çaylak → Efsane).
- **Süre başına kişisel rekor**, test geçmişi ve TXT/JSON/CSV dışa aktarma.

### 2️⃣0️⃣ Eklenti Modül Desteği
Tek bir `.py` dosyasıyla olay tabanlı eklentiler yazılır (`start`, `stop`, `pause`, `resume`, `session`). Eklentiler **varsayılan olarak kapalıdır**, *Eklentiler* sayfasından açılıp kapatılır; hatalı eklenti uygulamayı çökertmez. İki örnek eklenti hazır gelir.

### 2️⃣1️⃣ Diller
**Türkçe · English · Русский** — Ayarlar'dan seçilir ve **uygulama yeniden başlatılmadan** anında değişir (günlük kayıtları dahil).

### 2️⃣2️⃣ Temalar
- **Koyu tema** — siyah zemin, **bordo yazılar** (4R022'ye özel); okunabilirlik için parlak bordo ton kullanılır.
- **Beyaz tema** — temiz beyaz zemin, bordo vurgular.
Tema anında değişir ve kaydedilir.

### 2️⃣3️⃣ Arayüz
Gradyanlı ve basınca çöken butonlar, tek bir **aksiyon çubuğu**, kompakt **marka başlığı**, vurgulu kart başlıkları, istatistik kutucukları, hap biçimli seçim düğmeleri, **tik işaretli onay kutuları**, noktalı seçenek düğmeleri ve 7 sayfa: *Ana Sayfa · Gelişmiş · CPS Testi · İstatistikler · Günlükler · Eklentiler · Ayarlar*.

### 2️⃣4️⃣ Arka Planda Çalışma ve Sistem Tepsisi
Pencereyi kapatınca uygulama **arka planda çalışmaya devam eder** (isteğe bağlı). Tepsi simgesine sağ tıklayınca: *Pencereyi göster/gizle · Ana Sayfa · CPS · Ayarlar · Başlat/Durdur · KillSwitch · Çıkış*. Ayrıca *tepsiye küçültülmüş başla*, *her zaman üstte*, *çıkışta onay iste* seçenekleri vardır.

### 2️⃣5️⃣ Küçük Durum Paneli
Çalışma durumunu gösteren, **sürüklenebilir, her zaman üstte** küçük panel: durum, tıklama sayısı, anlık CPS ve süre. Ayarlar'dan açılıp kapatılır.

### 2️⃣6️⃣ Erişilebilirlik
Tam klavye gezintisi (`Ctrl+1 … Ctrl+7` sayfalar, `Ctrl+Q` çıkış), görünür odak çerçeveleri, erişilebilir bileşen adları, **yazı boyutu %80–160**, yüksek kontrastlı bordo palet ve ana işlevlerin klavyeyle yönetilebildiği kısayol sistemi.

### 2️⃣7️⃣ Tıklama Motoru Seçimi ve Yedek Zinciri
Otomatik seçim: **Windows'ta `win32` → `pynput` → `pyautogui`**, diğer sistemlerde `pynput` → `pyautogui`. Ayarlar'dan elle de seçilebilir. Hiçbir motor yoksa uygulama çökmez; güvenli bir *boş* motora geçer ve Tanılama nedenini gösterir.

### 2️⃣8️⃣ Ayarlar, Bakım ve Güncelleme Altyapısı
Tüm ayarlar otomatik kaydedilir (atomik yazma, bozuk dosyaya dayanıklı). **Bakım** bölümünden ayarlar güvenle sıfırlanır (geçmiş silinmez). Ayar dosyası **sürüm göçü** içerir: eski sürümlerin ayarları kaybolmadan yükseltilir ve güncelleme günlüğe yazılır. Ayarlar'ın en altındaki **Uygulama Hakkında** bölümü özet, yenilikler ve sistem bilgisini (tek tıkla kopyalanabilir) gösterir.

<a name="tr-keys"></a>
## ⌨️ Varsayılan Kısayollar

| Eylem | Tuş | Not |
|---|---|---|
| Başlat | `F6` | Her tuşa atanabilir |
| Durdur | `F7` | Tuş korumasından etkilenmez |
| Duraklat / Devam | `F8` | |
| Hedef ekle | `F9` | İmleç konumunu listeye ekler |
| **KillSwitch** | `Ctrl+Shift+F12` | Her şeyi anında durdurur |
| Sayfalar | `Ctrl+1 … Ctrl+7` | Klavye ile geçiş |
| Çıkış | `Ctrl+Q` | |

<a name="tr-platforms"></a>
## 🖥️ Platform Desteği

| Platform | Motor | Notlar |
|---|---|---|
| **Windows 10/11** | `win32` → `pynput` | Yönetici olarak çalışan uygulamalara tıklamak için AutoClicker'ı da yönetici çalıştırın |
| **macOS 12+** | `pynput` | *Sistem Ayarları → Gizlilik ve Güvenlik* bölümünde **Erişilebilirlik** ve **Girdi İzleme** izni verin |
| **Linux (X11)** | `pynput` | Tam destek. **Wayland**'de genel kısayol/tıklama kısıtlıdır; X11 oturumu önerilir |

<a name="tr-arch"></a>
## 🏗️ Mimari: Core + Worker

```
Main/
├── main.py                      giriş noktası (--selftest, --version, --minimized)
├── autoclicker/
│   ├── core/                    GUI'den bağımsız çekirdek (tamamen test edilir)
│   │   ├── engine.py            ClickEngine: yaşam döngüsü, oturum kayıtları, olaylar
│   │   ├── workers.py           ClickWorker (hassas tıklama iş parçacığı) + TaskPool (genel amaçlı Worker havuzu)
│   │   ├── backend.py           Win32 → pynput → pyautogui yedek zinciri (+ Dummy test motoru)
│   │   ├── hotkeys.py           Genel kısayollar, kombinasyon eşleştirici, tuş koruması
│   │   ├── killswitch.py        Acil durdurma + watchdog + otomatik kapatma
│   │   ├── cps_test.py          CPS test mantığı ve istatistikleri
│   │   ├── session.py           Oturum / etkinlik / CPS depoları (JSONL)
│   │   ├── exporter.py          TXT · JSON · CSV dışa aktarma
│   │   ├── plugins.py           Eklenti yöneticisi
│   │   └── config.py            Ayar modeli, doğrulama, sürüm göçü
│   ├── i18n/                    tr.json · en.json · ru.json
│   ├── ui/                      PySide6 arayüzü (7 sayfa, tema, tepsi, mini panel)
│   └── plugins_examples/        Örnek eklentiler
├── tests/                       41 birim testi
Build/
├── build.py                     Otomatik, gösterişli build sistemi
└── 4R022-AutoClicker.spec       PyInstaller tanımı
```

- **Core** hiçbir GUI kütüphanesini içe aktarmaz; motor, kısayollar ve istatistikler başsız test edilir.
- **ClickWorker** tıklamaları kendi iş parçacığında yapar. Arayüz yalnızca 10 Hz'de bir anlık görüntü okur — tıklama başına sinyal yoktur; yüksek CPS'de arayüz yavaşlamaz.
- **TaskPool** dışa aktarma gibi gerçek zamanlı olmayan işleri arka planda yürütür.
- **Zamanlayıcı** kaymasızdır: kaba bekleme + son milisaniyelerde hassas bekleme; takılma sonrası "yakalama patlaması" yapmaz.

<a name="tr-plugins"></a>
## 🧩 Eklenti Yazma

`plugins` klasörüne tek bir `.py` dosyası bırakın (klasörü *Eklentiler* sayfasından açabilirsiniz):

```python
PLUGIN_INFO = {"name": "Merhaba", "version": "1.0", "author": "Ben", "description": "Her oturumu kaydeder"}

def register(api):
    def bitti(kayit):                       # kayit: total_clicks, avg_cps, stop_reason ...
        api.log(f"{kayit['total_clicks']} tıklama yapıldı")
    api.on("session", bitti)                # olaylar: start · stop · pause · resume · session
```

> ⚠️ Eklentiler tam Python yetkisiyle çalışır. Yalnızca güvendiğiniz kodu etkinleştirin.

<a name="tr-data"></a>
## 📁 Veri Konumları

| Platform | Yol |
|---|---|
| Windows | `%APPDATA%\4R022-AutoClicker` |
| macOS | `~/Library/Application Support/4R022-AutoClicker` |
| Linux | `~/.local/share/4R022-AutoClicker` |

İçerik: `config.json`, `sessions.jsonl`, `activity.jsonl`, `cps_results.json`, `logs/`, `plugins/`. Dışa aktarma klasörü varsayılan olarak `Documents/4R022-AutoClicker-Exports`'tur. Taşınabilir kullanım için `AUTOCLICKER_4R022_HOME` ortam değişkeni veri klasörünü yönlendirir.

<a name="tr-build"></a>
## 🤖 Otomatik Build Sistemi ve CI

```bash
python Build/build.py                # tam hat
python Build/build.py --dry-run      # PyInstaller hariç tüm denetimler
python Build/build.py --onedir       # tek dosya yerine klasör
```

**Hat:** ortam denetimi → birim testleri → kaynak self-test (GUI dahil) → varlık/dil doğrulaması → **PyInstaller** → **derlenmiş uygulamayı `--selftest-gui` ile doğrulama** → paketleme (`.zip` / `.tar.gz`) → SHA-256 → `BUILD_REPORT.md` + `build-info.json`. Herhangi bir adım başarısız olursa build **durur ve paket üretilmez**.

| İş akışı | Tetikleyici | Ne yapar |
|---|---|---|
| `ci.yml` | push / PR | 3 işletim sisteminde test + GUI self-test + build dry-run |
| `build.yml` | `v*` etiketi / elle | Windows + macOS + Linux paketlerini derler, doğrular ve **Release** yayınlar (`b` içeren etiketler *pre-release* olur) |

```bash
git tag v1.5.0b1 && git push origin v1.5.0b1
```

<a name="tr-tests"></a>
## 🧪 Testler
```bash
cd Main
python -m unittest discover -s tests -t . -v
```
Kapsam: motor (tıklama sayıları, çift/seri, döngü, çoklu hedef sırası, duraklat/devam, başlangıç gecikmesi, rastgele aralık, köşe güvenliği, azami süre, hata eşiği), kısayol eşleştirici (kombinasyonlar, tuş tekrarı, tuş koruması, yakalama), CPS istatistikleri, ayar doğrulama ve sürüm göçü, bozuk dosya, dışa aktarma, eklentiler, tema bütünlüğü ve **TR/EN/RU çeviri bütünlüğü**.

<a name="tr-faq"></a>
## 🛠️ Sorun Giderme

| Sorun | Çözüm |
|---|---|
| Kısayollar çalışmıyor | *Günlükler → Tanılama* sayfasında "Hotkey listener" durumuna bakın. macOS'ta izinleri, Linux'ta X11 oturumunu kontrol edin |
| Tıklamalar bazı pencerelerde işlemiyor | Hedef uygulama yönetici ise AutoClicker'ı da yönetici çalıştırın (Windows) |
| Linux'ta açılmıyor | `sudo apt install libxcb-cursor0 libegl1` |
| Her şey durmuyor gibi | `Ctrl+Shift+F12` veya imleci sol üst köşeye götürün |
| Ayarlar bozuldu | Uygulama bozuk dosyayı `config.json.bak` olarak saklayıp varsayılana döner |

<a name="tr-legal"></a>
## ⚖️ Sorumlu Kullanım

Bu yazılım **kendi bilgisayarınızda**, test, erişilebilirlik ve otomasyon amaçlı kullanım içindir. Kullandığınız yazılım ve hizmetlerin kullanım şartlarına uymak kullanıcının sorumluluğundadır. Lisans: [MIT](LICENSE).

[⬆️ Başa dön](#top)

---
---

<a name="en"></a>

# 🇬🇧 ENGLISH

**4R022 AutoClicker** is a performance-focused professional auto-clicker for the desktop. It bundles a drift-free scheduler, multi-target support, layered safety (KillSwitch), a CPS test, detailed statistics, a plugin system and the signature 4R022 bordeaux/black interface in a single package. It runs on Windows, macOS and Linux, and both language and theme switch **live, without a restart**.

## 📑 Contents

[Quick Start](#en-quick) · [Features](#en-features) · [Hotkeys](#en-keys) · [Platforms](#en-platforms) · [Architecture](#en-arch) · [Plugins](#en-plugins) · [Data Locations](#en-data) · [Build & CI](#en-build) · [Tests](#en-tests) · [Troubleshooting](#en-faq) · [Responsible Use](#en-legal)

<a name="en-quick"></a>
## 🚀 Quick Start

**Prebuilt:** download the package for your platform from [Releases](https://github.com/Kaan-Kross/4R022-AutoClicker/releases), extract and run. Every release ships a `SHA256SUMS.txt` for verification.

**From source:**
```bash
git clone https://github.com/Kaan-Kross/4R022-AutoClicker.git
cd 4R022-AutoClicker
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python Main/main.py
```

**Your first click (30 seconds):**
1. On *Home*, pick the click type and interval (default: left button, 100 ms).
2. Move the cursor where you want to click.
3. Press `F6` to start and `F7` to stop. If anything goes wrong: `Ctrl+Shift+F12` (KillSwitch).

**Command-line options**

| Option | Description |
|---|---|
| `--minimized` | Starts hidden in the system tray |
| `--selftest` | Headless self check |
| `--selftest-gui` | Also renders every page offscreen in 3 languages × 2 themes |
| `--version` | Prints the version |

<a name="en-features"></a>
## ✨ Features — One by One

### 1️⃣ Click Type
**Left, right and middle** mouse buttons. Chosen in the *Clicking* card on Home and applied to every run.

### 2️⃣ Click Modes
- **Single click** — one click per round.
- **Double click** — two clicks 30 ms apart per round.
- **Automatic burst** — *clicks per burst* clicks per round; the gap inside a burst (ms) is set on the *Advanced* page.

### 3️⃣ Click Interval
Enter a precise interval in **hours · minutes · seconds · milliseconds**. The equivalent *clicks/s* is shown instantly. An interval of `0` means maximum possible speed (CPU-intensive — use with care).

### 4️⃣ Click Count
Run **unlimited**, or stop automatically at a **fixed count**. In double and burst modes the limit is applied to individual clicks exactly — never a half-finished burst, never overshooting.

### 5️⃣ Start / Stop / Pause
Control from the action bar or by hotkey. **Pause** keeps your counters; paused time is excluded from *elapsed time* and *average CPS*. On resume the scheduler never "catches up" with a burst.

### 6️⃣ Cursor Position & Multi-Target
- **Current position** — clicks where the cursor is.
- **Fixed point (X/Y)** — type coordinates, or press **"Pick position (3 s)"**, move the cursor and let it capture.
- **Multiple targets** — clicks the listed points in turn. Edit the list on *Advanced*: add/delete rows, **move up/down**, label, double-click cells to edit, clear all.
- **Add-target hotkey** (`F9`) — adds the cursor's current point to the list from anywhere.

### 7️⃣ Click Sequence
Choose how targets are visited: **Sequential**, **Random** (reshuffled every pass) or **Ping-pong** (1-2-3-2-1…). The *active target number* is shown while running.

### 8️⃣ Start Delay
Time to wait after pressing Start before clicking begins (0.1 s precision, up to 1 hour). The state shows *"Start delay"* meanwhile and you can cancel at any moment.

### 9️⃣ Random Interval & Position Jitter
- **Random interval** — every gap is picked at random between your *min–max* ms.
- **Position jitter** — adds ± pixels of deviation to the target point.

### 🔟 Hold Duration
Sets how many milliseconds the button stays pressed. On stop or error the button is **always released**.

### 1️⃣1️⃣ Loops & Runtime Limit
- **Loops** — with multiple targets 1 loop = one full pass of the list; otherwise 1 loop = one click action (`0` = unlimited).
- **Max runtime** — stops automatically when time is up.
- Whichever of click count, loops and runtime is reached first ends the run; the reason is stored in the session history.

### 1️⃣2️⃣ Hotkeys
**Any key** — and `Ctrl` / `Shift` / `Alt` / `Cmd` combinations — can be bound to any action. In the *Hotkeys* card click a button and press the key you want. Conflicts are rejected automatically; one click restores the defaults.

### 1️⃣3️⃣ KillSwitch — Emergency Stop & Auto Shutdown
Several independent safety layers:
- **Hotkey** (`Ctrl+Shift+F12`) and a big red **KILL SWITCH** button.
- **Corner failsafe** — moving the cursor to the top-left corner of the screen stops clicking.
- **Auto shutdown** — stops after the number of minutes you set of continuous running.
- **"Also quit the app when KillSwitch triggers"** option.
- **Watchdog** — if the click thread stops responding, every mouse button is released.
- **Error threshold** — five consecutive click errors stop the engine.
- Stop and KillSwitch run directly on the hotkey thread, even if the UI is busy.

### 1️⃣4️⃣ Key Protection
When on and the app is in the background, the **Start / Pause / Add-target** hotkeys must be pressed **twice** quickly to prevent accidents. **Stop and KillSwitch always work with a single press.**

### 1️⃣5️⃣ Statistics & Performance
Live tiles: **total clicks, elapsed time, average CPS, live CPS, peak CPS, error count** and a **live chart** of the last 60 seconds. Run status also appears in the summary tiles on *Home*.

### 1️⃣6️⃣ Session History & App Sign-in/Sign-out Tracking
Every run is stored with date, duration, clicks, average/peak CPS, type/mode and **stop reason**. A separate tab tracks **application sign-in/sign-out**, session start/end and update events.

### 1️⃣7️⃣ Export (TXT · JSON · CSV)
Session history or the activity log exports with one click to **TXT, JSON or CSV** (Excel-friendly UTF-8). **Choose the export folder with a button** in Settings and **open it** any time to see the files.

### 1️⃣8️⃣ Logs, Error Log & Diagnostics
- **Task tracking** — every event (start, stop, pause, KillSwitch, export, plugin …) is listed with time and level; *Info/Warning/Error* filter, clear and TXT export. Entries show in the **correct language even after switching language**.
- **Error log** — error records written to rotating files.
- **Diagnostics** — OS, Python, active backend, hotkey listener state, permission hints and paths; copyable to the clipboard.

### 1️⃣9️⃣ CPS Test
- **15 / 30 / 60-second** tests; the **first click starts the test**.
- Click with any mouse button or `Space`/`Enter`; clicks count on *press*.
- Live counter, time left, live CPS, progress bar and a **clicks-per-second chart**.
- Results: total, average CPS, **peak CPS (best 1 s)**, score, **consistency %**, average/fastest/slowest gap, first-half vs second-half CPS (fatigue analysis) and a **rank** (Rookie → Legend).
- **Personal best per duration**, test history and TXT/JSON/CSV export.

### 2️⃣0️⃣ Plugin Module Support
Write event-based plugins in a single `.py` file (`start`, `stop`, `pause`, `resume`, `session`). Plugins are **disabled by default**, toggled on the *Plugins* page; a faulty plugin never crashes the app. Two example plugins are included.

### 2️⃣1️⃣ Languages
**Türkçe · English · Русский** — chosen in Settings and switched instantly **without restarting** (log entries included).

### 2️⃣2️⃣ Themes
- **Dark theme** — black background with **bordeaux text** (signature 4R022); a bright bordeaux tone keeps it readable.
- **Light theme** — clean white background with bordeaux accents.
The theme switches instantly and is remembered.

### 2️⃣3️⃣ Interface
Gradient, press-down buttons, a single **action bar**, a compact **brand header**, accented card titles, statistic tiles, pill-shaped selectors, **tick-mark checkboxes**, dotted radio buttons and 7 pages: *Home · Advanced · CPS Test · Statistics · Logs · Plugins · Settings*.

### 2️⃣4️⃣ Background Mode & System Tray
Closing the window can **keep the app running in the background** (optional). Right-click the tray icon for: *Show/hide window · Home · CPS · Settings · Start/Stop · KillSwitch · Quit*. Also available: *start minimized to tray*, *always on top*, *ask before quitting*.

### 2️⃣5️⃣ Small Status Panel
A small **draggable, always-on-top** panel showing state, click count, live CPS and time. Toggle it in Settings.

### 2️⃣6️⃣ Accessibility
Full keyboard navigation (`Ctrl+1 … Ctrl+7` pages, `Ctrl+Q` quit), visible focus rings, accessible widget names, **text size 80–160 %**, a high-contrast bordeaux palette and a hotkey system that lets you drive the main functions from the keyboard.

### 2️⃣7️⃣ Click Backend Selection & Fallback Chain
Automatic choice: **`win32` → `pynput` → `pyautogui` on Windows**, `pynput` → `pyautogui` elsewhere. Can be chosen manually in Settings. If no backend exists the app does not crash — it falls back to a safe *no-op* backend and Diagnostics explains why.

### 2️⃣8️⃣ Settings, Maintenance & Update Infrastructure
All settings save automatically (atomic writes, corruption-tolerant). The **Maintenance** section resets settings safely (history is kept). The settings file has **schema migration**: settings from older versions upgrade without losing anything and the update is logged. The **About** section at the very bottom of Settings shows a summary, what's new and system info (one-click copy).

<a name="en-keys"></a>
## ⌨️ Default Hotkeys

| Action | Key | Note |
|---|---|---|
| Start | `F6` | Bindable to any key |
| Stop | `F7` | Not affected by key protection |
| Pause / Resume | `F8` | |
| Add target | `F9` | Adds the cursor position to the list |
| **KillSwitch** | `Ctrl+Shift+F12` | Stops everything instantly |
| Pages | `Ctrl+1 … Ctrl+7` | Keyboard navigation |
| Quit | `Ctrl+Q` | |

<a name="en-platforms"></a>
## 🖥️ Platform Support

| Platform | Backend | Notes |
|---|---|---|
| **Windows 10/11** | `win32` → `pynput` | Run AutoClicker as administrator to click into elevated apps |
| **macOS 12+** | `pynput` | Grant **Accessibility** and **Input Monitoring** in *System Settings → Privacy & Security* |
| **Linux (X11)** | `pynput` | Full support. **Wayland** limits global hotkeys/clicks — use an X11 session |

<a name="en-arch"></a>
## 🏗️ Architecture: Core + Worker

```
Main/
├── main.py                      entry point (--selftest, --version, --minimized)
├── autoclicker/
│   ├── core/                    GUI-free core (fully tested)
│   │   ├── engine.py            ClickEngine: lifecycle, session records, events
│   │   ├── workers.py           ClickWorker (precise click thread) + TaskPool (general-purpose Worker pool)
│   │   ├── backend.py           Win32 → pynput → pyautogui fallback chain (+ Dummy test backend)
│   │   ├── hotkeys.py           Global hotkeys, combo matcher, key protection
│   │   ├── killswitch.py        Emergency stop + watchdog + auto shutdown
│   │   ├── cps_test.py          CPS test logic and statistics
│   │   ├── session.py           Session / activity / CPS stores (JSONL)
│   │   ├── exporter.py          TXT · JSON · CSV export
│   │   ├── plugins.py           Plugin manager
│   │   └── config.py            Settings model, validation, schema migration
│   ├── i18n/                    tr.json · en.json · ru.json
│   ├── ui/                      PySide6 interface (7 pages, theme, tray, mini panel)
│   └── plugins_examples/        Example plugins
├── tests/                       41 unit tests
Build/
├── build.py                     Automatic, showy build system
└── 4R022-AutoClicker.spec       PyInstaller definition
```

- **Core** imports no GUI library; engine, hotkeys and statistics are tested headless.
- **ClickWorker** clicks on its own thread. The UI only reads a snapshot at 10 Hz — no per-click signals, so the interface never slows down at high CPS.
- **TaskPool** runs non-realtime jobs such as exports in the background.
- **The scheduler** is drift-free: coarse wait + precise wait for the last milliseconds; it never "catches up" with a burst after a stall.

<a name="en-plugins"></a>
## 🧩 Writing Plugins

Drop a single `.py` file into the `plugins` folder (open it from the *Plugins* page):

```python
PLUGIN_INFO = {"name": "Hello", "version": "1.0", "author": "Me", "description": "Logs every session"}

def register(api):
    def done(record):                       # record: total_clicks, avg_cps, stop_reason ...
        api.log(f"{record['total_clicks']} clicks done")
    api.on("session", done)                 # events: start · stop · pause · resume · session
```

> ⚠️ Plugins run with full Python privileges. Only enable code you trust.

<a name="en-data"></a>
## 📁 Data Locations

| Platform | Path |
|---|---|
| Windows | `%APPDATA%\4R022-AutoClicker` |
| macOS | `~/Library/Application Support/4R022-AutoClicker` |
| Linux | `~/.local/share/4R022-AutoClicker` |

Contents: `config.json`, `sessions.jsonl`, `activity.jsonl`, `cps_results.json`, `logs/`, `plugins/`. The export folder defaults to `Documents/4R022-AutoClicker-Exports`. For portable use, the `AUTOCLICKER_4R022_HOME` environment variable redirects the data folder.

<a name="en-build"></a>
## 🤖 Automatic Build System & CI

```bash
python Build/build.py                # full pipeline
python Build/build.py --dry-run      # every check except PyInstaller
python Build/build.py --onedir       # folder build instead of a single file
```

**Pipeline:** environment check → unit tests → source self-test (GUI included) → asset/language validation → **PyInstaller** → **verify the built app with `--selftest-gui`** → package (`.zip` / `.tar.gz`) → SHA-256 → `BUILD_REPORT.md` + `build-info.json`. If any step fails the build **stops and no package is produced**.

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | push / PR | Tests + GUI self-test + build dry run on 3 operating systems |
| `build.yml` | `v*` tag / manual | Builds, verifies and publishes Windows + macOS + Linux packages as a **Release** (tags containing `b` become *pre-releases*) |

```bash
git tag v1.5.0b1 && git push origin v1.5.0b1
```

<a name="en-tests"></a>
## 🧪 Tests
```bash
cd Main
python -m unittest discover -s tests -t . -v
```
Coverage: engine (click counts, double/burst, loops, multi-target order, pause/resume, start delay, random interval, corner failsafe, max runtime, error threshold), hotkey matcher (combos, key repeat, key protection, capture), CPS statistics, settings validation and schema migration, corrupt files, export, plugins, theme integrity and **TR/EN/RU translation integrity**.

<a name="en-faq"></a>
## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| Hotkeys don't work | Check "Hotkey listener" under *Logs → Diagnostics*. On macOS check permissions, on Linux use an X11 session |
| Clicks don't register in some windows | If the target app runs as administrator, run AutoClicker as administrator too (Windows) |
| Won't start on Linux | `sudo apt install libxcb-cursor0 libegl1` |
| Can't seem to stop it | Press `Ctrl+Shift+F12` or move the cursor to the top-left corner |
| Settings got corrupted | The app keeps the broken file as `config.json.bak` and falls back to defaults |

<a name="en-legal"></a>
## ⚖️ Responsible Use

This software is for testing, accessibility and automation **on your own computer**. You are responsible for complying with the terms of service of any software or service you use it with. License: [MIT](LICENSE).

[⬆️ Back to top](#top)

---
---

<a name="ru"></a>

# 🇷🇺 РУССКИЙ

**4R022 AutoClicker** — профессиональный автокликер для ПК, ориентированный на производительность. В одном пакете: точный планировщик без дрейфа, несколько целей, многоуровневая защита (KillSwitch), CPS-тест, подробная статистика, система плагинов и фирменный бордово-чёрный интерфейс 4R022. Работает в Windows, macOS и Linux; язык и тема переключаются **на лету, без перезапуска**.

## 📑 Содержание

[Быстрый старт](#ru-quick) · [Возможности](#ru-features) · [Горячие клавиши](#ru-keys) · [Платформы](#ru-platforms) · [Архитектура](#ru-arch) · [Плагины](#ru-plugins) · [Данные](#ru-data) · [Сборка и CI](#ru-build) · [Тесты](#ru-tests) · [Решение проблем](#ru-faq) · [Ответственное использование](#ru-legal)

<a name="ru-quick"></a>
## 🚀 Быстрый старт

**Готовая сборка:** скачайте пакет для своей платформы на странице [Releases](https://github.com/Kaan-Kross/4R022-AutoClicker/releases), распакуйте и запустите. В каждом релизе есть `SHA256SUMS.txt` для проверки.

**Из исходников:**
```bash
git clone https://github.com/Kaan-Kross/4R022-AutoClicker.git
cd 4R022-AutoClicker
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python Main/main.py
```

**Ваш первый клик (30 секунд):**
1. На странице *Главная* выберите тип клика и интервал (по умолчанию: левая кнопка, 100 мс).
2. Наведите курсор туда, где нужно кликать.
3. `F6` — старт, `F7` — стоп. Если что-то пошло не так: `Ctrl+Shift+F12` (KillSwitch).

**Параметры командной строки**

| Параметр | Описание |
|---|---|
| `--minimized` | Запуск, свёрнутым в системный трей |
| `--selftest` | Самопроверка без интерфейса |
| `--selftest-gui` | Дополнительно отрисовывает все страницы вне экрана: 3 языка × 2 темы |
| `--version` | Выводит версию |

<a name="ru-features"></a>
## ✨ Возможности — по одной

### 1️⃣ Тип клика
Поддерживаются **левая, правая и средняя** кнопки мыши. Выбираются в карточке *Клик* на главной странице и применяются при каждом запуске.

### 2️⃣ Режимы клика
- **Одиночный клик** — один клик за раунд.
- **Двойной клик** — два клика с интервалом 30 мс за раунд.
- **Автосерия** — за раунд выполняется заданное число кликов; пауза внутри серии (мс) настраивается на странице *Дополнительно*.

### 3️⃣ Интервал кликов
Точный интервал задаётся в **часах · минутах · секундах · миллисекундах**. Эквивалент в *кликах/с* показывается сразу. Интервал `0` означает максимально возможную скорость (сильно нагружает процессор — осторожно).

### 4️⃣ Количество кликов
Работа **без ограничений** или автоматическая остановка по **заданному числу**. В двойном и серийном режимах лимит применяется к отдельным кликам точно — без недоделанных серий и без превышения.

### 5️⃣ Старт / Стоп / Пауза
Управление кнопками на панели действий или горячими клавишами. **Пауза** не сбрасывает счётчики; время паузы не входит в *прошедшее время* и *средний CPS*. После продолжения планировщик не «догоняет» пропущенное серией кликов.

### 6️⃣ Позиция курсора и несколько целей
- **Текущая позиция** — клик там, где стоит курсор.
- **Фиксированная точка (X/Y)** — введите координаты или нажмите **«Выбрать точку (3 с)»**, наведите курсор и дождитесь захвата.
- **Несколько целей** — клики по точкам списка по очереди. Список редактируется на странице *Дополнительно*: добавление/удаление строк, **перемещение вверх/вниз**, метки, правка ячеек двойным щелчком, очистка.
- **Горячая клавиша «Добавить цель»** (`F9`) — добавляет текущую позицию курсора в список из любого места.

### 7️⃣ Последовательность кликов
Порядок обхода целей: **По порядку**, **Случайно** (перемешивается на каждом проходе) или **Туда-обратно** (1-2-3-2-1…). Во время работы показывается *номер активной цели*.

### 8️⃣ Задержка старта
Время ожидания после нажатия «Старт» до первого клика (точность 0,1 с, максимум 1 час). Всё это время статус показывает *«Задержка старта»*, отменить можно в любой момент.

### 9️⃣ Случайный интервал и разброс позиции
- **Случайный интервал** — каждая пауза выбирается случайно между заданными *мин–макс* мс.
- **Разброс позиции (jitter)** — добавляет отклонение ± пикселей от целевой точки.

### 🔟 Время удержания
Задаёт, сколько миллисекунд кнопка остаётся нажатой. При остановке или ошибке кнопка **всегда отпускается**.

### 1️⃣1️⃣ Циклы и ограничение времени
- **Число циклов** — при нескольких целях 1 цикл = один полный проход по списку; иначе 1 цикл = одно действие клика (`0` = без ограничений).
- **Максимальное время работы** — автоматическая остановка по истечении времени.
- Работа заканчивается по достижении первого из лимитов (число кликов, циклы, время); причина сохраняется в истории сессий.

### 1️⃣2️⃣ Горячие клавиши
**Любую клавишу** — и сочетания `Ctrl` / `Shift` / `Alt` / `Cmd` — можно назначить на любое действие. В карточке *Горячие клавиши* нажмите кнопку и затем нужную клавишу. Конфликты отклоняются автоматически; одним нажатием можно вернуть значения по умолчанию.

### 1️⃣3️⃣ KillSwitch — аварийная остановка и автоотключение
Несколько независимых уровней защиты:
- **Горячая клавиша** (`Ctrl+Shift+F12`) и большая красная кнопка **АВАРИЙНЫЙ СТОП**.
- **Защита углом** — курсор в левом верхнем углу экрана останавливает клики.
- **Автоотключение** — остановка после заданного числа минут непрерывной работы.
- Опция **«Выходить из приложения при срабатывании KillSwitch»**.
- **Watchdog** — если поток кликов не отвечает, все кнопки мыши отпускаются.
- **Порог ошибок** — пять ошибок клика подряд останавливают движок.
- «Стоп» и KillSwitch выполняются прямо в потоке горячих клавиш, даже если интерфейс занят.

### 1️⃣4️⃣ Защита клавиш
Если включено и приложение работает в фоне, горячие клавиши **Старт / Пауза / Добавить цель** нужно нажать **дважды** подряд — это защищает от случайных срабатываний. **«Стоп» и KillSwitch всегда работают с одного нажатия.**

### 1️⃣5️⃣ Статистика и производительность
Живые плитки: **всего кликов, прошедшее время, средний CPS, текущий CPS, пиковый CPS, число ошибок** и **живой график** за последние 60 секунд. Состояние работы видно и в плитках на *Главной*.

### 1️⃣6️⃣ История сессий и учёт входа/выхода из приложения
Каждый запуск сохраняется с датой, длительностью, числом кликов, средним/пиковым CPS, типом/режимом и **причиной остановки**. Отдельная вкладка отслеживает **вход/выход из приложения**, начало/конец сессий и события обновления.

### 1️⃣7️⃣ Экспорт (TXT · JSON · CSV)
История сессий или журнал активности экспортируется одним нажатием в **TXT, JSON или CSV** (UTF-8, совместим с Excel). **Папку экспорта можно выбрать кнопкой** в настройках и в любой момент **открыть**, чтобы увидеть файлы.

### 1️⃣8️⃣ Журналы, журнал ошибок и диагностика
- **Отслеживание задач** — каждое событие (старт, стоп, пауза, KillSwitch, экспорт, плагин …) в списке со временем и уровнем; фильтр *Инфо/Предупреждения/Ошибки*, очистка и экспорт в TXT. Записи отображаются **на нужном языке даже после смены языка**.
- **Журнал ошибок** — записи об ошибках в ротируемых файлах.
- **Диагностика** — ОС, Python, активный движок, состояние слушателя горячих клавиш, подсказки по разрешениям и пути; копируется в буфер обмена.

### 1️⃣9️⃣ CPS-тест
- Тесты на **15 / 30 / 60 секунд**; **первый клик запускает тест**.
- Кликать можно любой кнопкой мыши, а также `Пробелом`/`Enter`; клик засчитывается в момент *нажатия*.
- Живой счётчик, оставшееся время, текущий CPS, индикатор прогресса и **график кликов по секундам**.
- Результаты: всего, средний CPS, **пиковый CPS (лучшая 1 с)**, очки, **стабильность %**, средний/быстрейший/медленнейший интервал, CPS первой и второй половины (анализ усталости) и **ранг** (Новичок → Легенда).
- **Личный рекорд для каждой длительности**, история тестов и экспорт в TXT/JSON/CSV.

### 2️⃣0️⃣ Поддержка плагинов
Плагины по событиям пишутся в одном `.py`-файле (`start`, `stop`, `pause`, `resume`, `session`). Плагины **по умолчанию выключены**, включаются на странице *Плагины*; неисправный плагин не роняет приложение. В комплекте два примера.

### 2️⃣1️⃣ Языки
**Türkçe · English · Русский** — выбираются в настройках и переключаются мгновенно **без перезапуска** (включая записи журнала).

### 2️⃣2️⃣ Темы
- **Тёмная тема** — чёрный фон и **бордовый текст** (фирменный стиль 4R022); яркий бордовый оттенок обеспечивает читаемость.
- **Светлая тема** — чистый белый фон и бордовые акценты.
Тема меняется мгновенно и запоминается.

### 2️⃣3️⃣ Интерфейс
Градиентные кнопки с эффектом нажатия, единая **панель действий**, компактный **фирменный заголовок**, карточки с акцентными заголовками, плитки статистики, переключатели-«таблетки», **флажки с галочкой**, переключатели с точкой и 7 страниц: *Главная · Дополнительно · CPS-тест · Статистика · Журналы · Плагины · Настройки*.

### 2️⃣4️⃣ Работа в фоне и системный трей
При закрытии окна приложение может **продолжать работать в фоне** (по желанию). Правый щелчок по значку в трее: *Показать/скрыть окно · Главная · CPS · Настройки · Старт/Стоп · KillSwitch · Выход*. Также доступны *запуск, свёрнутым в трей*, *всегда поверх окон*, *подтверждение выхода*.

### 2️⃣5️⃣ Мини-панель состояния
Небольшая **перетаскиваемая панель поверх всех окон**: состояние, число кликов, текущий CPS и время. Включается в настройках.

### 2️⃣6️⃣ Доступность
Полная навигация с клавиатуры (`Ctrl+1 … Ctrl+7` — страницы, `Ctrl+Q` — выход), заметные рамки фокуса, доступные имена элементов, **размер текста 80–160 %**, высококонтрастная бордовая палитра и система горячих клавиш, позволяющая управлять основными функциями с клавиатуры.

### 2️⃣7️⃣ Выбор движка кликов и цепочка резервов
Автоматический выбор: **в Windows `win32` → `pynput` → `pyautogui`**, в остальных системах `pynput` → `pyautogui`. Можно выбрать вручную в настройках. Если движка нет, приложение не падает — переходит на безопасный *пустой* движок, а диагностика объясняет причину.

### 2️⃣8️⃣ Настройки, обслуживание и механизм обновления
Все настройки сохраняются автоматически (атомарная запись, устойчивость к повреждению файла). Раздел **«Обслуживание»** безопасно сбрасывает настройки (история сохраняется). У файла настроек есть **миграция схемы**: настройки старых версий обновляются без потерь, а обновление записывается в журнал. Раздел **«О программе»** в самом низу настроек показывает сводку, новинки и сведения о системе (копируются одним нажатием).

<a name="ru-keys"></a>
## ⌨️ Горячие клавиши по умолчанию

| Действие | Клавиша | Примечание |
|---|---|---|
| Старт | `F6` | Можно назначить любую клавишу |
| Стоп | `F7` | Защита клавиш не действует |
| Пауза / Продолжить | `F8` | |
| Добавить цель | `F9` | Добавляет позицию курсора в список |
| **KillSwitch** | `Ctrl+Shift+F12` | Мгновенно останавливает всё |
| Страницы | `Ctrl+1 … Ctrl+7` | Навигация с клавиатуры |
| Выход | `Ctrl+Q` | |

<a name="ru-platforms"></a>
## 🖥️ Поддержка платформ

| Платформа | Движок | Примечания |
|---|---|---|
| **Windows 10/11** | `win32` → `pynput` | Чтобы кликать в приложениях с правами администратора, запускайте AutoClicker тоже от администратора |
| **macOS 12+** | `pynput` | Выдайте права **«Универсальный доступ»** и **«Мониторинг ввода»** в *Системных настройках → Конфиденциальность и безопасность* |
| **Linux (X11)** | `pynput` | Полная поддержка. В **Wayland** глобальные клавиши и клики ограничены — используйте сеанс X11 |

<a name="ru-arch"></a>
## 🏗️ Архитектура: Core + Worker

```
Main/
├── main.py                      точка входа (--selftest, --version, --minimized)
├── autoclicker/
│   ├── core/                    ядро без GUI (полностью покрыто тестами)
│   │   ├── engine.py            ClickEngine: жизненный цикл, записи сессий, события
│   │   ├── workers.py           ClickWorker (точный поток кликов) + TaskPool (универсальный пул Worker)
│   │   ├── backend.py           цепочка Win32 → pynput → pyautogui (+ тестовый Dummy-движок)
│   │   ├── hotkeys.py           глобальные клавиши, сопоставление сочетаний, защита клавиш
│   │   ├── killswitch.py        аварийная остановка + watchdog + автоотключение
│   │   ├── cps_test.py          логика и статистика CPS-теста
│   │   ├── session.py           хранилища сессий / активности / CPS (JSONL)
│   │   ├── exporter.py          экспорт TXT · JSON · CSV
│   │   ├── plugins.py           менеджер плагинов
│   │   └── config.py            модель настроек, проверка, миграция схемы
│   ├── i18n/                    tr.json · en.json · ru.json
│   ├── ui/                      интерфейс PySide6 (7 страниц, тема, трей, мини-панель)
│   └── plugins_examples/        примеры плагинов
├── tests/                       41 модульный тест
Build/
├── build.py                     автоматическая эффектная система сборки
└── 4R022-AutoClicker.spec       описание PyInstaller
```

- **Core** не импортирует GUI-библиотек; движок, клавиши и статистика тестируются без интерфейса.
- **ClickWorker** кликает в собственном потоке. Интерфейс лишь читает снимок состояния с частотой 10 Гц — сигналов на каждый клик нет, поэтому на высоком CPS интерфейс не тормозит.
- **TaskPool** выполняет нережимные по времени задачи (например, экспорт) в фоне.
- **Планировщик** без дрейфа: грубое ожидание + точное ожидание последних миллисекунд; после зависания он не «догоняет» серией кликов.

<a name="ru-plugins"></a>
## 🧩 Написание плагинов

Положите один `.py`-файл в папку `plugins` (откройте её на странице *Плагины*):

```python
PLUGIN_INFO = {"name": "Привет", "version": "1.0", "author": "Я", "description": "Записывает каждую сессию"}

def register(api):
    def done(record):                       # record: total_clicks, avg_cps, stop_reason ...
        api.log(f"Выполнено кликов: {record['total_clicks']}")
    api.on("session", done)                 # события: start · stop · pause · resume · session
```

> ⚠️ Плагины выполняются с полными правами Python. Включайте только доверенный код.

<a name="ru-data"></a>
## 📁 Расположение данных

| Платформа | Путь |
|---|---|
| Windows | `%APPDATA%\4R022-AutoClicker` |
| macOS | `~/Library/Application Support/4R022-AutoClicker` |
| Linux | `~/.local/share/4R022-AutoClicker` |

Содержимое: `config.json`, `sessions.jsonl`, `activity.jsonl`, `cps_results.json`, `logs/`, `plugins/`. Папка экспорта по умолчанию — `Documents/4R022-AutoClicker-Exports`. Для портативного использования переменная окружения `AUTOCLICKER_4R022_HOME` перенаправляет папку данных.

<a name="ru-build"></a>
## 🤖 Автоматическая система сборки и CI

```bash
python Build/build.py                # полный конвейер
python Build/build.py --dry-run      # все проверки, кроме PyInstaller
python Build/build.py --onedir       # папка вместо одного файла
```

**Конвейер:** проверка окружения → модульные тесты → самопроверка исходников (включая GUI) → проверка ресурсов и языков → **PyInstaller** → **проверка собранного приложения через `--selftest-gui`** → упаковка (`.zip` / `.tar.gz`) → SHA-256 → `BUILD_REPORT.md` + `build-info.json`. Если любой шаг не проходит, сборка **останавливается, пакет не создаётся**.

| Workflow | Триггер | Что делает |
|---|---|---|
| `ci.yml` | push / PR | Тесты + самопроверка GUI + пробный прогон сборки в 3 ОС |
| `build.yml` | тег `v*` / вручную | Собирает, проверяет и публикует пакеты Windows + macOS + Linux как **Release** (теги с `b` становятся *pre-release*) |

```bash
git tag v1.5.0b1 && git push origin v1.5.0b1
```

<a name="ru-tests"></a>
## 🧪 Тесты
```bash
cd Main
python -m unittest discover -s tests -t . -v
```
Покрытие: движок (число кликов, двойной/серия, циклы, порядок целей, пауза/продолжение, задержка старта, случайный интервал, защита углом, макс. время, порог ошибок), сопоставление клавиш (сочетания, автоповтор, защита клавиш, захват), статистика CPS, проверка настроек и миграция схемы, повреждённые файлы, экспорт, плагины, целостность темы и **целостность переводов TR/EN/RU**.

<a name="ru-faq"></a>
## 🛠️ Решение проблем

| Проблема | Решение |
|---|---|
| Не работают горячие клавиши | Проверьте «Hotkey listener» в *Журналы → Диагностика*. В macOS проверьте разрешения, в Linux используйте сеанс X11 |
| Клики не проходят в некоторых окнах | Если целевое приложение запущено от администратора, запустите AutoClicker тоже от администратора (Windows) |
| Не запускается в Linux | `sudo apt install libxcb-cursor0 libegl1` |
| Не получается остановить | Нажмите `Ctrl+Shift+F12` или переместите курсор в левый верхний угол |
| Повреждены настройки | Приложение сохраняет сломанный файл как `config.json.bak` и возвращается к значениям по умолчанию |

<a name="ru-legal"></a>
## ⚖️ Ответственное использование

Программа предназначена для тестирования, доступности и автоматизации **на вашем собственном компьютере**. Соблюдать условия использования программ и сервисов, с которыми вы её применяете, — ваша ответственность. Лицензия: [MIT](LICENSE).

[⬆️ Наверх](#top)

---

<div align="center">

**4R022** · Professional AutoClick Application · `1.5V Beta`

</div>
