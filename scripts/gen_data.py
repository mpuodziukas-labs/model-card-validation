"""Write the three seeded synthetic systems: datasets, manifest.csv, receipts.json."""
import csv
import hashlib
import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# (rows, positives, correct overall, correct among positives)
SPECS = {
    "A": {"dev": (400, 200, 368, 180), "heldout": (300, 150, 272, 135)},
    "B": {"dev": (400, 200, 368, 180), "heldout": (300, 150, 272, 135)},
    "C": {"dev": (400, 200, 352, 176), "heldout": (300, 140, 260, 101)},
}
SEEDS = {"A": 101, "B": 202, "C": 303}
DATES = {"dev": "2026-10-20", "heldout": "2026-10-28"}
NAMES = {"A": "Ticket router A", "B": "Ticket router B", "C": "Ticket router C"}


def write_dataset(key, split):
    rows, pos, ok_all, ok_pos = SPECS[key][split]
    neg = rows - pos
    ok_neg = ok_all - ok_pos
    cases = [(1, 1)] * ok_pos + [(1, 0)] * (pos - ok_pos) + [(0, 1)] * ok_neg + [(0, 0)] * (neg - ok_neg)
    assert len(cases) == rows
    random.Random(SEEDS[key] + (0 if split == "dev" else 1)).shuffle(cases)
    path = DATA / "datasets" / ("ds_%s_%s.csv" % (key.lower(), split))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["case_id", "is_positive", "correct"])
        for i, (p, c) in enumerate(cases):
            w.writerow(["c%04d" % i, p, c])
    return path


def system(key, manifest_rows):
    recs = []
    for split in ("dev", "heldout"):
        rows, pos, ok_all, ok_pos = SPECS[key][split]
        ds = "DS-%s-%s" % (key, "DEV" if split == "dev" else "HELD")
        path = write_dataset(key, split)
        manifest_rows.append([ds, "datasets/" + path.name, hashlib.sha256(path.read_bytes()).hexdigest(),
                              rows, "synthetic seeded generator, no real records", split])
        for metric, k, n in (("accuracy", ok_all, rows), ("recall", ok_pos, pos)):
            recs.append({"receipt_id": "RC-%s-%02d" % (key, len(recs) + 1), "metric": metric, "split": split,
                         "dataset_id": ds, "k": k, "n": n, "stated_rate": round(k / n, 2),
                         "evaluated_on": DATES[split]})
    s = {
        "system_id": "SYN-" + key,
        "name": NAMES[key],
        "label": "SYNTHETIC",
        "intended_use": "Route synthetic support tickets to one of two queues for human triage.",
        "out_of_scope": [
            "Any decision about a real person.",
            "Use on data that is not synthetic.",
            "Fully automatic routing with no human review.",
        ],
        "known_limitations": [
            "Evaluated on seeded synthetic data only.",
            "Recall is measured on the positive class only.",
        ],
        "human_oversight": "A named reviewer inspects a sample of routed tickets each week and can switch the router off.",
        "design_rationale": "A single threshold classifier was chosen as the simplest baseline that can be audited.",
        "receipts": recs,
    }
    if key == "B":
        recs[0]["evaluated_on"] = "2026-06-01"  # stale
        del recs[3]["dataset_id"]  # missing field
    if key == "C":
        del s["design_rationale"]  # optional field, becomes a GAP
    return s


def main():
    (DATA / "datasets").mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    systems = [system(k, manifest_rows) for k in ("A", "B", "C")]
    doc = {"synthetic": True, "ci_confidence": 0.95, "systems": systems}
    (DATA / "receipts.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    with open(DATA / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["dataset_id", "path", "sha256", "rows", "source", "split"])
        w.writerows(manifest_rows)
    print("wrote %d datasets and %d systems" % (len(manifest_rows), len(systems)))


if __name__ == "__main__":
    main()
