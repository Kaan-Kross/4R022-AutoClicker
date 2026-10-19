#!/usr/bin/env python3
"""
4R022 AutoClicker - automatic build system
==========================================

One command builds, verifies and packages the app for the CURRENT platform
(Windows / macOS / Linux):

    python Build/build.py                 full pipeline
    python Build/build.py --dry-run       run every check except PyInstaller (fast, safe)
    python Build/build.py --skip-tests    skip unit tests
    python Build/build.py --onedir        folder build instead of a single file
    python Build/build.py --ci            plain output (no animation) for CI logs
    python Build/build.py --clean         wipe Build/output + Build/work first

Pipeline:  environment -> unit tests -> source self-test -> assets -> PyInstaller
           -> verify built executable (--version, --selftest-gui) -> package -> checksums -> report
Any failing step aborts the build with a non-zero exit code, so a broken app can never be released.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "Main"
BUILD = ROOT / "Build"
OUT = BUILD / "output"
WORK = BUILD / "work"
SPEC = BUILD / "4R022-AutoClicker.spec"
NAME = "4R022-AutoClicker"

sys.path.insert(0, str(MAIN))
from autoclicker import VERSION_LABEL, __version__  # noqa: E402

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
PLATFORM = "windows" if IS_WIN else "macos" if IS_MAC else "linux"
ARCH = platform.machine().lower() or "x64"

# ---------------------------------------------------------------- pretty console
ANSI = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
if IS_WIN and ANSI:
    os.system("")          # enables ANSI escape processing on Windows 10+


def c(code: int | str, text: str) -> str:
    return f"\033[38;5;{code}m{text}\033[0m" if ANSI else text


def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m" if ANSI else text


BANNER = r"""
   _  _ ____   ___ ____  ____
  | || |  _ \ / _ \___ \|___ \
  | || | |_) | | | |__) | __) |
  |__   _|  _ <| |_| / __/ / __/
     |_| |_| \_\\___/_____|_____|   AutoClicker  ·  Build System
