"""Plant four defects and one clean control; each defect must be caught by its own scenario."""
import hashlib
import json
import tempfile
from pathlib import Path
from unittest import mock

from . import card, contract, verdict

CONF = 0.95
POLICY = Path(__file__).resolve().parents[2] / "policy.json"


def _rc(i, split, ds, k, n, date):
    return {"receipt_id": "RC-S-0%d" % i, "metric": "accuracy", "split": split, "dataset_id": ds,
            "k": k, "n": n, "stated_rate": round(k / n, 2), "evaluated_on": date}


def _system():
    return {
        "system_id": "SYN-S", "name": "Selftest system", "label": "SYNTHETIC",
        "intended_use": "Rank synthetic tickets.", "out_of_scope": ["Any real decision."],
        "known_limitations": ["Synthetic only."], "human_oversight": "A reviewer signs off.",
        "receipts": [_rc(1, "dev", "DS-S-DEV", 920, 1000, "2026-10-20"),
                     _rc(2, "heldout", "DS-S-HELD", 900, 1000, "2026-10-28")],
    }


def _env(tmp):
    manifest = {}
    for ds, split in (("DS-S-DEV", "dev"), ("DS-S-HELD", "heldout")):
        p = tmp / (ds + ".csv")
        p.write_text("case_id,correct\nc,%s\n" % ds)
        manifest[ds] = {"dataset_id": ds, "path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                        "rows": "1", "source": "synthetic selftest file", "split": split}
    return {"manifest": manifest, "policy": json.loads(POLICY.read_text()), "root": tmp}


def _oracle(env):
    """Return the names of scenarios that fail. Empty means every guard fired as expected."""
    fails = []
    s = _system()
    s["receipts"][0]["k"] = s["receipts"][0]["n"] + 1
    if "k_le_n" not in {v[0] for v in contract.validate(s, env)}:
        fails.append("k_le_n")
    s = _system()
    s["receipts"][0]["evaluated_on"] = "2026-01-01"
    if "freshness" not in {v[0] for v in contract.validate(s, env)}:
        fails.append("freshness")
    s = _system()
    s["receipts"][0].update(k=173, n=200, stated_rate=0.7777)
    text = card.build_card(s, env["manifest"], CONF)
    if "173/200 = 0.8650" not in text or "0.7777" in text:
        fails.append("recompute")
    s = _system()
    s["receipts"][1]["k"] = 500
    if verdict.decide(s["receipts"], env["policy"], CONF)[0] != "REJECT":
        fails.append("floor")
    return fails


MUTANTS = [
    ("k_le_n check dropped", "k_le_n", contract, "check_k_le_n", lambda s, e: []),
    ("freshness check skipped", "freshness", contract, "check_freshness", lambda s, e: []),
    ("stated rate copied", "recompute", card, "rate_of", lambda r: r["stated_rate"]),
    ("below-floor ignored by verdict", "floor", verdict, "find_below_floor", lambda r, p, c: []),
]


def run():
    lines, ok = [], 0
    with tempfile.TemporaryDirectory() as t:
        env = _env(Path(t))
        control = _oracle(env)
        lines.append("control clean: %s" % ("ok" if not control else "FAIL " + ",".join(control)))
        ok += not control
        for label, expect, mod, attr, repl in MUTANTS:
            with mock.patch.object(mod, attr, repl):
                fails = _oracle(env)
            caught = expect in fails
            lines.append("defect %s: %s" % (label, "caught" if caught else "MISSED"))
            ok += caught
    return ok, len(MUTANTS) + 1, lines
