"""Export statistics to TXT / JSON / CSV and open folders in the OS file manager."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from .. import APP_NAME, __version__

FORMATS = ("txt", "json", "csv")


def _stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def _columns(rows: list[dict]) -> list[str]:
    cols: list[str] = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    return cols


def _flat(v):
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return v


def export_rows(rows: list[dict], fmt: str, directory: str | Path, basename: str = "sessions") -> Path:
    fmt = fmt.lower()
    if fmt not in FORMATS:
        raise ValueError(f"unsupported format: {fmt}")
    out_dir = Path(directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"4R022-{basename}-{_stamp()}.{fmt}"
    if fmt == "json":
        payload = {"app": APP_NAME, "version": __version__,
                   "exported_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "count": len(rows), "data": rows}
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    elif fmt == "csv":
        cols = _columns(rows)
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:   # BOM: Excel-friendly
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({k: _flat(r.get(k, "")) for k in cols})
    else:
        lines = [f"{APP_NAME} {__version__} - {basename}",
                 f"Exported: {time.strftime('%Y-%m-%d %H:%M:%S')}   Records: {len(rows)}",
                 "=" * 64]
        for i, r in enumerate(rows, 1):
            lines.append(f"#{i}")
            for k, v in r.items():
                lines.append(f"  {k:<18}: {_flat(v)}")
            lines.append("-" * 64)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def open_folder(path: str | Path) -> bool:
    p = Path(path)
    try:
        p.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])
        return True
    except Exception:
        return False
