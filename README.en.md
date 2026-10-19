<div align="center">

<img src="Main/autoclicker/assets/logo.png" width="300" alt="4R022 AutoClicker">

# 4R022 AutoClicker

**Professional AutoClick Application** · `1.0V Beta`

[🇹🇷 Türkçe](README.md) · 🇬🇧 **English**

*Precise timing · Multi-target · KillSwitch safety · CPS test · Bordeaux/black 4R022 look*

</div>

---

## 📸 Screenshots

Generated automatically by `Build/screenshots.py` (CI refreshes them on every push to `main`).

<div align="center">

| Home (dark · bordeaux) | CPS Test |
|:---:|:---:|
| <img src="docs/screenshots/home-dark.png" width="440"> | <img src="docs/screenshots/cps-dark.png" width="440"> |
| **Advanced** | **Statistics** |
| <img src="docs/screenshots/advanced-dark.png" width="440"> | <img src="docs/screenshots/stats-dark.png" width="440"> |
| **Logs & Diagnostics** | **Settings** |
| <img src="docs/screenshots/logs-dark.png" width="440"> | <img src="docs/screenshots/settings-dark.png" width="440"> |
| **Light theme – Home** | **Light theme – CPS** |
| <img src="docs/screenshots/home-light.png" width="440"> | <img src="docs/screenshots/cps-light.png" width="440"> |

</div>

---

## ✨ Features

* **Clicking** – left / right / middle button; single, double and automatic burst clicks; interval in hours / minutes / seconds / milliseconds; unlimited or fixed click count.
* **Targeting** – current cursor position, a fixed X/Y point, or a **multi-target list** (sequential · random · ping-pong). Capture points with a 3-second countdown or the *add target* hotkey.
* **Precision** – drift-free scheduler (coarse wait + short spin for the last milliseconds).
* **Advanced** – start delay, random min–max interval, position jitter, hold duration, loops, max runtime, pause / resume without losing counters.
* **KillSwitch** – hotkey, big red button, top-left-corner failsafe, auto shutdown and a watchdog that releases stuck mouse buttons.
* **Hotkeys** – *any* key (plus Ctrl/Shift/Alt combos) can be bound to any action. Defaults: F6 start, F7 stop, F8 pause, F9 add target, Ctrl+Shift+F12 KillSwitch.
* **Statistics** – total clicks, elapsed time, average / live / peak CPS, session history, live chart, export to **TXT · JSON · CSV**, app sign-in/sign-out tracking.
* **Logs** – filterable task-tracking log, error log, diagnostics page.
* **CPS test** – 15 / 30 / 60 s runs, per-second chart, peak CPS, consistency, fatigue analysis, ranks and personal bests.
* **Plugins** – event-based Python plugins (`start`, `stop`, `pause`, `resume`, `session`); disabled by default.
* **3 languages** (TR · EN · RU) and **2 themes** (dark with bordeaux text, light) – both switch live, no restart.
* **Background mode** – lives in the system tray; right-click for Home / CPS / Settings / Start-Stop / KillSwitch. **Key protection** requires a double-press for Start / Pause / Add-target while in the background.
* **Accessibility** – full keyboard navigation (Ctrl+1…7), text size 80–160 %, accessible names, high-contrast bordeaux palette.

## 🏗️ Architecture

`Main/autoclicker/core` is GUI-free (engine, worker, backends, hotkeys, killswitch, stores, exporter, plugins) and fully unit-tested. `ClickWorker` runs clicks on a dedicated thread; the UI only polls a snapshot at 10 Hz, so even very high CPS never slows the interface. `TaskPool` handles non-realtime jobs (exports, IO). Safety-critical hotkeys (Stop, KillSwitch) execute directly on the listener thread, independent of the UI.

## 🖥️ Platforms

| Platform | Backend | Notes |
|---|---|---|
| Windows 10/11 | `win32` → `pynput` | Run as administrator to click into elevated apps |
| macOS 12+ | `pynput` | Grant *Accessibility* and *Input Monitoring* in System Settings → Privacy & Security |
| Linux (X11) | `pynput` | Wayland limits global hotkeys/clicks – use an X11 session |

## 🚀 Run

```bash
pip install -r requirements.txt
python Main/main.py              # add --minimized to start in the tray
python Main/main.py --selftest   # headless self check
```

## 🤖 Build

```bash
python Build/build.py            # tests → self-test → PyInstaller → verify exe → package → SHA-256 → report
python Build/build.py --dry-run  # everything except PyInstaller
```

Any failing step aborts the build, so a broken app is never released. GitHub Actions: `ci.yml` (tests on 3 OS) and `build.yml` (tag `v*` → builds Windows/macOS/Linux and publishes a Release).

## 🧪 Tests

```bash
cd Main && python -m unittest discover -s tests -t . -v
```

## ⚠️ Responsible use

Intended for testing, accessibility and automation on your own computer. You are responsible for complying with the terms of service of any software you use it with.

---

<div align="center"><b>4R022</b> · Professional AutoClick Application · <code>1.0V Beta</code></div>