"""


def banner() -> None:
    for i, line in enumerate(BANNER.splitlines()):
        print(c([88, 124, 160, 196, 160][i % 5], line))
    print(c(131, f"  v{VERSION_LABEL}  ·  {PLATFORM}/{ARCH}  ·  Python {platform.python_version()}"))
    print(c(238, "  " + "─" * 66))


class Spinner:
    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, label: str, enabled: bool):
        self.label, self.enabled = label, enabled
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        i = 0
        while not self._stop.is_set():
            sys.stdout.write(f"\r  {c(196, self.FRAMES[i % len(self.FRAMES)])} {self.label} ")
            sys.stdout.flush()
            i += 1
            time.sleep(0.08)

    def __enter__(self):
        if self.enabled:
            self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self.enabled:
            self._t.join()
            sys.stdout.write("\r" + " " * (len(self.label) + 12) + "\r")


class Pipeline:
    def __init__(self, ci: bool, total: int):
        self.ci = ci or not ANSI
        self.total = total
        self.n = 0
        self.results: list[dict] = []
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "logs").mkdir(exist_ok=True)
        self.logfile = open(OUT / "logs" / "build.log", "w", encoding="utf-8")

    def step(self, title: str, fn, *, optional: bool = False):
        self.n += 1
        label = f"[{self.n}/{self.total}] {title}"
        t0 = time.time()
        if self.ci:
            print(f"::group::{label}" if os.environ.get("GITHUB_ACTIONS") else f">> {label}", flush=True)
        self.logfile.write(f"\n===== {label} =====\n")
        ok, detail = True, ""
        with Spinner(label, enabled=not self.ci):
            try:
                detail = fn() or ""
            except Exception as exc:  # noqa: BLE001
                ok, detail = False, str(exc)
        dt = time.time() - t0
        self.logfile.write(f"{'OK' if ok else 'FAIL'} ({dt:.1f}s) {detail}\n")
        self.logfile.flush()
        mark = c(46, "✔") if ok else c(196, "✘")
        print(f"  {mark} {label}  {c(244, f'({dt:.1f}s)')}" + (f"  {c(244, detail.splitlines()[0])}" if detail and ok else ""))
        if self.ci and os.environ.get("GITHUB_ACTIONS"):
            print("::endgroup::")
        self.results.append({"step": title, "ok": ok, "seconds": round(dt, 2), "detail": detail[:500]})
        if not ok and not optional:
            print(c(196, "\n  BUILD FAILED at: ") + title)
            print(c(244, "\n".join("    " + ln for ln in detail.splitlines()[-25:])))
            self.finish(False)
            sys.exit(1)

    def run(self, cmd: list[str], *, cwd: Path = ROOT, env: dict | None = None, timeout: int = 1800) -> str:
        self.logfile.write("$ " + " ".join(map(str, cmd)) + "\n")
        full_env = dict(os.environ, **(env or {}))
        proc = subprocess.run(cmd, cwd=str(cwd), env=full_env, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8", errors="replace")
        out = (proc.stdout or "") + (proc.stderr or "")
        self.logfile.write(out + "\n")
        if proc.returncode != 0:
            raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(map(str, cmd))}\n{out[-3000:]}")
        return out

    def finish(self, ok: bool):
        self.logfile.flush()


# ---------------------------------------------------------------- steps
def exe_path() -> Path:
    dist = WORK / "dist"
    if IS_WIN:
        return dist / f"{NAME}.exe"
    if IS_MAC:
        return dist / "4R022 AutoClicker.app" / "Contents" / "MacOS" / NAME
    return dist / NAME


def step_environment(p: Pipeline, args) -> str:
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10+ is required")
    missing = []
    for mod in ("PySide6", "pynput"):
        try:
            __import__(mod)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{mod} ({exc.__class__.__name__})")
    if missing and not args.dry_run:
        raise RuntimeError("missing runtime dependencies: " + ", ".join(missing) + "\n  pip install -r requirements-dev.txt")
    if not args.dry_run:
        try:
            import PyInstaller  # noqa: F401
        except ImportError:
            raise RuntimeError("PyInstaller not installed:  pip install -r requirements-dev.txt")
    for f in (MAIN / "main.py", SPEC, MAIN / "autoclicker" / "assets" / "logo.png"):
        if not f.exists():
            raise RuntimeError(f"required file missing: {f}")
    note = " (dry-run: GUI libs not required)" if missing else ""
    return f"python {platform.python_version()} · {PLATFORM}/{ARCH}{note}"


def step_tests(p: Pipeline, args) -> str:
    env = {"QT_QPA_PLATFORM": "offscreen", "PYTHONPATH": str(MAIN)}
    out = p.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"], cwd=MAIN, env=env)
    last = [ln for ln in out.splitlines() if ln.startswith("Ran ")]
    return last[-1] if last else "tests ok"


def step_selftest_source(p: Pipeline, args) -> str:
    flag = "--selftest" if args.dry_run else "--selftest-gui"
    try:
        import PySide6  # noqa: F401
    except Exception:  # noqa: BLE001
        flag = "--selftest"
    out = p.run([sys.executable, str(MAIN / "main.py"), flag], cwd=MAIN, env={"QT_QPA_PLATFORM": "offscreen"})
    passed = [ln.strip() for ln in out.splitlines() if "checks passed" in ln]
    return passed[-1] if passed else "ok"


def step_assets(p: Pipeline, args) -> str:
    a = MAIN / "autoclicker" / "assets"
    need = ["logo.png", "emblem.png", "tray.png", "icon.ico", "icon.icns"]
    miss = [n for n in need if not (a / n).exists()]
    if miss:
        raise RuntimeError("missing assets: " + ", ".join(miss))
    for code in ("tr", "en", "ru"):
        json.loads((MAIN / "autoclicker" / "i18n" / f"{code}.json").read_text(encoding="utf-8"))
    return f"{len(need)} assets + 3 language catalogs valid"


def step_pyinstaller(p: Pipeline, args) -> str:
    if args.dry_run:
        return "skipped (dry-run)"
    if WORK.exists():
        shutil.rmtree(WORK, ignore_errors=True)
    env = {"AC_ONEFILE": "0" if args.onedir else "1"}
    p.run([sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm", "--clean",
           "--distpath", str(WORK / "dist"), "--workpath", str(WORK / "pyi")], env=env)
    exe = exe_path()
    if not exe.exists() and not args.onedir:
        alt = WORK / "dist" / NAME / (NAME + (".exe" if IS_WIN else ""))
        if alt.exists():
            return str(alt)
    if not (exe.exists() or (WORK / "dist" / NAME).exists()):
        raise RuntimeError(f"PyInstaller finished but no output found at {exe}")
    return f"built {exe.name}"


def step_verify(p: Pipeline, args) -> str:
    if args.dry_run:
        return "skipped (dry-run)"
    exe = exe_path()
    if not exe.exists():
        exe = WORK / "dist" / NAME / (NAME + (".exe" if IS_WIN else ""))
    if not exe.exists():
        raise RuntimeError("built executable not found")
    report = WORK / "selftest-report.txt"
    env = {"QT_QPA_PLATFORM": "offscreen", "AUTOCLICKER_SELFTEST_REPORT": str(report)}
    proc = subprocess.run([str(exe), "--selftest-gui"], env=dict(os.environ, **env), capture_output=True,
                          text=True, timeout=300)
    text = report.read_text(encoding="utf-8") if report.exists() else (proc.stdout + proc.stderr)
    p.logfile.write(text + "\n")
    if proc.returncode != 0 or "FAIL" in text:
        raise RuntimeError("built executable failed its self-test:\n" + text[-3000:])
    ver = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=60)
    shutil.copy2(report, OUT / "selftest-report.txt") if report.exists() else None
    return (ver.stdout.strip() or "self-test passed") + " · self-test passed"


def step_package(p: Pipeline, args) -> str:
    if args.dry_run:
        return "skipped (dry-run)"
    base = f"{NAME}-{VERSION_LABEL.replace(' ', '-')}-{PLATFORM}-{ARCH}"
    dist = WORK / "dist"
    OUT.mkdir(parents=True, exist_ok=True)
    extras = [ROOT / "README.md", ROOT / "CHANGELOG.md", ROOT / "LICENSE"]
    if IS_WIN:
        target = OUT / f"{base}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            if (dist / f"{NAME}.exe").exists():
                z.write(dist / f"{NAME}.exe", f"{NAME}.exe")
            else:
                for f in (dist / NAME).rglob("*"):
                    if f.is_file():
                        z.write(f, f"{NAME}/{f.relative_to(dist / NAME)}")
            for e in extras:
                if e.exists():
                    z.write(e, e.name)
    else:
        target = OUT / f"{base}.tar.gz"
        with tarfile.open(target, "w:gz", compresslevel=9) as t:
            if IS_MAC:
                t.add(dist / "4R022 AutoClicker.app", "4R022 AutoClicker.app")
            elif (dist / NAME).is_file():
                t.add(dist / NAME, NAME)
            else:
                t.add(dist / NAME, NAME)
            for e in extras:
                if e.exists():
                    t.add(e, e.name)
    return f"{target.name} ({target.stat().st_size / 1_048_576:.1f} MB)"


def step_checksums(p: Pipeline, args) -> str:
    files = [f for f in OUT.iterdir() if f.is_file() and f.suffix in (".zip", ".gz")]
    if not files:
        return "no packages to hash (dry-run)"
    lines = []
    for f in sorted(files):
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{h}  {f.name}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return f"{len(files)} file(s) hashed (SHA-256)"


def write_report(p: Pipeline, ok: bool, started: float) -> None:
    info = {
        "app": "4R022 AutoClicker", "version": VERSION_LABEL, "semver": __version__,
        "platform": PLATFORM, "arch": ARCH, "python": platform.python_version(),
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "duration_s": round(time.time() - started, 1),
        "success": ok, "steps": p.results,
        "artifacts": sorted(f.name for f in OUT.iterdir() if f.is_file() and f.suffix in (".zip", ".gz", ".txt")),
    }
    (OUT / "build-info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    md = [f"# 4R022 AutoClicker {VERSION_LABEL} — build report", "",
          f"* Platform: **{PLATFORM}/{ARCH}**  ·  Python {platform.python_version()}",
          f"* Result: **{'SUCCESS' if ok else 'FAILED'}**  ·  {info['duration_s']} s", "",
          "| # | Step | Result | Time |", "|---|------|--------|------|"]
    for i, r in enumerate(p.results, 1):
        md.append(f"| {i} | {r['step']} | {'✅' if r['ok'] else '❌'} | {r['seconds']} s |")
    (OUT / "BUILD_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="4R022 AutoClicker build system")
    ap.add_argument("--dry-run", action="store_true", help="validate everything except PyInstaller packaging")
    ap.add_argument("--skip-tests", action="store_true")
    ap.add_argument("--onedir", action="store_true", help="folder build instead of single file")
    ap.add_argument("--ci", action="store_true", help="plain output for CI logs")
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()

    if args.clean:
        for d in (OUT, WORK):
            shutil.rmtree(d, ignore_errors=True)
    banner()
    started = time.time()
    steps = [("Environment check", step_environment)]
    if not args.skip_tests:
        steps.append(("Unit tests", step_tests))
    steps += [("Source self-test", step_selftest_source), ("Assets & languages", step_assets),
              ("PyInstaller build", step_pyinstaller), ("Verify built executable", step_verify),
              ("Package", step_package), ("Checksums", step_checksums)]
    pipe = Pipeline(args.ci, len(steps))
    for title, fn in steps:
        pipe.step(title, lambda fn=fn: fn(pipe, args))
    write_report(pipe, True, started)
    print(c(238, "  " + "─" * 66))
    print(f"  {c(46, bold('BUILD SUCCESSFUL'))}  {c(244, f'{time.time() - started:.1f}s')}  →  {c(131, str(OUT))}")
    for f in sorted(OUT.iterdir()):
        if f.is_file() and f.suffix in (".zip", ".gz"):
            print(f"    {c(196, '▸')} {f.name}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
