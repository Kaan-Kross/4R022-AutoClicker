# 📜 4R022 AutoClicker — Changelog · Değişiklik Günlüğü · Журнал изменений

### 🌍 [🇹🇷 Türkçe](#tr) · [🇬🇧 English](#en) · [🇷🇺 Русский](#ru)

---

<a name="tr"></a>

## 🇹🇷 TÜRKÇE

**Değişiklik Günlüğü** — Biçim [Keep a Changelog](https://keepachangelog.com/) esas alınmıştır. Sürüm numaralandırması: `MAJOR.MINOR.PATCH` (`b` = beta).

### [1.5V Beta] — 2026-10-19 · `v1.5.0b1`

> 🎨 **Büyük arayüz güncellemesi** — görünüm baştan tasarlandı, altyapı yeni arayüze entegre edildi.

#### ✨ Eklenenler

**🖱️ Arayüz**

- **Aksiyon çubuğu**: Başlat / Duraklat / Durdur / ACİL DURDUR düğmeleri tek bir vurgulu çubukta; ▶ ■ ❚❚ ⚠ simgeleri.
- **Kompakt marka başlığı**: 42 px amblem + `4R022 · AUTOCLICKER` yazısı.
- **Tik işaretli onay kutuları** ve **noktalı seçenek düğmeleri** (yüksek çözünürlük için `@2x` görseller); eklenti listesi de aynı stile geçti.
- **Ayarlar › Bakım** bölümü: ayarları güvenle sıfırlama + açıklama.
- **Ayarlar › Uygulama Hakkında** (sayfanın en altı): logo, sürüm, platform/dil/tema rozetleri, özet metin, özellik listesi, 1.5'te yenilikler, sistem satırı, *sistem bilgisini kopyala* ve *veri klasörünü aç*.

**🔄 Altyapı**

- Ayar dosyasına `config_schema` ve `app_version` alanları; 1.0 → 1.5 **otomatik göç** (kullanıcı değerleri korunur).
- **Güncelleme algılama**: sürüm değişince günlükte ve etkinlik kaydında *"Güncelleme algılandı: 1.0V Beta → 1.5V Beta"*.
- Ayar kaydı artık serileştirme hatalarına karşı korumalı: önce serileştirir, sonra yazar; geçici dosya hatada temizlenir.
- Yeni testler: ayar göçü, QSS bütünlüğü, tik/nokta varlıkları. Toplam **41 birim testi**.

**📖 Belgeler**

- README **TR / EN / RU** olarak alt alta, 28 özelliğin tek tek tanıtımıyla yeniden yazıldı; ekran görüntüsü bölümü kaldırıldı.
- Bu değişiklik günlüğü üç dilde ve ayrıntılı biçimde yeniden düzenlendi.

#### 🔧 Değişenler

- **Logo küçültüldü**: kenar çubuğundaki 196 px'lik tam logo yerine kompakt başlık; kenar çubuğu 232 → 214 px. Tam logo yalnızca Hakkında bölümünde.
- **Butonlar**: 10–12 px yuvarlak köşe, gradyan dolgu, alt kenarlıkla "basılabilir" görünüm, basınca aşağı kayma, odak halkası; segment düğmeleri hap şeklinde.
- **Gezinme**: etkin sayfada sol vurgu çubuğu ve gradyan dolgu.
- **Kartlar ve kutucuklar**: bölüm başlıklarında bordo vurgu çizgisi, istatistik kutucuklarında üst vurgu şeridi, daha yumuşak kenarlar.
- **Giriş alanları, sekmeler, tablolar, kaydırma çubukları, menüler, ilerleme çubuğu, kaydırıcı** yeni görünüme kavuştu; odaktaki alan belirgin çerçeve alır.
- **CPS TIKLA düğmesi**: kalın, basınca çöken 3B görünüm.
- **Ana Sayfa**: *Tıklama* ve *Tıklama sayısı* kartları yan yana iki sütunda.
- Sürüm `1.0V Beta` → `1.5V Beta` (`1.5.0b1`); spec, paketleme ve belgeler güncellendi.
- README için otomatik ekran görüntüsü üretimi (CI işi ve betik) kaldırıldı.

#### 🔒 Uyumluluk

- 1.0 ayar dosyaları sorunsuz yüklenir; hiçbir kullanıcı değeri kaybolmaz. Oturum geçmişi ve CPS rekorları aynen korunur.

#### ⚠️ Bilinen sınırlamalar

- 1.0 Beta'daki sınırlamalar geçerlidir (Wayland, macOS izinleri, yönetici pencereleri, imzasız paketler).
- Arayüz yenilemesinin ilk gerçek Qt çalıştırması kullanıcı makinesinde yapılır; görsel ince ayarlar bir sonraki sürüme alınır.

### [1.0V Beta] — 2026-10-18 · `v1.0.0b1`

> 🎉 **4R022 AutoClicker'ın ilk herkese açık beta sürümü.**

#### ✨ Eklenenler

**🖱️ Tıklama motoru**

- Sol / sağ / orta fare tuşu desteği.
- **Tek**, **çift** (30 ms arayla) ve **otomatik seri** tıklama; seri başına tıklama ve seri içi bekleme ayarlanabilir.
- **Saat · dakika · saniye · milisaniye** aralık girişi; seçilen aralığın tık/sn karşılığı canlı gösterilir.
- Tıklama sayısı: **belirli sayı** veya **sınırsız**; çift/seri modlarda limit tıklama bazında tam uygulanır.
- **Kaymasız zamanlayıcı**: kaba bekleme + son milisaniyelerde hassas bekleme; takılma sonrası "yakalama patlaması" yapmaz.
- **Duraklat / devam et**: sayaçlar sıfırlanmaz, duraklama süresi geçen süreye sayılmaz.

**🎯 Hedefleme**

- **Mevcut konum**, **sabit nokta (X/Y)** ve **çoklu hedef** modları.
- Hedef listesi: satır ekle/sil, yukarı–aşağı taşı, etiketle, temizle; hücreler çift tıkla düzenlenir.
- **3 saniyelik geri sayımla** konum yakalama ve **"Hedef ekle" kısayolu** (varsayılan `F9`).
- Geçiş sırası: **sırayla**, **rastgele**, **ileri-geri**; konum sapması (jitter) ve aktif hedef göstergesi.

**⚙️ Gelişmiş**

- Başlangıç gecikmesi, basılı tutma süresi, **rastgele aralık (min–maks)**, döngü sayısı, azami çalışma süresi.
- Döngü tanımı: çoklu hedefte listede 1 tam tur; diğer modlarda 1 tıklama işlemi. Hangi limit önce dolarsa işlem biter.

**🛑 KillSwitch & Güvenlik**

- **Acil durdur** kısayolu (`Ctrl+Shift+F12`) ve büyük kırmızı arayüz düğmesi.
- **Köşe güvenliği**: imleç sol üst köşeye gidince işlem durur.
- **Otomatik kapatma**: kesintisiz çalışma süresi dolunca durdurur; isteğe bağlı olarak uygulamadan çıkar.
- **Watchdog**: tıklama iş parçacığı yanıt vermezse fare tuşlarını serbest bırakır.
- Üst üste 5 tıklama hatasında motor durur; iş bitince veya hatada basılı tuşlar her zaman bırakılır.
- Durdur ve KillSwitch, arayüzden bağımsız olarak kısayol iş parçacığında çalışır.
- **Tuş koruması**: arka plandayken Başlat / Duraklat / Hedef-ekle yalnızca çift basışla tetiklenir.

**⌨️ Kısayollar**

- **Her tuş** ve Ctrl / Shift / Alt / Cmd kombinasyonları herhangi bir eyleme atanabilir ("bir tuşa basın" yakalama modu).
- Çakışma denetimi, varsayılana dönme, tuş tekrarı filtresi, kaçırılan tuş-bırakma olayına karşı kurtarma.

**📊 İstatistik ve Günlükler**

- Toplam tıklama, geçen süre, ortalama / **anlık** / tepe CPS, hata sayısı ve son 60 saniyelik canlı grafik.
- **Oturum geçmişi** (tarih, süre, tıklama, ort./tepe CPS, tür/mod, bitiş nedeni).
- **Uygulama giriş-çıkış takibi** ve oturum başlangıç/bitiş kayıtları.
- **TXT · JSON · CSV** dışa aktarma (CSV Excel uyumlu); dışa aktarma klasörünü seçme ve uygulamadan açma.
- **Profesyonel görev takip günlüğü** (Bilgi/Uyarı/Hata filtresi; dil değişimine uyumlu), **hata günlüğü**, **tanılama** ekranı.
- Çalışma durumunu gösteren **küçük, sürüklenebilir durum paneli**.

**⚡ CPS Testi**

- **15 / 30 / 60 saniye** testleri; ilk tıklama testi başlatır; tıklama *basış anında* sayılır.
- Canlı sayaç, ilerleme çubuğu, saniye başına tıklama grafiği.
- Toplam, ortalama, tepe (en iyi 1 sn), skor, tutarlılık %, aralık istatistikleri, ilk-ikinci yarı CPS, **seviye** (Çaylak → Efsane).
- Süre başına **kişisel rekor**, test geçmişi ve dışa aktarma.

**🧩 Eklentiler**

- Olay tabanlı eklentiler: `start`, `stop`, `pause`, `resume`, `session`; varsayılan **kapalı**; hatalı eklenti uygulamayı çökertmez.
- İki örnek eklenti: *Session Notes*, *Beep On Stop*.

**🎨 Arayüz, Diller, Erişilebilirlik**

- **4R022 logosu** vurgulu; logodan türetilmiş uygulama ve tepsi simgeleri (`.ico`, `.icns`, `.png`).
- **Koyu tema** (siyah zemin, bordo yazılar) ve **Beyaz tema**; anında değişir.
- **Türkçe · English · Русский** — yeniden başlatmadan değişir.
- Yazı boyutu %80–160, tam klavye gezintisi (`Ctrl+1…7`), erişilebilir bileşen adları, görünür odak çerçeveleri.
- 7 sayfa: Ana Sayfa · Gelişmiş · CPS Testi · İstatistikler · Günlükler · Eklentiler · Ayarlar.

**🫥 Arka plan**

- Pencere kapatılınca arka planda çalışmaya devam eder; tepsi menüsü: Pencere · Ana Sayfa · CPS · Ayarlar · Başlat/Durdur · KillSwitch · Çıkış.
- Tepsiye küçültülmüş başlama, her zaman üstte, çıkışta onay isteme seçenekleri.

**🖥️ Platform**

- **Windows** (`win32` motoru), **macOS** ve **Linux/X11** (`pynput`); `pyautogui` isteğe bağlı yedek.
- Otomatik motor seçimi ve yedek zinciri; hiçbir motor yoksa güvenli *boş* motor + tanılama açıklaması.

**🏗️ Mimari ve Build**

- **Core** (GUI'siz) + **Worker** sistemi: `ClickWorker` ve `TaskPool`; arayüz motoru 10 Hz anlık görüntüyle okur.
- Atomik, bozulmaya dayanıklı ayar kaydı; bozuk `config.json` yedeklenip varsayılana dönülür; bozuk JSONL satırları atlanır.
- **Otomatik build sistemi** (`Build/build.py`): ortam → testler → self-test → PyInstaller → derlenmiş uygulamayı doğrulama → paketleme → SHA-256 → rapor; `--ci` düz modu.
- **GitHub Actions**: `ci.yml` (3 işletim sisteminde test + GUI self-test + build dry-run) ve `build.yml` (etiketle 3 platform derleme + Release).
- 38 birim testi; `--selftest` / `--selftest-gui` modları; TR/EN/RU çeviri bütünlüğü testi.
- Depo yapısı: `Main/`, `Build/`, `.github/`, README, CHANGELOG, LICENSE (MIT).

#### ⚠️ Bilinen sınırlamalar

- Linux **Wayland**'de genel kısayollar ve sentetik tıklamalar kısıtlıdır; X11 önerilir.
- macOS'ta *Erişilebilirlik* ve *Girdi İzleme* izinleri gerekir.
- Yükseltilmiş (yönetici) pencerelere tıklamak için AutoClicker da yönetici çalıştırılmalıdır (Windows).
- 0 ms aralık işlemciyi yoğun kullanır.
- Windows/macOS paketleri imzasızdır; SmartScreen / Gatekeeper uyarısı görülebilir.

#### 🔜 Planlananlar

- Kaydet-oynat (makro) modu · görüntü/renk tabanlı hedef bulma · profil sistemi · yeni diller · kod imzalama.

[⬆️](#top)

---

<a name="en"></a>

## 🇬🇧 ENGLISH

**Changelog** — Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning: `MAJOR.MINOR.PATCH` (`b` = beta).

### [1.5V Beta] — 2026-10-19 · `v1.5.0b1`

> 🎨 **Major interface update** — the look was redesigned from scratch and the infrastructure integrated with the new UI.

#### ✨ Added

**Interface**

- **Action bar**: Start / Pause / Stop / KILL SWITCH buttons in one highlighted bar; ▶ ■ ❚❚ ⚠ glyphs.
- **Compact brand header**: 42 px emblem + `4R022 · AUTOCLICKER` wordmark.
- **Tick-mark checkboxes** and **dotted radio buttons** (`@2x` images for high-DPI); the plugin list uses the same style.
- **Settings › Maintenance** section: safe settings reset with an explanation.
- **Settings › About** (bottom of the page): logo, version, platform/language/theme badges, summary text, feature list, what's new in 1.5, system line, *copy system info* and *open data folder*.

**Infrastructure**

- `config_schema` and `app_version` fields in the settings file; automatic **1.0 → 1.5 migration** (user values preserved).
- **Update detection**: when the version changes the log and activity record show *"Update detected: 1.0V Beta → 1.5V Beta"*.
- Settings saving is now safe against serialization errors: it serializes first, then writes; the temp file is cleaned up on failure.
- New tests: settings migration, QSS integrity, tick/dot assets. **41 unit tests** in total.

**Docs**

- README rewritten in **TR / EN / RU** stacked, introducing all 28 features one by one; the screenshots section was removed.
- This changelog was reorganised in three languages with more detail.

#### 🔧 Changed

- **Logo scaled down**: compact header instead of the 196 px full logo in the sidebar; sidebar 232 → 214 px. The full logo now lives only in About.
- **Buttons**: 10–12 px rounded corners, gradient fill, bottom border for a "pressable" look, press-down shift, focus ring; segmented buttons are pill-shaped.
- **Navigation**: active page gets a left accent bar and gradient fill.
- **Cards and tiles**: bordeaux accent line on section titles, top accent strip on statistic tiles, softer edges.
- **Inputs, tabs, tables, scrollbars, menus, progress bar and slider** got a new look; the focused field gets a clear frame.
- **CPS CLICK button**: thick, press-down 3D look.
- **Home**: the *Clicking* and *Click count* cards sit side by side in two columns.
- Version `1.0V Beta` → `1.5V Beta` (`1.5.0b1`); spec, packaging and docs updated.
- Automatic screenshot generation for the README (CI job and script) was removed.

#### 🔒 Compatibility

- 1.0 settings files load seamlessly; no user value is lost. Session history and CPS records are kept as they are.

#### ⚠️ Known limitations

- The 1.0 Beta limitations still apply (Wayland, macOS permissions, elevated windows, unsigned packages).
- The first real Qt run of the refreshed UI happens on the user's machine; visual fine-tuning goes into the next release.

### [1.0V Beta] — 2026-10-18 · `v1.0.0b1`

> 🎉 **The first public beta of 4R022 AutoClicker.**

#### ✨ Added

**Click engine**

- Left / right / middle mouse button support.
- **Single**, **double** (30 ms apart) and **automatic burst** clicks; clicks per burst and in-burst gap are adjustable.
- Interval entry in **hours · minutes · seconds · milliseconds**; the clicks/s equivalent is shown live.
- Click count: **fixed** or **unlimited**; in double/burst modes the limit is applied exactly per click.
- **Drift-free scheduler**: coarse wait + precise wait for the last milliseconds; no "catch-up burst" after a stall.
- **Pause / resume**: counters are kept, paused time is excluded from elapsed time.

**Targeting**

- **Current position**, **fixed point (X/Y)** and **multi-target** modes.
- Target list: add/delete rows, move up/down, label, clear; cells edit on double-click.
- Position capture with a **3-second countdown** and an **"Add target" hotkey** (default `F9`).
- Visit order: **sequential**, **random**, **ping-pong**; position jitter and an active-target indicator.

**Advanced**

- Start delay, hold duration, **random interval (min–max)**, loop count, max runtime.
- Loop definition: with multiple targets one full pass of the list; otherwise one click action. Whichever limit is reached first ends the run.

**Safety**

- **Emergency stop** hotkey (`Ctrl+Shift+F12`) and a big red UI button.
- **Corner failsafe**: clicking stops when the cursor reaches the top-left corner.
- **Auto shutdown**: stops after the continuous-run limit; optionally quits the app.
- **Watchdog**: releases mouse buttons if the click thread stops responding.
- Five consecutive click errors stop the engine; held buttons are always released on finish or error.
- Stop and KillSwitch run on the hotkey thread, independent of the UI.
- **Key protection**: in the background, Start / Pause / Add-target fire only on a double press.

**Hotkeys**

- **Any key** and Ctrl / Shift / Alt / Cmd combos can be bound to any action ("press a key" capture mode).
- Conflict detection, reset to defaults, key-repeat filter, recovery from a missed key-release event.

**Statistics & Logs**

- Total clicks, elapsed time, average / **live** / peak CPS, error count and a live 60-second chart.
- **Session history** (date, duration, clicks, avg/peak CPS, type/mode, stop reason).
- **Application sign-in/sign-out tracking** and session start/end records.
- **TXT · JSON · CSV** export (Excel-friendly CSV); choose and open the export folder from the app.
- **Professional task-tracking log** (Info/Warning/Error filter; follows language changes), **error log**, **diagnostics** page.
- A **small draggable status panel** showing the run state.

**CPS Test**

- **15 / 30 / 60 second** tests; the first click starts the test; clicks count on *press*.
- Live counter, progress bar, clicks-per-second chart.
- Total, average, peak (best 1 s), score, consistency %, gap statistics, first/second-half CPS, **rank** (Rookie → Legend).
- **Personal best** per duration, test history and export.

**Plugins**

- Event-based plugins: `start`, `stop`, `pause`, `resume`, `session`; **off** by default; a faulty plugin never crashes the app.
- Two example plugins: *Session Notes*, *Beep On Stop*.

**UI, Languages, Accessibility**

- **4R022 logo** featured; app and tray icons derived from the logo (`.ico`, `.icns`, `.png`).
- **Dark theme** (black background, bordeaux text) and **Light theme**; switches instantly.
- **Türkçe · English · Русский** — switches without restarting.
- Text size 80–160 %, full keyboard navigation (`Ctrl+1…7`), accessible widget names, visible focus rings.
- 7 pages: Home · Advanced · CPS Test · Statistics · Logs · Plugins · Settings.

**Background**

- Keeps running in the background when the window closes; tray menu: Window · Home · CPS · Settings · Start/Stop · KillSwitch · Quit.
- Options: start minimized to tray, always on top, ask before quitting.

**Platform**

- **Windows** (`win32` backend), **macOS** and **Linux/X11** (`pynput`); `pyautogui` as an optional fallback.
- Automatic backend selection and fallback chain; with no backend a safe *no-op* backend plus a diagnostics explanation.

**Architecture & Build**

- **Core** (GUI-free) + **Worker** system: `ClickWorker` and `TaskPool`; the UI reads the engine via 10 Hz snapshots.
- Atomic, corruption-tolerant settings saving; a broken `config.json` is backed up and defaults are used; corrupt JSONL lines are skipped.
- **Automatic build system** (`Build/build.py`): environment → tests → self-test → PyInstaller → verify built app → package → SHA-256 → report; `--ci` plain mode.
- **GitHub Actions**: `ci.yml` (tests + GUI self-test + build dry run on 3 OS) and `build.yml` (3-platform build on tag + Release).
- 38 unit tests; `--selftest` / `--selftest-gui` modes; TR/EN/RU translation-integrity test.
- Repository layout: `Main/`, `Build/`, `.github/`, README, CHANGELOG, LICENSE (MIT).

#### ⚠️ Known limitations

- On Linux **Wayland**, global hotkeys and synthetic clicks are limited; X11 is recommended.
- macOS needs *Accessibility* and *Input Monitoring* permissions.
- To click into elevated (administrator) windows, run AutoClicker as administrator too (Windows).
- A 0 ms interval is CPU-intensive.
- Windows/macOS packages are unsigned; SmartScreen / Gatekeeper warnings may appear.

#### 🔜 Planned

- Record-and-replay (macro) mode · image/colour-based target finding · profiles · more languages · code signing.

[⬆️](#top)

---

<a name="ru"></a>

## 🇷🇺 РУССКИЙ

**Журнал изменений** — Формат основан на [Keep a Changelog](https://keepachangelog.com/). Нумерация версий: `MAJOR.MINOR.PATCH` (`b` = бета).

### [1.5V Beta] — 2026-10-19 · `v1.5.0b1`

> 🎨 **Крупное обновление интерфейса** — внешний вид переработан с нуля, инфраструктура интегрирована с новым UI.

#### ✨ Добавлено

**Интерфейс**

- **Панель действий**: кнопки «Старт» / «Пауза» / «Стоп» / «АВАРИЙНЫЙ СТОП» в одной выделенной панели; значки ▶ ■ ❚❚ ⚠.
- **Компактный фирменный заголовок**: эмблема 42 px + надпись `4R022 · AUTOCLICKER`.
- **Флажки с галочкой** и **переключатели с точкой** (изображения `@2x` для высокого DPI); список плагинов в том же стиле.
- Раздел **Настройки › Обслуживание**: безопасный сброс настроек с пояснением.
- **Настройки › О программе** (внизу страницы): логотип, версия, значки платформ/языка/темы, краткое описание, список возможностей, новинки 1.5, строка о системе, *копировать сведения* и *открыть папку данных*.

**Инфраструктура**

- Поля `config_schema` и `app_version` в файле настроек; автоматическая **миграция 1.0 → 1.5** (значения пользователя сохраняются).
- **Обнаружение обновления**: при смене версии в журнале и журнале активности появляется *«Обнаружено обновление: 1.0V Beta → 1.5V Beta»*.
- Сохранение настроек защищено от ошибок сериализации: сначала сериализация, затем запись; временный файл удаляется при сбое.
- Новые тесты: миграция настроек, целостность QSS, ресурсы галочки/точки. Всего **41 модульный тест**.

**Документация**

- README переписан на **TR / EN / RU** подряд, с описанием всех 28 возможностей по отдельности; раздел со скриншотами удалён.
- Этот журнал изменений переработан на трёх языках и стал подробнее.

#### 🔧 Изменено

- **Логотип уменьшен**: вместо полного логотипа 196 px в боковой панели — компактный заголовок; панель 232 → 214 px. Полный логотип остался только в «О программе».
- **Кнопки**: скругление 10–12 px, градиентная заливка, нижняя кромка для «нажимаемого» вида, смещение при нажатии, кольцо фокуса; сегментные кнопки в форме «таблетки».
- **Навигация**: у активной страницы левая акцентная полоса и градиентная заливка.
- **Карточки и плитки**: бордовая акцентная линия у заголовков разделов, верхняя полоса у плиток статистики, более мягкие края.
- **Поля ввода, вкладки, таблицы, полосы прокрутки, меню, индикатор прогресса и ползунок** получили новый вид; поле в фокусе выделяется рамкой.
- **Кнопка CPS «КЛИК»**: массивный объёмный вид с эффектом нажатия.
- **Главная**: карточки *Клик* и *Количество кликов* расположены в две колонки.
- Версия `1.0V Beta` → `1.5V Beta` (`1.5.0b1`); обновлены spec, упаковка и документация.
- Автоматическое создание скриншотов для README (задание CI и скрипт) удалено.

#### 🔒 Совместимость

- Файлы настроек 1.0 загружаются без проблем; ни одно значение пользователя не теряется. История сессий и рекорды CPS сохраняются.

#### ⚠️ Известные ограничения

- Ограничения 1.0 Beta сохраняются (Wayland, разрешения macOS, окна с правами администратора, неподписанные пакеты).
- Первый реальный запуск обновлённого интерфейса на Qt выполняется на машине пользователя; визуальная доводка — в следующем релизе.

### [1.0V Beta] — 2026-10-18 · `v1.0.0b1`

> 🎉 **Первая публичная бета-версия 4R022 AutoClicker.**

#### ✨ Добавлено

**Движок кликов**

- Поддержка левой / правой / средней кнопок мыши.
- **Одиночный**, **двойной** (через 30 мс) и **автосерия** кликов; число кликов в серии и пауза внутри серии настраиваются.
- Ввод интервала в **часах · минутах · секундах · миллисекундах**; эквивалент в кликах/с показывается сразу.
- Число кликов: **заданное** или **без ограничений**; в двойном/серийном режимах лимит применяется точно по кликам.
- **Планировщик без дрейфа**: грубое ожидание + точное ожидание последних миллисекунд; нет «догоняющей серии» после зависания.
- **Пауза / продолжение**: счётчики не сбрасываются, время паузы не входит в прошедшее время.

**Прицеливание**

- Режимы **текущей позиции**, **фиксированной точки (X/Y)** и **нескольких целей**.
- Список целей: добавление/удаление строк, перемещение вверх/вниз, метки, очистка; ячейки правятся двойным щелчком.
- Захват позиции с **обратным отсчётом 3 с** и горячая клавиша **«Добавить цель»** (по умолчанию `F9`).
- Порядок обхода: **по порядку**, **случайно**, **туда-обратно**; разброс позиции (jitter) и индикатор активной цели.

**Дополнительно**

- Задержка старта, время удержания, **случайный интервал (мин–макс)**, число циклов, максимальное время работы.
- Определение цикла: при нескольких целях — один полный проход по списку; иначе — одно действие клика. Работа заканчивается по первому достигнутому лимиту.

**Безопасность**

- Горячая клавиша **аварийной остановки** (`Ctrl+Shift+F12`) и большая красная кнопка в интерфейсе.
- **Защита углом**: клики останавливаются, когда курсор попадает в левый верхний угол.
- **Автоотключение**: остановка по истечении времени непрерывной работы; по желанию — выход из приложения.
- **Watchdog**: отпускает кнопки мыши, если поток кликов перестал отвечать.
- Пять ошибок клика подряд останавливают движок; зажатые кнопки всегда отпускаются при завершении или ошибке.
- «Стоп» и KillSwitch выполняются в потоке горячих клавиш независимо от интерфейса.
- **Защита клавиш**: в фоне «Старт» / «Пауза» / «Добавить цель» срабатывают только по двойному нажатию.

**Горячие клавиши**

- **Любую клавишу** и сочетания Ctrl / Shift / Alt / Cmd можно назначить на любое действие (режим захвата «нажмите клавишу»).
- Проверка конфликтов, сброс по умолчанию, фильтр автоповтора, восстановление после пропущенного события отпускания клавиши.

**Статистика и журналы**

- Всего кликов, прошедшее время, средний / **текущий** / пиковый CPS, число ошибок и живой график за 60 секунд.
- **История сессий** (дата, длительность, клики, средний/пиковый CPS, тип/режим, причина остановки).
- **Учёт входа/выхода из приложения** и записи начала/окончания сессий.
- Экспорт **TXT · JSON · CSV** (CSV совместим с Excel); выбор и открытие папки экспорта из приложения.
- **Профессиональный журнал задач** (фильтр Инфо/Предупреждения/Ошибки; следует смене языка), **журнал ошибок**, страница **диагностики**.
- **Небольшая перетаскиваемая панель состояния**, показывающая ход работы.

**CPS-тест**

- Тесты на **15 / 30 / 60 секунд**; первый клик запускает тест; клик засчитывается в момент *нажатия*.
- Живой счётчик, индикатор прогресса, график кликов по секундам.
- Всего, средний, пиковый (лучшая 1 с), очки, стабильность %, статистика интервалов, CPS половин, **ранг** (Новичок → Легенда).
- **Личный рекорд** для каждой длительности, история тестов и экспорт.

**Плагины**

- Плагины по событиям: `start`, `stop`, `pause`, `resume`, `session`; по умолчанию **выключены**; неисправный плагин не роняет приложение.
- Два примера плагинов: *Session Notes*, *Beep On Stop*.

**Интерфейс, языки, доступность**

- Выделенный **логотип 4R022**; значки приложения и трея созданы из логотипа (`.ico`, `.icns`, `.png`).
- **Тёмная тема** (чёрный фон, бордовый текст) и **светлая тема**; переключаются мгновенно.
- **Türkçe · English · Русский** — переключение без перезапуска.
- Размер текста 80–160 %, полная навигация с клавиатуры (`Ctrl+1…7`), доступные имена элементов, заметные рамки фокуса.
- 7 страниц: Главная · Дополнительно · CPS-тест · Статистика · Журналы · Плагины · Настройки.

**Фон**

- При закрытии окна продолжает работать в фоне; меню трея: Окно · Главная · CPS · Настройки · Старт/Стоп · KillSwitch · Выход.
- Опции: запуск свёрнутым в трей, всегда поверх окон, подтверждение выхода.

**Платформы**

- **Windows** (движок `win32`), **macOS** и **Linux/X11** (`pynput`); `pyautogui` как необязательный резерв.
- Автовыбор движка и цепочка резервов; если движка нет — безопасный *пустой* движок и пояснение в диагностике.

**Архитектура и сборка**

- **Core** (без GUI) + система **Worker**: `ClickWorker` и `TaskPool`; интерфейс читает движок снимками 10 Гц.
- Атомарное, устойчивое к повреждениям сохранение настроек; сломанный `config.json` сохраняется копией, берутся значения по умолчанию; битые строки JSONL пропускаются.
- **Автоматическая система сборки** (`Build/build.py`): окружение → тесты → самопроверка → PyInstaller → проверка собранного приложения → упаковка → SHA-256 → отчёт; простой режим `--ci`.
- **GitHub Actions**: `ci.yml` (тесты + самопроверка GUI + пробная сборка в 3 ОС) и `build.yml` (сборка для 3 платформ по тегу + Release).
- 38 модульных тестов; режимы `--selftest` / `--selftest-gui`; тест целостности переводов TR/EN/RU.
- Структура репозитория: `Main/`, `Build/`, `.github/`, README, CHANGELOG, LICENSE (MIT).

#### ⚠️ Известные ограничения

- В Linux **Wayland** глобальные клавиши и синтетические клики ограничены; рекомендуется X11.
- В macOS нужны разрешения *Универсальный доступ* и *Мониторинг ввода*.
- Чтобы кликать в окнах с правами администратора, запускайте AutoClicker тоже от администратора (Windows).
- Интервал 0 мс сильно нагружает процессор.
- Пакеты Windows/macOS не подписаны; возможны предупреждения SmartScreen / Gatekeeper.

#### 🔜 В планах

- Режим записи и воспроизведения (макросы) · поиск цели по изображению/цвету · профили · новые языки · подпись кода.

[⬆️](#top)

---

[1.5V Beta]: https://github.com/Kaan-Kross/4R022-AutoClicker/releases/tag/v1.5.0b1
[1.0V Beta]: https://github.com/Kaan-Kross/4R022-AutoClicker/releases/tag/v1.0.0b1
