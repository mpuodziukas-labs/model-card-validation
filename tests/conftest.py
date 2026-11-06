import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONF = 0.95


def _rc(i, metric, split, ds, k, n, date):
    return {
        "receipt_id": "RC-T-0%d" % i,
        "metric": metric,
        "split": split,
        "dataset_id": ds,
        "k": k,
        "n": n,
        "stated_rate": round(k / n, 2),
        "evaluated_on": date,
    }


def good_system():
    return {
        "system_id": "SYN-T",
        "name": "Test system",
        "label": "SYNTHETIC",
        "intended_use": "Rank synthetic tickets.",
        "out_of_scope": ["Any real decision."],
        "known_limitations": ["Synthetic only."],
        "human_oversight": "A reviewer signs off.",
        "design_rationale": "Plain baseline.",
        "receipts": [
            _rc(1, "accuracy", "dev", "DS-T-DEV", 920, 1000, "2026-10-20"),
            _rc(2, "accuracy", "heldout", "DS-T-HELD", 900, 1000, "2026-10-28"),
        ],
    }


@pytest.fixture
def env(tmp_path):
    manifest = {}
    for ds, split in (("DS-T-DEV", "dev"), ("DS-T-HELD", "heldout")):
        p = tmp_path / (ds + ".csv")
        p.write_text("case_id,correct\nc,%s\n" % ds)
        manifest[ds] = {
            "dataset_id": ds,
            "path": p.name,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "rows": "1",
            "source": "synthetic test file",
            "split": split,
        }
    policy = json.loads((ROOT / "policy.json").read_text())
    return {"manifest": manifest, "policy": policy, "root": tmp_path}
