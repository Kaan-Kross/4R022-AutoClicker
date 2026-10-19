"""Plugin (eklenti) system.

A plugin is a single .py file in the plugins folder exposing:

    PLUGIN_INFO = {"name": "...", "version": "1.0", "author": "...", "description": "..."}
    def register(api): ...          # api.on("start"|"stop"|"pause"|"resume"|"session", callback)

Plugins are DISABLED by default and run with full Python privileges - enable only code you trust.
"""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from typing import Callable

from . import paths
from .logger import TaskLog, get_logger

EVENTS = ("start", "stop", "pause", "resume", "session")


class PluginAPI:
    def __init__(self, pid: str, manager: "PluginManager"):
        self._pid = pid
        self._m = manager

    def on(self, event: str, cb: Callable[[dict], None]) -> None:
        if event not in EVENTS:
            raise ValueError(f"unknown event: {event}")
        self._m._hooks.setdefault(event, []).append((self._pid, cb))

    def log(self, message: str) -> None:
        self._m.tasklog.info("plugin.message", plugin=self._pid, message=str(message))

    @property
    def data_dir(self) -> Path:
        return paths.data_dir()


class PluginManager:
    def __init__(self, tasklog: TaskLog):
        self.tasklog = tasklog
        self.available: dict[str, dict] = {}
        self.loaded: set[str] = set()
        self._hooks: dict[str, list] = {}

    def install_examples(self) -> None:
        src = paths.resource_dir() / "plugins_examples"
        dst = paths.plugins_dir()
        if not src.exists():
            return
        for f in src.glob("*.py"):
            target = dst / f.name
            if not target.exists():
                try:
                    shutil.copy2(f, target)
                except OSError:
                    pass

    def discover(self) -> dict[str, dict]:
        self.available = {}
        for f in sorted(paths.plugins_dir().glob("*.py")):
            if f.name.startswith("_"):
                continue
            info = {"id": f.stem, "name": f.stem, "version": "?", "author": "?", "description": "", "path": str(f)}
            try:
                spec = importlib.util.spec_from_file_location(f"_probe_{f.stem}", f)
                # Read metadata statically to avoid executing disabled plugins
                text = f.read_text(encoding="utf-8")
                import ast
                tree = ast.parse(text)
                for node in tree.body:
                    if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "PLUGIN_INFO" for t in node.targets):
                        data = ast.literal_eval(node.value)
                        if isinstance(data, dict):
                            info.update({k: str(v) for k, v in data.items() if k in ("name", "version", "author", "description")})
                del spec
            except Exception as exc:
                info["description"] = f"(metadata error: {exc})"
            self.available[f.stem] = info
        return self.available

    def load(self, pid: str) -> bool:
        if pid in self.loaded:
            return True
        info = self.available.get(pid)
        if not info:
            return False
        try:
            spec = importlib.util.spec_from_file_location(f"autoclicker_plugin_{pid}", info["path"])
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.register(PluginAPI(pid, self))
            self.loaded.add(pid)
            self.tasklog.info("plugin.loaded", plugin=pid)
            return True
        except Exception as exc:
            self._drop_hooks(pid)
            self.tasklog.error("plugin.error", plugin=pid, error=repr(exc))
            get_logger().exception("plugin %s failed to load", pid)
            return False

    def _drop_hooks(self, pid: str) -> None:
        for ev in list(self._hooks):
            self._hooks[ev] = [h for h in self._hooks[ev] if h[0] != pid]

    def unload(self, pid: str) -> None:
        self._drop_hooks(pid)
        if pid in self.loaded:
            self.loaded.discard(pid)
            self.tasklog.info("plugin.unloaded", plugin=pid)

    def sync(self, enabled: list[str]) -> None:
        self.discover()
        for pid in list(self.loaded):
            if pid not in enabled:
                self.unload(pid)
        for pid in enabled:
            self.load(pid)

    def dispatch(self, event: str, payload: dict) -> None:
        for pid, cb in list(self._hooks.get(event, [])):
            try:
                cb(payload)
            except Exception as exc:
                self.tasklog.error("plugin.error", plugin=pid, error=repr(exc))
