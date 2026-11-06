import re

from conftest import ROOT

SKIP_DIRS = {"build", ".pytest_cache", "__pycache__", ".git"}
IPV4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
# Brand names are stored reversed so this file does not contain them.
BRANDS = ["edualc", "cipohtna", "ianepo", "tpg", "inimeg", "amall", "lartsim", "newq", "keestpeed"]


def _files():
    out = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS):
            out.append(p)
    return out


def test_no_banned_strings_anywhere():
    files = _files()
    assert len(files) > 15
    words = [chr(0x2014), "/Us" + "ers/", "lever" + "age"] + [b[::-1] for b in BRANDS]
    hits = []
    for p in files:
        text = p.read_text(encoding="utf-8")
        low = text.lower()
        hits += [(p.name, w) for w in words if w.lower() in low]
        hits += [(p.name, m) for m in IPV4.findall(text)]
    assert hits == []
