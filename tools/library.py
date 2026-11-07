"""Exercise library lookup: name -> TrainHeroic exercise id.

Cached in ~/.nataly_programming/library.json (refreshed if older than a day or with
refresh=True). Resolution order: tools/aliases.json, exact title (case-insensitive,
preferring Nataly's own exercises), then failure with closest suggestions.
"""
from __future__ import annotations
import difflib, json, re, time
from pathlib import Path

CACHE = Path.home() / ".nataly_programming" / "library.json"
ALIASES = Path(__file__).resolve().parent / "aliases.json"
COACH_USER_ID = 2614315
TH_USER_ID = 555777


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9֐-׿]+", " ", s.lower()).strip()


class Library:
    def __init__(self, th, refresh: bool = False):
        if refresh or not CACHE.exists() or time.time() - CACHE.stat().st_mtime > 86400:
            items = th.library()
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(items, ensure_ascii=False))
        self.items = json.loads(CACHE.read_text())
        self.by_id = {i["id"]: i for i in self.items}
        self.by_name: dict[str, list[dict]] = {}
        for i in self.items:
            self.by_name.setdefault(_norm(i["title"]), []).append(i)
        self.aliases = {_norm(k): v for k, v in json.loads(ALIASES.read_text()).items()} if ALIASES.exists() else {}

    def resolve(self, name: str) -> dict | None:
        key = _norm(name)
        key = _norm(self.aliases.get(key, name))
        cands = self.by_name.get(key)
        if not cands:
            return None
        cands.sort(key=lambda i: (i.get("user_id") != COACH_USER_ID, i.get("user_id") != TH_USER_ID, i["id"]))
        return cands[0]

    def suggest(self, name: str, n: int = 5) -> list[str]:
        keys = difflib.get_close_matches(_norm(name), list(self.by_name), n=n, cutoff=0.5)
        return [self.by_name[k][0]["title"] for k in keys]
