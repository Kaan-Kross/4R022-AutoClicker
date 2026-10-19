import json
import re
import unittest
from pathlib import Path

from . import __name__ as _pkg  # noqa: F401

PKG = Path(__file__).resolve().parents[1] / "autoclicker"
CAT = {c: json.loads((PKG / "i18n" / f"{c}.json").read_text(encoding="utf-8")) for c in ("tr", "en", "ru")}

STATIC = re.compile(r"""(?:\bt|tr_|\.t)\(\s*["']([\w.]+[\w])["']""")
CARD = re.compile(r"""(?:Card|Tile)\(\s*["']([\w.]*\w)["']""")
ITEMS = re.compile(r"""\("\w+",\s*"([a-z]+\.\w+)"\)""")
TASKLOG = re.compile(r"""tasklog\.(?:info|warn|error)\(\s*["']([\w.]+)["']""")
PLACEHOLDER = re.compile(r"\{(\w+)\}")


class I18nTests(unittest.TestCase):
    def test_parity(self):
        base = set(CAT["en"])
        for c in ("tr", "ru"):
            self.assertEqual(base - set(CAT[c]), set(), f"{c} missing keys")
            self.assertEqual(set(CAT[c]) - base, set(), f"{c} has extra keys")

    def test_placeholders_match(self):
        for k, en in CAT["en"].items():
            for c in ("tr", "ru"):
                self.assertEqual(set(PLACEHOLDER.findall(en)), set(PLACEHOLDER.findall(CAT[c][k])), f"{c}:{k}")

    def test_no_empty(self):
        for c, d in CAT.items():
            for k, v in d.items():
                self.assertTrue(v.strip(), f"{c}:{k} empty")

    def test_used_keys_exist(self):
        used = set()
        for f in PKG.rglob("*.py"):
            s = f.read_text(encoding="utf-8")
            used |= set(STATIC.findall(s)) | set(CARD.findall(s))
            if "ui" in f.parts:
                used |= set(ITEMS.findall(s))
            used |= {"log." + k for k in TASKLOG.findall(s)}
        used = {k for k in used if not k.endswith(".")}
        missing = sorted(k for k in used if k not in CAT["en"])
        self.assertEqual(missing, [], f"keys used in code but missing from catalogs: {missing}")

    def test_dynamic_families(self):
        need = [f"state.{s}" for s in ("idle", "delay", "running", "paused")]
        need += [f"hk.{a}" for a in ("start", "stop", "pause", "add_target", "kill")]
        need += [f"unit.{u}" for u in ("hours", "minutes", "seconds", "millis")]
        need += [f"reason.{r}" for r in ("user", "finished", "count_reached", "loops_done", "max_runtime",
                                         "failsafe", "killswitch", "error", "app_exit", "auto_shutdown")]
        need += [f"act.{e}" for e in ("app_start", "app_exit", "session_start", "session_end")]
        need += [f"rank.{i}" for i in range(8)]
        need += [f"cps.r.{k}" for k in ("total", "avg_cps", "peak_cps", "score", "consistency", "avg_interval",
                                        "fastest", "slowest", "first_half", "second_half")]
        need += [f"stat.{k}" for k in ("total", "elapsed", "avg", "now", "peak", "errors")]
        need += [f"log.engine.stop_{r}" for r in ("count_reached", "loops_done", "max_runtime", "failsafe",
                                                  "killswitch", "error", "auto_shutdown", "app_exit")]
        for k in need:
            self.assertIn(k, CAT["en"], k)


if __name__ == "__main__":
    unittest.main()
