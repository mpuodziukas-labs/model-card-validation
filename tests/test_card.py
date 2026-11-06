import json
import re
from math import sqrt

from conftest import CONF, ROOT, good_system
from mcv import card, cli

HEX = re.compile(r"\b[0-9a-f]{64}\b")
TAG = re.compile(r"\s*\{(?:src:[^}]*|gap)\}")
NUM = re.compile(r"\d+(?:\.\d+)?")
SECTIONS = [
    "Intended use",
    "Out-of-scope use",
    "Evaluation results",
    "Known limitations",
    "Data provenance",
    "Human oversight",
]


def wilson_ref(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def allowed_numbers(raw, doc):
    nums = set(NUM.findall(raw))
    for s in doc["systems"]:
        for r in s.get("receipts", []):
            lo, hi = wilson_ref(r["k"], r["n"])
            nums |= {"%.4f" % (r["k"] / r["n"]), "%.4f" % lo, "%.4f" % hi}
    return nums


def untraced_numbers(text, allowed):
    body = TAG.sub("", HEX.sub("", text))
    return sorted(set(NUM.findall(body)) - allowed)


def untagged_lines(text):
    bad = []
    for ln in text.splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        if "{src:" not in ln and "{gap}" not in ln:
            bad.append(ln)
    return bad


def build(system, env):
    return card.build_card(system, env["manifest"], CONF)


def test_sections_in_order(env):
    text = build(good_system(), env)
    heads = [ln[3:] for ln in text.splitlines() if ln.startswith("## ")]
    assert heads == SECTIONS


def test_rate_is_recomputed_not_copied(env):
    s = good_system()
    r = s["receipts"][0]
    r["k"], r["n"], r["stated_rate"] = 173, 200, 0.7777
    text = build(s, env)
    assert "173/200 = 0.8650" in text
    assert "0.7777" not in text


def test_wilson_matches_reference(env):
    s = good_system()
    r = s["receipts"][0]
    r["k"], r["n"] = 173, 200
    lo, hi = wilson_ref(173, 200)
    assert "Wilson CI %.4f to %.4f" % (lo, hi) in build(s, env)


def test_empty_limitations_become_gap(env):
    s = good_system()
    s["known_limitations"] = []
    assert "GAP:" in build(s, env)


def test_every_line_is_tagged(env):
    assert untagged_lines(build(good_system(), env)) == []
    assert untagged_lines("plain claim with no tag") != []


def _generated(system, tmp_path):
    out = tmp_path / "o"
    rc = cli.main(
        [
            "generate",
            "--receipts", str(ROOT / "data/receipts.json"),
            "--manifest", str(ROOT / "data/manifest.csv"),
            "--policy", str(ROOT / "policy.json"),
            "--system", system,
            "--out", str(out),
        ]
    )
    assert rc == 0
    return (out / system / "system_card.md").read_text()


def test_every_number_in_card_appears_in_receipts(tmp_path):
    raw = (ROOT / "data/receipts.json").read_text()
    doc = json.loads(raw)
    ok = allowed_numbers(raw, doc)
    assert len(ok) > 20
    for system in ("SYN-A", "SYN-C"):
        text = _generated(system, tmp_path)
        assert NUM.findall(TAG.sub("", HEX.sub("", text)))
        assert untraced_numbers(text, ok) == []
        assert untagged_lines(text) == []
    assert untraced_numbers("rate 0.9999 here", ok) == ["0.9999"]
