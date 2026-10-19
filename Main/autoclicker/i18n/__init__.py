"""Tiny live-switchable i18n (TR / EN / RU). JSON catalogs live next to this file."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from ..core import paths

LANGUAGE_NAMES = {"tr": "Türkçe", "en": "English", "ru": "Русский"}


class I18n:
    def __init__(self, language: str = "tr", directory: Path | None = None):
        self._dir = directory or (paths.resource_dir() / "i18n")
        self._catalogs: dict[str, dict] = {}
        self._listeners: list[Callable[[], None]] = []
        self.language = "en"
        for code in LANGUAGE_NAMES:
            self._catalogs[code] = self._load(code)
        self.set_language(language, notify=False)

    def _load(self, code: str) -> dict:
        try:
            return json.loads((self._dir / f"{code}.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def set_language(self, code: str, notify: bool = True) -> None:
        self.language = code if code in self._catalogs else "en"
        if notify:
            for cb in list(self._listeners):
                cb()

    def subscribe(self, cb: Callable[[], None]) -> None:
        self._listeners.append(cb)

    def has(self, key: str) -> bool:
        return key in self._catalogs.get(self.language, {}) or key in self._catalogs.get("en", {})

    def t(self, key: str, /, **kw) -> str:
        text = self._catalogs.get(self.language, {}).get(key)
        if text is None:
            text = self._catalogs.get("en", {}).get(key, key)
        if kw:
            try:
                return text.format(**kw)
            except (KeyError, IndexError, ValueError):
                return text
        return text

    def keys(self, code: str = "en") -> set[str]:
        return set(self._catalogs.get(code, {}))
