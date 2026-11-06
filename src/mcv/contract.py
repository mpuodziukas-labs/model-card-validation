"""Hand-written data contract. Each check returns a list of (check, where, message)."""
import csv
import datetime as dt
import hashlib

CHECK_IDS = ("schema", "required", "ranges", "k_le_n", "uniqueness", "freshness", "dataset_sha")
MANIFEST_COLUMNS = ["dataset_id", "path", "sha256", "rows", "source", "split"]
NUM = (int, float)
SYSTEM_TYPES = {
    "system_id": str,
    "name": str,
    "label": str,
    "intended_use": str,
    "out_of_scope": list,
    "known_limitations": list,
    "human_oversight": str,
    "receipts": list,
}
RECEIPT_TYPES = {
    "receipt_id": str,
    "metric": str,
    "split": str,
    "dataset_id": str,
    "k": int,
    "n": int,
    "stated_rate": NUM,
    "evaluated_on": str,
}


def _is(v, typ):
    return isinstance(v, typ) and not isinstance(v, bool)


def _num(v):
    return v if _is(v, NUM) else None


def _receipts(s):
    rs = s.get("receipts")
    return [r for r in rs if isinstance(r, dict)] if isinstance(rs, list) else []


def _w(r):
    return str(r.get("receipt_id", "receipt without id"))


def _dups(values):
    return sorted({v for v in values if values.count(v) > 1}, key=str)


def check_schema(s, env):
    sid = str(s.get("system_id", "?"))
    out = []
    for key, typ in SYSTEM_TYPES.items():
        if key in s and not _is(s[key], typ):
            out.append(("schema", sid, "%s has the wrong type" % key))
    if isinstance(s.get("receipts"), list):
        out += [("schema", sid, "a receipt is not an object") for r in s["receipts"] if not isinstance(r, dict)]
    for r in _receipts(s):
        for key, typ in RECEIPT_TYPES.items():
            if key in r and not _is(r[key], typ):
                out.append(("schema", _w(r), "%s has the wrong type" % key))
    return out


def check_required(s, env):
    sid = str(s.get("system_id", "?"))
    out = [("required", sid, "missing %s" % key) for key in SYSTEM_TYPES if key not in s]
    if isinstance(s.get("receipts"), list) and not s["receipts"]:
        out.append(("required", sid, "receipts is empty"))
    for r in _receipts(s):
        out += [("required", _w(r), "missing %s" % key) for key in RECEIPT_TYPES if key not in r]
    return out


def check_ranges(s, env):
    out = []
    for r in _receipts(s):
        n, k, sr = _num(r.get("n")), _num(r.get("k")), _num(r.get("stated_rate"))
        if n is not None and n <= 0:
            out.append(("ranges", _w(r), "n must be greater than 0"))
        if k is not None and k < 0:
            out.append(("ranges", _w(r), "k must not be negative"))
        if sr is not None and not 0 <= sr <= 1:
            out.append(("ranges", _w(r), "stated_rate must be between 0 and 1"))
    return out


def check_k_le_n(s, env):
    out = []
    for r in _receipts(s):
        n, k = _num(r.get("n")), _num(r.get("k"))
        if n is not None and k is not None and k > n:
            out.append(("k_le_n", _w(r), "k is greater than n"))
    return out


def check_uniqueness(s, env):
    recs = _receipts(s)
    out = [("uniqueness", str(i), "duplicate receipt_id") for i in _dups([r["receipt_id"] for r in recs if "receipt_id" in r])]
    pairs = [(r.get("metric"), r.get("split")) for r in recs]
    out += [("uniqueness", "%s/%s" % p, "duplicate metric and split") for p in _dups(pairs)]
    return out


def check_freshness(s, env):
    as_of = dt.date.fromisoformat(env["policy"]["as_of"])
    limit = env["policy"]["stale_days"]
    out = []
    for r in _receipts(s):
        raw = r.get("evaluated_on")
        if not isinstance(raw, str):
            continue
        try:
            age = (as_of - dt.date.fromisoformat(raw)).days
        except ValueError:
            out.append(("freshness", _w(r), "evaluated_on is not an ISO date"))
            continue
        if age < 0:
            out.append(("freshness", _w(r), "evaluated_on is after as_of"))
        elif age > limit:
            out.append(("freshness", _w(r), "STALE: %d days old, limit %d" % (age, limit)))
    return out


def check_dataset_sha(s, env):
    out, seen = [], set()
    for r in _receipts(s):
        ds = r.get("dataset_id")
        if not isinstance(ds, str) or ds in seen:
            continue
        seen.add(ds)
        row = env["manifest"].get(ds)
        if row is None:
            out.append(("dataset_sha", ds, "dataset_id is not in the manifest"))
            continue
        path = env["root"] / row["path"]
        if not path.is_file():
            out.append(("dataset_sha", ds, "dataset file is missing"))
        elif hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            out.append(("dataset_sha", ds, "sha256 does not match the manifest"))
    return out


def validate(system, env):
    violations = []
    for check in (check_schema, check_required, check_ranges, check_k_le_n,
                  check_uniqueness, check_freshness, check_dataset_sha):
        violations += check(system, env)
    return violations


def load_manifest(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header, rows = reader.fieldnames, list(reader)
    if header != MANIFEST_COLUMNS:
        return {}, [("schema", "manifest", "unexpected columns")]
    v = []
    if not rows:
        v.append(("required", "manifest", "no rows"))
    v += [("uniqueness", d, "duplicate dataset_id in manifest") for d in _dups([r["dataset_id"] for r in rows])]
    return {r["dataset_id"]: r for r in rows}, v


def check_document(doc):
    if not isinstance(doc, dict):
        return [("schema", "receipts", "top level is not an object")]
    v = []
    c = _num(doc.get("ci_confidence"))
    if c is None or not 0 < c < 1:
        v.append(("ranges", "ci_confidence", "must be a number strictly between 0 and 1"))
    systems = doc.get("systems")
    if not isinstance(systems, list) or not systems:
        v.append(("schema", "systems", "must be a non-empty list"))
    else:
        ids = [s.get("system_id") for s in systems if isinstance(s, dict)]
        v += [("uniqueness", str(i), "duplicate system_id") for i in _dups(ids)]
    return v
